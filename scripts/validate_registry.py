#!/usr/bin/env python3
"""Validate AGUI-registry index, packages and zip layout."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "index.json"
NAME_RE = re.compile(r"^[A-Za-z0-9._-]+$")
VERSION_RE = re.compile(r"^\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?$")

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"{path.relative_to(ROOT)}: 无法解析 JSON: {exc}")
        return None


def package_zip_path(url: str, name: str, version: str) -> Path:
    marker = "/packages/"
    if marker in url:
        tail = url.split(marker, 1)[1].split("?", 1)[0]
        return ROOT / "packages" / tail
    return ROOT / "packages" / f"{name}-{version}.zip"


def validate_zip(name: str, version: str, entry: str, path: Path, sha256: str) -> None:
    rel = path.relative_to(ROOT)
    if not path.is_file():
        fail(f"{name}@{version}: 缺少 zip {rel}")
        return

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest.lower() != sha256.lower():
        fail(f"{name}@{version}: SHA-256 不匹配，实际 {digest}")

    try:
        with zipfile.ZipFile(path) as zf:
            names = zf.namelist()
            for member in names:
                normalized = member.replace("\\", "/")
                if normalized.startswith("/") or ".." in normalized.split("/"):
                    fail(f"{name}@{version}: zip 条目路径越界: {member}")
            if "agui-package.json" not in names:
                fail(f"{name}@{version}: zip 根目录缺少 agui-package.json")
                return
            manifest = json.loads(zf.read("agui-package.json").decode("utf-8"))
            if manifest.get("name") != name:
                fail(f"{name}@{version}: manifest.name={manifest.get('name')!r}")
            if manifest.get("version") != version:
                fail(f"{name}@{version}: manifest.version={manifest.get('version')!r}")
            manifest_entry = manifest.get("entry") or entry
            if manifest_entry != entry:
                fail(f"{name}@{version}: manifest.entry={manifest_entry!r}，索引 entry={entry!r}")
            if entry not in names:
                fail(f"{name}@{version}: zip 中不存在入口 {entry}")
            if not any(n.endswith(".ag") for n in names):
                fail(f"{name}@{version}: zip 中没有 .ag 文件")
    except zipfile.BadZipFile:
        fail(f"{name}@{version}: 不是有效 zip")
    except Exception as exc:
        fail(f"{name}@{version}: 读取 zip 失败: {exc}")


def main() -> int:
    index = load_json(INDEX)
    if index is None:
        return 1
    if index.get("version") != 1:
        fail(f"index.version={index.get('version')!r}，应为 1")

    packages = index.get("packages")
    if not isinstance(packages, dict):
        fail("index.packages 必须是对象")
        packages = {}

    for name, pkg in packages.items():
        if not NAME_RE.match(name) or ".." in name:
            fail(f"非法包名: {name!r}")
            continue
        if not isinstance(pkg, dict):
            fail(f"{name}: 包描述必须是对象")
            continue
        versions = pkg.get("versions")
        if not isinstance(versions, dict) or not versions:
            fail(f"{name}: versions 必须是非空对象")
            continue
        latest = pkg.get("latest")
        if latest and latest not in versions:
            fail(f"{name}: latest={latest!r} 不在 versions 中")
        if not pkg.get("description"):
            fail(f"{name}: 缺少 description")

        seen_sha: dict[str, str] = {}
        for version, meta in versions.items():
            if not VERSION_RE.match(version):
                fail(f"{name}@{version}: 版本号不是 SemVer")
            if not isinstance(meta, dict):
                fail(f"{name}@{version}: 版本描述必须是对象")
                continue
            url = meta.get("url", "")
            sha = meta.get("sha256", "")
            entry = meta.get("entry") or f"{name}.ag"
            if not url:
                fail(f"{name}@{version}: 缺少 url")
                continue
            if not sha or len(sha) != 64:
                fail(f"{name}@{version}: sha256 必须是 64 位十六进制")
                continue
            if sha.lower() in seen_sha:
                fail(f"{name}@{version}: 与 {seen_sha[sha.lower()]} 共用同一 SHA-256")
            seen_sha[sha.lower()] = f"{name}@{version}"
            path = package_zip_path(url, name, version)
            try:
                path.relative_to(ROOT)
            except ValueError:
                fail(f"{name}@{version}: zip 路径越出仓库: {path}")
                continue
            validate_zip(name, version, entry, path, sha)

    if errors:
        print("Registry 校验失败：", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1

    print(f"Registry 校验通过：{len(packages)} 个包")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
