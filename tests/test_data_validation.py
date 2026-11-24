"""驗證資料工具的正常與失敗路徑。所有個案使用隔離的暫存資料。"""

import contextlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

from scripts import sync_data, validate_data


class DataToolsTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory(prefix="my-project-hub-data-tests-")
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        (self.root / "data").mkdir()
        images = self.root / "assets/images"
        images.mkdir(parents=True)
        (images / "cover.svg").write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1 1"><rect width="1" height="1"/></svg>',
            encoding="utf-8"
        )
        self.project = {
            "id": "sample-project",
            "title": "實作測試",
            "category": "LLM Wiki",
            "summary": "作品簡介",
            "description": "作品說明",
            "motivation": "開發動機",
            "features": ["首頁"],
            "technologies": ["Python", "HTML"],
            "results": "開發成果",
            "lessonsLearned": "待補充",
            "image": "assets/images/cover.svg",
            "imageAlt": "測試封面",
            "demoUrl": "",
            "githubUrl": "https://example.test/project",
            "status": "completed",
            "featured": True,
        }
        self.profile = {
            "intro": {"role": "測試身分", "roleEn": "Test profile", "description": "介紹"},
            "education": [{"school": "測試學校", "program": "系所", "degree": "學位"}],
            "skills": {"note": "技術領域", "groups": [{"title": "網頁", "technologies": ["HTML"]}]},
            "interests": [{"title": "興趣", "description": "說明"}],
            "links": [{"label": "公開網站", "url": "https://example.test/profile"}],
            "site": {"paragraphs": ["網站說明"]},
        }
        self.write_source(sync_data.PROJECTS, [self.project])
        self.write_source(sync_data.PROFILE, self.profile)
        sync_data.synchronize(self.root)

    def write_source(self, spec, value):
        (self.root / spec.source).write_bytes(
            (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
        )

    def backup_bytes(self):
        return {spec.fallback: (self.root / spec.fallback).read_bytes() for spec in sync_data.DATASETS}

    def assert_field_error(self, fragment):
        report = validate_data.validate(self.root)
        self.assertTrue(any(fragment in item for item in report.errors), report.errors)

    def run_cli(self, entry, *args):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            code = entry(list(args), root=self.root)
        return code, output.getvalue()

    def test_valid_projects_pass_with_media_and_links(self):
        media = {"src": "assets/images/cover.svg", "alt": "測試畫面"}
        self.project.update(
            systemDiagram=media, screenshots=[media], projectType="課程作業",
            links=[{"label": "線上展示", "url": "https://example.test/a#overview"}],
            addedOrder=1, imageType="screenshot", courseWeek=9, projectDate="2024-02-29",
        )
        self.write_source(sync_data.PROJECTS, [self.project])
        sync_data.synchronize(self.root)
        report = validate_data.validate(self.root)
        self.assertEqual(report.project_count, 1)
        self.assertEqual(report.errors, [])
        self.assertEqual(report.warnings, [])

    def test_valid_profile_passes(self):
        report = validate_data.validate(self.root)
        self.assertIn("個人資料欄位、各區塊型態及公開網址格式", report.passed)
        self.assertEqual(report.errors, [])

    def test_legacy_project_allows_absent_optional_fields(self):
        self.assertFalse(any(key in self.project for key in ("addedOrder", "projectType", "projectDate")))
        self.assertEqual(validate_data.validate(self.root).errors, [])

    def test_json_syntax_reports_file_line_and_column(self):
        for spec in sync_data.DATASETS:
            with self.subTest(file=spec.source):
                source = self.root / spec.source
                correct = source.read_bytes()
                source.write_bytes(b"{\n")
                self.assert_field_error(f"{spec.source.as_posix()}：JSON 格式錯誤（第 2 行，第 1 欄）")
                source.write_bytes(correct)

    def test_source_rejects_non_json_trailing_whitespace(self):
        source = self.root / sync_data.PROFILE.source
        source.write_bytes(source.read_bytes() + "\u00a0".encode("utf-8"))
        self.assert_field_error("data/profile.json：JSON 格式錯誤")

    def test_missing_source_is_reported(self):
        (self.root / sync_data.PROJECTS.source).unlink()
        self.assert_field_error("data/projects.json：檔案不存在")

    def test_invalid_root_shapes_are_reported(self):
        self.write_source(sync_data.PROJECTS, {})
        self.write_source(sync_data.PROFILE, [])
        self.assert_field_error("data/projects.json：JSON 根層必須是陣列")
        self.assert_field_error("data/profile.json：JSON 根層必須是物件")

    def test_duplicate_json_fields_and_nonstandard_constants_are_rejected(self):
        source = self.root / sync_data.PROFILE.source
        for contents, message in [
            (b'{"intro":{},"intro":{}}', "重複的 JSON 欄位"),
            (b'{"value":NaN}', "不是有效的 JSON 數值"),
        ]:
            with self.subTest(contents=contents):
                source.write_bytes(contents)
                self.assert_field_error(message)

    def test_missing_required_fields_are_reported(self):
        del self.project["title"]
        del self.profile["intro"]["roleEn"]
        self.write_source(sync_data.PROJECTS, [self.project])
        self.write_source(sync_data.PROFILE, self.profile)
        self.assert_field_error("（sample-project）.title：缺少必填欄位")
        self.assert_field_error("data/profile.json.intro.roleEn：缺少必填欄位")

    def test_duplicate_id_is_reported(self):
        self.write_source(sync_data.PROJECTS, [self.project, self.project])
        self.assert_field_error("[1]（sample-project）.id：作品 ID 重複")

    def test_blank_or_invalid_id_is_reported(self):
        for value, message in [("  ", ".id：文字不可空白"), ("Wrong/ID", ".id：只接受小寫英數")]:
            with self.subTest(value=value):
                self.write_source(sync_data.PROJECTS, [dict(self.project, id=value)])
                self.assert_field_error(message)

    def test_field_types_and_empty_technology_tags_are_reported(self):
        self.project.update(featured=1, features={}, technologies=["Python", "", 3])
        self.profile["skills"]["groups"] = {}
        self.write_source(sync_data.PROJECTS, [self.project])
        self.write_source(sync_data.PROFILE, self.profile)
        for expected in (".featured：必須是布林值", ".features：必須是陣列",
                         ".technologies[1]：必須是非空白文字", ".technologies[2]：必須是非空白文字",
                         "profile.json.skills.groups：必須是陣列"):
            self.assert_field_error(expected)

    def test_invalid_project_type_category_or_status_is_reported(self):
        self.project.update(projectType="未定義類別", category="任意分類", status="pending")
        self.write_source(sync_data.PROJECTS, [self.project])
        for key in ("projectType", "category", "status"):
            self.assert_field_error(f".{key}：允許值")

    def test_invalid_order_week_and_date_are_reported(self):
        self.project.update(addedOrder=0, courseWeek=True, projectDate="2026-02-30")
        self.write_source(sync_data.PROJECTS, [self.project])
        self.assert_field_error(".addedOrder：必須是正整數")
        self.assert_field_error(".courseWeek：必須是正整數")
        self.assert_field_error(".projectDate：必須是有效日期")

    def test_added_order_ties_follow_existing_frontend_rule(self):
        first = dict(self.project, addedOrder=2)
        second = dict(self.project, id="second-project")
        third = dict(self.project, id="third-project", addedOrder=2)
        self.write_source(sync_data.PROJECTS, [first, second, third])
        sync_data.synchronize(self.root)
        self.assertEqual(validate_data.validate(self.root).errors, [])

    def test_missing_cover_diagram_and_screenshot_files_are_reported(self):
        media = {"src": "assets/images/missing.svg", "alt": "測試圖片"}
        self.project.update(image=media["src"], systemDiagram=media, screenshots=[media])
        self.write_source(sync_data.PROJECTS, [self.project])
        for path in ("image", "systemDiagram.src", "screenshots[0].src"):
            self.assert_field_error(f".{path}：圖片檔案不存在")

    def test_unsafe_image_paths_are_rejected(self):
        for value in ("../outside.svg", "/assets/images/cover.svg", "C:/cover.svg",
                      "assets\\images\\cover.svg", "https://example.test/image.svg",
                      "assets/images/%2e%2e/out.svg", "assets/images/cover.svg?foo=1",
                      "assets/images/cover.svg/"):
            with self.subTest(value=value):
                self.write_source(sync_data.PROJECTS, [dict(self.project, image=value)])
                self.assert_field_error(".image：必須使用專案內的相對圖片路徑")

    def test_image_alt_is_required_for_all_image_shapes(self):
        self.project.update(
            imageAlt="  ",
            systemDiagram={"src": self.project["image"]},
            screenshots=[{"src": self.project["image"], "alt": False}],
        )
        self.write_source(sync_data.PROJECTS, [self.project])
        for expected in (".imageAlt：文字不可空白", ".systemDiagram.alt：缺少必填欄位",
                         ".screenshots[0].alt：必須是文字"):
            self.assert_field_error(expected)

    def test_invalid_link_formats_are_reported_for_both_sources(self):
        self.project.update(githubUrl="javascript:alert(1)", demoUrl="https://",
                            links=[{"label": "網站", "url": "https://example.test:70000/"}])
        self.profile["links"][0]["url"] = "https://user:pass@example.test/"
        self.write_source(sync_data.PROJECTS, [self.project])
        self.write_source(sync_data.PROFILE, self.profile)
        for expected in (".githubUrl：必須使用完整", ".demoUrl：必須使用完整",
                         "）.links[0].url：必須使用完整", "profile.json.links[0].url：必須使用完整"):
            self.assert_field_error(expected)

    def test_http_link_is_a_warning_without_network_access(self):
        self.project["demoUrl"] = "http://example.test/"
        self.write_source(sync_data.PROJECTS, [self.project])
        sync_data.synchronize(self.root)
        report = validate_data.validate(self.root)
        self.assertEqual(report.errors, [])
        self.assertEqual(len(report.warnings), 1)
        self.assertIn(".demoUrl：HTTP 格式有效", report.warnings[0])
        self.assertEqual(self.run_cli(validate_data.main)[0], 0)

    def test_invalid_nested_profile_blocks_are_reported(self):
        self.profile.update(education=[[]], interests=[{"title": "缺少說明"}],
                            site={"paragraphs": [123]})
        self.write_source(sync_data.PROFILE, self.profile)
        for expected in ("education[0]：必須是物件", "interests[0].description：缺少必填欄位",
                         "site.paragraphs[0]：必須是非空白文字"):
            self.assert_field_error(expected)

    def test_stale_project_and_profile_backups_are_reported(self):
        self.project["title"] = "新版作品"
        self.profile["intro"]["role"] = "新版簡介"
        self.write_source(sync_data.PROJECTS, [self.project])
        self.write_source(sync_data.PROFILE, self.profile)
        passed_backups = self.backup_bytes()
        self.assert_field_error("projects-data.js：與 data/projects.json 不一致")
        self.assert_field_error("profile-data.js：與 data/profile.json 不一致")
        code, _ = self.run_cli(validate_data.main)
        self.assertEqual(code, 1)
        self.assertEqual(self.backup_bytes(), passed_backups)

    def test_boolean_and_number_in_backup_are_distinct(self):
        target = self.root / sync_data.PROJECTS.fallback
        wrong = [dict(self.project, featured=1)]
        target.write_bytes(sync_data.fallback_bytes(sync_data.PROJECTS, json.dumps(wrong)))
        self.assert_field_error("projects-data.js：與 data/projects.json 不一致")

    def test_backup_parser_rejects_javascript_expression_and_trailing_code(self):
        target = self.root / sync_data.PROJECTS.fallback
        for payload in [
            b"window.PROJECTS_FALLBACK = Array();",
            target.read_bytes() + b"globalThis.unexpected = true;",
        ]:
            with self.subTest(payload=payload):
                target.write_bytes(payload)
                self.assert_field_error("data/projects-data.js：JSON 格式錯誤")

    def test_missing_backup_is_reported(self):
        (self.root / sync_data.PROFILE.fallback).unlink()
        self.assert_field_error("data/profile-data.js：檔案不存在")

    def test_check_mode_reports_drift_and_only_reads(self):
        target = self.root / sync_data.PROFILE.fallback
        target.write_bytes(target.read_bytes() + b"\n")
        original = target.read_bytes()
        self.assertEqual(validate_data.validate(self.root).errors, [])
        code, output = self.run_cli(sync_data.main, "--check")
        self.assertEqual(code, 1)
        self.assertIn("data/profile-data.js 需要重新產生", output)
        self.assertEqual(target.read_bytes(), original)

    def test_windows_crlf_checkout_is_already_synchronized(self):
        for spec in sync_data.DATASETS:
            target = self.root / spec.fallback
            target.write_bytes(target.read_bytes().replace(b"\n", b"\r\n"))
        before = self.backup_bytes()
        self.assertEqual(self.run_cli(sync_data.main, "--check")[0], 0)
        self.assertEqual(sync_data.synchronize(self.root), [])
        self.assertEqual(validate_data.validate(self.root).errors, [])
        self.assertEqual(self.backup_bytes(), before)

    def test_synchronize_updates_both_backups_without_editing_sources(self):
        self.project["title"] = "新作品名稱"
        self.profile["intro"]["role"] = "新身分"
        self.write_source(sync_data.PROJECTS, [self.project])
        self.write_source(sync_data.PROFILE, self.profile)
        sources = {spec.source: (self.root / spec.source).read_bytes() for spec in sync_data.DATASETS}
        self.assertEqual(sync_data.synchronize(self.root), [spec.fallback for spec in sync_data.DATASETS])
        self.assertEqual(validate_data.validate(self.root).errors, [])
        self.assertIn("新身分".encode(), (self.root / sync_data.PROFILE.fallback).read_bytes())
        self.assertEqual({path: (self.root / path).read_bytes() for path in sources}, sources)

    def test_synchronize_repeatedly_is_stable(self):
        before = self.backup_bytes()
        modified = {path: (self.root / path).stat().st_mtime_ns for path in before}
        self.assertEqual(sync_data.synchronize(self.root), [])
        self.assertEqual(sync_data.synchronize(self.root), [])
        self.assertEqual(self.run_cli(sync_data.main, "--check")[0], 0)
        self.assertEqual(self.backup_bytes(), before)
        self.assertEqual({path: (self.root / path).stat().st_mtime_ns for path in before}, modified)

    def test_synchronize_verifies_both_json_sources_before_writing(self):
        before = self.backup_bytes()
        self.write_source(sync_data.PROJECTS, [dict(self.project, title="尚未同步")])
        (self.root / sync_data.PROFILE.source).write_bytes(b"{")
        code, output = self.run_cli(sync_data.main)
        self.assertEqual(code, 1)
        self.assertIn("data/profile.json", output)
        self.assertEqual(self.backup_bytes(), before)

    def test_synchronize_rolls_back_first_output_if_second_replacement_fails(self):
        before = self.backup_bytes()
        self.write_source(sync_data.PROJECTS, [dict(self.project, title="有變更")])
        self.write_source(sync_data.PROFILE, dict(self.profile, site={"paragraphs": ["有變更"]}))
        original_replace = Path.replace

        def replace(path, target):
            if path.name == "profile-data.js":
                raise PermissionError(13, "fixture has no write permission")
            return original_replace(path, target)

        with mock.patch.object(Path, "replace", replace):
            code, output = self.run_cli(sync_data.main)
        self.assertEqual(code, 1)
        self.assertIn("data/profile-data.js：備援寫入失敗", output)
        self.assertEqual(self.backup_bytes(), before)
        self.assertEqual(list((self.root / "data").glob(".sync-data-*")), [])


if __name__ == "__main__":
    unittest.main()
