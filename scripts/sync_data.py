"""從正式 JSON 同步作品與個人資料的本機預覽備援。"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]


class DataError(ValueError):
    """資料檔無法讀取或格式不正確。"""


@dataclass(frozen=True)
class Dataset:
    name: str
    variable: str
    root_type: type
    shape: str

    @property
    def source(self) -> Path:
        return Path("data") / f"{self.name}.json"

    @property
    def fallback(self) -> Path:
        return Path("data") / f"{self.name}-data.js"


PROJECTS = Dataset("projects", "PROJECTS_FALLBACK", list, "陣列")
PROFILE = Dataset("profile", "PROFILE_FALLBACK", dict, "物件")
DATASETS = (PROJECTS, PROFILE)


def read_text(root: Path, filename: Path) -> str:
    try:
        return (root / filename).read_text(encoding="utf-8")
    except FileNotFoundError as error:
        raise DataError(f"{filename.as_posix()}：檔案不存在") from error
    except UnicodeError as error:
        raise DataError(f"{filename.as_posix()}：必須使用 UTF-8 編碼") from error
    except OSError as error:
        raise DataError(f"{filename.as_posix()}：無法讀取（{error.strerror}）") from error


def parse_json(text: str, label: str):
    def unique_object(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"重複的 JSON 欄位 {key!r}")
            result[key] = value
        return result

    def reject_constant(value):
        raise ValueError(f"{value} 不是有效的 JSON 數值")

    try:
        return json.loads(text, object_pairs_hook=unique_object, parse_constant=reject_constant)
    except json.JSONDecodeError as error:
        raise DataError(f"{label}：JSON 格式錯誤（第 {error.lineno} 行，第 {error.colno} 欄）") from error
    except ValueError as error:
        raise DataError(f"{label}：{error}") from error


def read_source(root: Path, dataset: Dataset) -> tuple[str, object]:
    text = read_text(root, dataset.source)
    data = parse_json(text, dataset.source.as_posix())
    if not isinstance(data, dataset.root_type):
        raise DataError(f"{dataset.source.as_posix()}：JSON 根層必須是{dataset.shape}")
    return text.rstrip(), data


def fallback_bytes(dataset: Dataset, source: str) -> bytes:
    comment = f"/* 自 {dataset.source.as_posix()} 產生：修改 JSON 後請同步此檔 */"
    return f"{comment}\nwindow.{dataset.variable} = {source};\n".encode("utf-8")


def synchronize(root: Path = ROOT, *, check: bool = False) -> list[Path]:
    data_dir = root / "data"
    if not data_dir.resolve().is_relative_to(root.resolve()):
        raise DataError("data/：目錄必須位於專案根目錄之內")

    # 兩份來源都解析後，才準備任何待寫入內容。
    expected = {
        dataset.fallback: fallback_bytes(dataset, read_source(root, dataset)[0])
        for dataset in DATASETS
    }

    changes = {}
    for relative, contents in expected.items():
        target = root / relative
        if target.is_symlink():
            raise DataError(f"{relative.as_posix()}：備援檔必須是一般檔案")
        try:
            previous = target.read_bytes()
        except FileNotFoundError:
            previous = None
        # Git 在 Windows 工作樹可能使用 CRLF，這不代表備援資料過期。
        if previous is not None and previous.replace(b"\r\n", b"\n") == contents:
            continue
        changes[relative] = (previous, contents)

    if check or not changes:
        return list(changes)

    # 先在同一檔案系統備妥完整檔案，再逐一進行原子替換。
    with TemporaryDirectory(prefix=".sync-data-", dir=data_dir) as staging:
        stage = Path(staging)
        for relative, (previous, contents) in changes.items():
            (stage / relative.name).write_bytes(contents)
            if previous is not None:
                (stage / (relative.name + ".previous")).write_bytes(previous)

        replaced = []
        try:
            for relative in changes:
                (stage / relative.name).replace(root / relative)
                replaced.append(relative)
        except OSError as error:
            restore_errors = []
            for published in reversed(replaced):
                try:
                    if changes[published][0] is None:
                        (root / published).unlink()
                    else:
                        (stage / (published.name + ".previous")).replace(root / published)
                except OSError as restore_error:
                    restore_errors.append(f"{published.as_posix()}（{restore_error.strerror}）")
            message = f"{relative.as_posix()}：備援寫入失敗（{error.strerror or error}）"
            if restore_errors:
                message += "。無法還原 " + "、".join(restore_errors) + "，請排除檔案問題後重跑同步"
            raise DataError(message) from error
    return list(changes)


def main(argv=None, *, root: Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="唯讀檢查備援是否已同步")
    args = parser.parse_args(argv)

    try:
        changed = synchronize(root, check=args.check)
    except (DataError, OSError) as error:
        print(f"[ERROR] {error}")
        return 1

    for dataset in DATASETS:
        path = dataset.fallback
        if path not in changed:
            print(f"[PASS] {path.as_posix()} 已同步")
        elif args.check:
            print(f"[ERROR] {path.as_posix()} 需要重新產生")
        else:
            print(f"[SYNC] {path.as_posix()} 已從 {dataset.source.as_posix()} 產生")

    if args.check and changed:
        print("同步檢查未通過。請執行 python scripts/sync_data.py")
        return 1
    print("備援同步檢查通過。" if args.check else "兩份備援資料均已同步。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
