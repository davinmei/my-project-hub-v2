"""離線驗證網站資料及備援，回報檔案、作品與欄位位置。"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path, PurePosixPath
import re
from urllib.parse import urlsplit

if __package__:
    from . import sync_data
else:
    import sync_data


CATEGORIES = ("Web App", "AI / LLM", "RAG", "AI Agent", "LLM Wiki", "Other")
PROJECT_TYPES = ("課程作業", "個人專案", "產學合作", "研究專案")
TYPE_LABELS = {str: "文字", list: "陣列", dict: "物件", bool: "布林值"}
PROJECT_FIELDS = {
    "id": str,
    "title": str,
    "category": str,
    "summary": str,
    "description": str,
    "motivation": str,
    "features": list,
    "technologies": list,
    "results": str,
    "lessonsLearned": str,
    "image": str,
    "imageAlt": str,
    "demoUrl": str,
    "githubUrl": str,
    "status": str,
    "featured": bool,
}
PROFILE_FIELDS = {
    "intro": dict,
    "education": list,
    "skills": dict,
    "interests": list,
    "links": list,
    "site": dict,
}
MEDIA_FIELDS = {"src": str, "alt": str}
LINK_FIELDS = {"label": str, "url": str}


@dataclass
class ValidationReport:
    passed: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    project_count: int | None = None

    def error(self, path: str, message: str) -> None:
        self.errors.append(f"{path}：{message}")


def check_fields(record, fields, path, report, *, allow_empty=()) -> bool:
    if not isinstance(record, dict):
        report.error(path, "必須是物件")
        return False
    for key, expected in fields.items():
        location = f"{path}.{key}"
        if key not in record:
            report.error(location, "缺少必填欄位")
        elif not isinstance(record[key], expected):
            report.error(location, f"必須是{TYPE_LABELS[expected]}")
        elif expected is str and key not in allow_empty and not record[key].strip():
            report.error(location, "文字不可空白")
    return True


def check_text_items(items, path, report) -> None:
    if isinstance(items, list):
        for index, item in enumerate(items):
            if not isinstance(item, str) or not item.strip():
                report.error(f"{path}[{index}]", "必須是非空白文字")


def checked_records(items, fields, path, report):
    records = []
    if isinstance(items, list):
        for index, item in enumerate(items):
            location = f"{path}[{index}]"
            if check_fields(item, fields, location, report):
                records.append((item, location))
    return records


def valid_url(value: str) -> bool:
    if re.search(r"[\s\x00-\x1f\x7f\\]|%(?![0-9a-fA-F]{2})", value):
        return False
    try:
        url = urlsplit(value)
        if url.scheme not in ("http", "https") or url.username is not None:
            return False
        authority = re.fullmatch(r"(?:\[[^\[\]]+\]|[^:\[\]]+)(?::(?P<port>[0-9]+))?", url.netloc)
        if not url.hostname or authority is None:
            return False
        port = authority["port"]
        if port is not None and int(port) > 65535:
            return False
        if ":" in url.hostname:
            return True
        host = url.hostname.encode("idna").decode("ascii").removesuffix(".")
    except (ValueError, UnicodeError):
        return False
    return all(re.fullmatch(r"[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?", part) for part in host.split("."))


def check_url(value, path, report, *, allow_empty=False) -> None:
    if not isinstance(value, str):
        return  # 型態錯誤已由 check_fields 回報。
    if value == "" and allow_empty:
        return
    if not value.strip():
        if allow_empty:
            report.error(path, "沒有連結時請使用空字串")
        return  # 必填連結的空白已由 check_fields 回報。
    if not valid_url(value):
        report.error(path, "必須使用完整的 HTTP 或 HTTPS 網址，且不能含帳密")
    elif value.lower().startswith("http:"):
        report.warnings.append(f"{path}：HTTP 格式有效，目前網站僅顯示 HTTPS 連結")


def check_links(links, path, report) -> None:
    for link, location in checked_records(links, LINK_FIELDS, path, report):
        check_url(link.get("url"), f"{location}.url", report)


def check_image(value, path, root, report) -> None:
    if not isinstance(value, str) or not value.strip():
        return  # 型態與空白已由 check_fields 回報。
    relative = PurePosixPath(value)
    if (value != value.strip() or value.endswith("/") or relative.is_absolute() or ".." in relative.parts
            or re.search(r"[\x00-\x1f\x7f\\:?#%]", value)):
        report.error(path, "必須使用專案內的相對圖片路徑，使用 / 並省略查詢、片段及編碼")
        return

    target = root / relative
    try:
        resolved = target.resolve()
        if not resolved.is_relative_to(root):
            report.error(path, "圖片路徑不能指向專案根目錄外")
            return
        if not target.is_file():
            report.error(path, f"圖片檔案不存在（{value}）")
            return
        parent = root
        for part in relative.parts:
            if not any(item.name == part for item in parent.iterdir()):
                report.error(path, f"圖片路徑的大小寫必須與檔案一致（{value}）")
                return
            parent /= part
    except (OSError, RuntimeError) as error:
        report.error(path, f"無法檢查圖片路徑（{error}）")


def check_media(media, path, root, report) -> None:
    if check_fields(media, MEDIA_FIELDS, path, report):
        check_image(media.get("src"), f"{path}.src", root, report)


def positive_integer(value) -> bool:
    return type(value) in (int, float) and value > 0 and (
        isinstance(value, int) or value.is_integer()
    )


def valid_date(value) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def validate_projects(projects, root, report) -> None:
    source = sync_data.PROJECTS.source.as_posix()
    seen_ids = {}
    for index, project in enumerate(projects):
        entry = f"{source}[{index}]"
        identifier = project.get("id") if isinstance(project, dict) else None
        path = f"{entry}（{identifier}）" if isinstance(identifier, str) and identifier.strip() else entry
        if not check_fields(project, PROJECT_FIELDS, path, report, allow_empty=("githubUrl", "demoUrl")):
            continue

        if isinstance(identifier, str) and identifier.strip():
            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", identifier):
                report.error(f"{path}.id", "只接受小寫英數及以連字號分隔的字串")
            if identifier in seen_ids:
                report.error(f"{path}.id", f"作品 ID 重複，已用於第 {seen_ids[identifier] + 1} 筆")
            else:
                seen_ids[identifier] = index

        for key, options in (
            ("category", CATEGORIES),
            ("status", ("completed", "in-progress")),
            ("projectType", PROJECT_TYPES),
            ("imageType", ("screenshot", "placeholder")),
        ):
            if key in project and project[key] not in options:
                report.error(f"{path}.{key}", "允許值為 " + "、".join(options))
        for key in ("addedOrder", "courseWeek"):
            if key in project and not positive_integer(project[key]):
                report.error(f"{path}.{key}", "必須是正整數")
        if "projectDate" in project and not valid_date(project["projectDate"]):
            report.error(f"{path}.projectDate", "必須是有效日期（YYYY-MM-DD）")

        for key in ("features", "technologies"):
            check_text_items(project.get(key), f"{path}.{key}", report)
        check_image(project.get("image"), f"{path}.image", root, report)
        for key in ("demoUrl", "githubUrl"):
            check_url(project.get(key), f"{path}.{key}", report, allow_empty=True)

        if "systemDiagram" in project:
            check_media(project["systemDiagram"], f"{path}.systemDiagram", root, report)
        for key in ("screenshots", "links"):
            if key in project and not isinstance(project[key], list):
                report.error(f"{path}.{key}", "必須是陣列")
        for image, location in checked_records(project.get("screenshots"), MEDIA_FIELDS, f"{path}.screenshots", report):
            check_image(image.get("src"), f"{location}.src", root, report)
        check_links(project.get("links"), f"{path}.links", report)


def validate_profile(profile, report) -> None:
    path = sync_data.PROFILE.source.as_posix()
    check_fields(profile, PROFILE_FIELDS, path, report)
    if isinstance(profile.get("intro"), dict):
        check_fields(profile["intro"], {"role": str, "roleEn": str, "description": str}, f"{path}.intro", report)
    for key, fields in (
        ("education", {"school": str, "program": str, "degree": str}),
        ("interests", {"title": str, "description": str}),
    ):
        checked_records(profile.get(key), fields, f"{path}.{key}", report)

    skills = profile.get("skills")
    if isinstance(skills, dict):
        check_fields(skills, {"note": str, "groups": list}, f"{path}.skills", report)
        for group, location in checked_records(
            skills.get("groups"), {"title": str, "technologies": list}, f"{path}.skills.groups", report
        ):
            check_text_items(group.get("technologies"), f"{location}.technologies", report)
    site = profile.get("site")
    if isinstance(site, dict):
        check_fields(site, {"paragraphs": list}, f"{path}.site", report)
        check_text_items(site.get("paragraphs"), f"{path}.site.paragraphs", report)
    check_links(profile.get("links"), f"{path}.links", report)


def read_fallback(root: Path, dataset: sync_data.Dataset):
    label = dataset.fallback.as_posix()
    script = sync_data.read_text(root, dataset.fallback)
    assignment = re.fullmatch(
        rf"\s*(?:/\*.*?\*/\s*)?window\.{re.escape(dataset.variable)}\s*=\s*(.+?)\s*;\s*",
        script, flags=re.DOTALL
    )
    if assignment is None:
        raise sync_data.DataError(f"{label}：必須使用 window.{dataset.variable} = <JSON>;")
    return sync_data.parse_json(assignment.group(1), label)


def json_equal(source, fallback) -> bool:
    # Python 的 True == 1，但 JSON 布林值與數字是不同的資料型態。
    if isinstance(source, bool) or isinstance(fallback, bool):
        return source is fallback
    if isinstance(source, dict) and isinstance(fallback, dict):
        return source.keys() == fallback.keys() and all(json_equal(source[key], fallback[key]) for key in source)
    if isinstance(source, list) and isinstance(fallback, list):
        return len(source) == len(fallback) and all(json_equal(a, b) for a, b in zip(source, fallback))
    return source == fallback


def validate(root: Path = sync_data.ROOT) -> ValidationReport:
    root = root.resolve()
    report = ValidationReport()
    for dataset in sync_data.DATASETS:
        try:
            _, data = sync_data.read_source(root, dataset)
        except sync_data.DataError as error:
            report.errors.append(str(error))
            continue
        report.passed.append(f"{dataset.source.as_posix()} 的 UTF-8、JSON 格式與根層型態")

        errors_before = len(report.errors)
        if dataset == sync_data.PROJECTS:
            report.project_count = len(data)
            validate_projects(data, root, report)
            checks = "作品欄位、ID、分類、排序、圖片及網址格式"
        else:
            validate_profile(data, report)
            checks = "個人資料欄位、各區塊型態及公開網址格式"
        if len(report.errors) == errors_before:
            report.passed.append(checks)

        try:
            fallback = read_fallback(root, dataset)
        except sync_data.DataError as error:
            report.errors.append(str(error))
        else:
            label = dataset.fallback.as_posix()
            if json_equal(data, fallback):
                report.passed.append(f"{label} 內容與正式 JSON 一致")
            else:
                report.error(label, f"與 {dataset.source.as_posix()} 不一致，請重新產生備援")

    return report


def main(argv=None, *, root: Path = sync_data.ROOT) -> int:
    argparse.ArgumentParser(description=__doc__).parse_args(argv)
    report = validate(root)
    for label, messages in (("PASS", report.passed), ("WARN", report.warnings), ("ERROR", report.errors)):
        for message in messages:
            print(f"[{label}] {message}")
    count = report.project_count if report.project_count is not None else "無法取得"
    print(f"作品數量：{count}｜警告：{len(report.warnings)}｜錯誤：{len(report.errors)}")
    print("資料驗證未通過。" if report.errors else "資料驗證通過。")
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
