#!/usr/bin/env python3
"""Deterministic checks for the zh-TW documentation slice."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
UPSTREAM_COMMIT = "74744182329f08d7a1badc97e47576ef527532a0"

REQUIRED_FILES = (
    "README.md",
    "README.zh-TW.md",
    "TRANSLATION.md",
    "LICENSE",
    "docs/zh-TW/original-announcement.md",
    "docs/zh-TW/architecture.md",
    "docs/zh-TW/results-guide.md",
    "docs/zh-TW/firmware-guide.md",
    "docs/zh-TW/reproduction-status.md",
    "docs/zh-TW/third-party-claims.md",
    "docs/zh-TW/glossary.md",
    "scripts/check_docs.py",
)

TRANSLATED_PAGES = (
    "README.zh-TW.md",
    "docs/zh-TW/original-announcement.md",
    "docs/zh-TW/architecture.md",
    "docs/zh-TW/results-guide.md",
    "docs/zh-TW/firmware-guide.md",
    "docs/zh-TW/reproduction-status.md",
    "docs/zh-TW/third-party-claims.md",
    "docs/zh-TW/glossary.md",
)

DISCLAIMER_LINES = (
    "本倉庫是 slvDev/esp32-ai 的非官方繁體中文翻譯、技術解讀與重現紀錄。",
    "原始專案作者為 Viacheslav Sierbov（slvDev），依 MIT License 使用。",
    "如翻譯與英文原文有歧義，以 upstream 原文為準。",
    "所有效能數字都必須標示為 upstream reported 或 locally reproduced。",
)

ATTRIBUTION_TOKENS = (
    "slvDev/esp32-ai",
    UPSTREAM_COMMIT,
    "Viacheslav Sierbov",
    "MIT License",
)

EVIDENCE_MARKERS = (
    "upstream reported",
    "locally reproduced",
    "本地驗證",
    "尚未驗證",
)

PERFORMANCE_PATTERN = re.compile(
    r"(?:"
    r"\d+(?:\.\d+)?\s*(?:tok/s|ms(?:/token|/model step)?|MB/s)"
    r"|(?:ppl|perplexity)[^\n]{0,24}\d"
    r")",
    re.IGNORECASE,
)

FALSE_ATTRIBUTION_PATTERN = re.compile(
    r"(?:"
    r"(?:upstream|上游|原作者)[^。\n]{0,50}"
    r"(?:實作|支援|包含|提供|implements?|supports?)[^。\n]{0,50}"
    r"(?:I2S|microphone|麥克風|BLE|BTHome|Home Assistant|swarm)"
    r"|"
    r"(?:I2S|microphone|麥克風|BLE|BTHome|Home Assistant|swarm)[^。\n]{0,50}"
    r"(?:由|是)[^。\n]{0,20}(?:upstream|上游|原作者)[^。\n]{0,20}"
    r"(?:實作|提供|implemented)"
    r")",
    re.IGNORECASE,
)

NEGATION_PATTERN = re.compile(
    r"(?:不在|不包含|不支援|不代表|不歸因|不是|未實作|沒有|並非|"
    r"not |does not|isn't|aren't)",
    re.IGNORECASE,
)

MARKDOWN_LINK_PATTERN = re.compile(r"!?\[[^\]]*]\(([^)]+)\)")


def read_text(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def check_required_files(errors: list[str]) -> None:
    for relative_path in REQUIRED_FILES:
        path = ROOT / relative_path
        if not path.is_file():
            errors.append(f"missing required file: {relative_path}")
        elif path.stat().st_size == 0:
            errors.append(f"required file is empty: {relative_path}")


def check_local_links(errors: list[str]) -> None:
    for relative_path in REQUIRED_FILES:
        if not relative_path.endswith(".md"):
            continue

        source = ROOT / relative_path
        text = source.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_PATTERN.findall(text):
            target = raw_target.strip().split(maxsplit=1)[0].strip("<>")
            target = unquote(target)
            if (
                not target
                or target.startswith(("#", "http://", "https://", "mailto:"))
            ):
                continue

            target_without_fragment = target.split("#", 1)[0].split("?", 1)[0]
            if not target_without_fragment:
                continue

            resolved = (source.parent / target_without_fragment).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                errors.append(
                    f"{relative_path}: local link escapes repository: {target}"
                )
                continue

            if not resolved.exists():
                errors.append(
                    f"{relative_path}: local link target is missing: {target}"
                )


def check_disclaimer_and_commit(errors: list[str]) -> None:
    readme = read_text("README.zh-TW.md")
    for line in DISCLAIMER_LINES:
        if line not in readme:
            errors.append(f"README.zh-TW.md: missing disclaimer line: {line}")
    if UPSTREAM_COMMIT not in readme:
        errors.append("README.zh-TW.md: missing full upstream commit")


def check_attribution(errors: list[str]) -> None:
    for relative_path in TRANSLATED_PAGES:
        text = read_text(relative_path)
        for token in ATTRIBUTION_TOKENS:
            if token not in text:
                errors.append(f"{relative_path}: missing attribution token: {token}")


def check_performance_evidence(errors: list[str]) -> None:
    for relative_path in TRANSLATED_PAGES:
        lines = read_text(relative_path).splitlines()
        unit_lines: list[str] = []
        unit_start = 1

        def check_unit() -> None:
            unit = "\n".join(unit_lines)
            if PERFORMANCE_PATTERN.search(unit) and not any(
                marker in unit for marker in EVIDENCE_MARKERS
            ):
                errors.append(
                    f"{relative_path}:{unit_start}: "
                    "performance claim lacks evidence marker"
                )

        for line_number, line in enumerate(lines, start=1):
            stripped = line.lstrip()
            starts_new_unit = stripped.startswith("|") or bool(
                re.match(r"(?:[-*]|\d+\.)\s", stripped)
            )
            if (not line.strip() or starts_new_unit) and unit_lines:
                check_unit()
                unit_lines = []
            if line.strip():
                unit_start = line_number if not unit_lines else unit_start
                unit_lines.append(line)
            if stripped.startswith("|"):
                check_unit()
                unit_lines = []

        if unit_lines:
            check_unit()


def check_false_attribution(errors: list[str]) -> None:
    for relative_path in TRANSLATED_PAGES:
        for line_number, line in enumerate(
            read_text(relative_path).splitlines(), start=1
        ):
            if (
                FALSE_ATTRIBUTION_PATTERN.search(line)
                and not NEGATION_PATTERN.search(line)
            ):
                errors.append(
                    f"{relative_path}:{line_number}: "
                    "possible false attribution of third-party feature to upstream"
                )


def main() -> int:
    errors: list[str] = []
    check_required_files(errors)

    if not errors:
        check_local_links(errors)
        check_disclaimer_and_commit(errors)
        check_attribution(errors)
        check_performance_evidence(errors)
        check_false_attribution(errors)

    if errors:
        print("docs check failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(
        "docs check passed: required files, links, disclaimer, attribution, "
        "evidence labels, and source boundaries"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
