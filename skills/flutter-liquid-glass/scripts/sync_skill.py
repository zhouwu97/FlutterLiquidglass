"""Check or explicitly synchronize the demo bundle and an installed skill copy.

Defaults to read-only checks. Use --write to copy changed/missing files.
Extra destination files are reported for a demo bundle and preserved on install.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import re
import shutil
import sys


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEXT_SUFFIXES = {".md", ".yaml", ".yml", ".dart", ".frag", ".kt", ".py", ".txt"}
IGNORED_PARTS = {".git", ".dart_tool", "build", "__pycache__"}


def package_files(root: Path) -> list[Path]:
    return sorted(
        path for path in root.rglob("*")
        if path.is_file()
        and not IGNORED_PARTS.intersection(path.relative_to(root).parts)
        and path.suffix not in {".pyc", ".pyo"}
    )


def same_content(source: Path, destination: Path) -> bool:
    if not destination.is_file():
        return False
    source_bytes, destination_bytes = source.read_bytes(), destination.read_bytes()
    if source.suffix.lower() in TEXT_SUFFIXES:
        return source_bytes.decode("utf-8-sig").replace("\r\n", "\n") == destination_bytes.decode("utf-8-sig").replace("\r\n", "\n")
    return source_bytes == destination_bytes


def synchronize(pairs: list[tuple[Path, Path]], write: bool) -> int:
    differences = 0
    for source, destination in pairs:
        if same_content(source, destination):
            continue
        differences += 1
        print(f"{'COPY' if write else 'DIFF'} {source} -> {destination}")
        if write:
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
    if write:
        differences = sum(not same_content(source, destination) for source, destination in pairs)
    print(f"Checked {len(pairs)} files; {differences} remaining differences.")
    return differences


def demo_pairs(demo_root: Path) -> list[tuple[Path, Path]]:
    manifest = demo_root / "pubspec.yaml"
    if not manifest.is_file() or not re.search(r"^name:\s*bottom_nav_demo\s*$", manifest.read_text(encoding="utf-8-sig"), re.MULTILINE):
        raise ValueError("--demo-root must name the bottom_nav_demo repository, not a business application")
    bundle = SKILL_ROOT / "assets/reference_flutter"
    pairs = [(manifest, bundle / "pubspec.yaml")]
    for directory, pattern in (("lib", "*.dart"), ("shaders", "*.frag"), ("test", "*.dart"), ("licenses", "*.txt"), ("assets/fonts", "*")):
        folder = demo_root / directory
        if not folder.is_dir():
            raise ValueError(f"Missing demo resource directory: {folder}")
        pairs.extend((path, bundle / path.relative_to(demo_root)) for path in sorted(folder.rglob(pattern)) if path.is_file())
    android_source = demo_root / "android/app/src/main/kotlin/com/example/bottom_nav_demo/MainActivity.kt"
    if not android_source.is_file():
        raise ValueError(f"Missing Android reference: {android_source}")
    pairs.append((android_source, bundle / "android-reference/MainActivity.kt"))
    return pairs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--demo-root", type=Path)
    parser.add_argument("--install-to", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.demo_root is None and args.install_to is None:
        parser.error("Specify --demo-root and/or --install-to; checks are read-only unless --write is present")
    install_root = args.install_to.resolve() if args.install_to else None
    if install_root is not None and (
        install_root == SKILL_ROOT or install_root in SKILL_ROOT.parents or SKILL_ROOT in install_root.parents
    ):
        parser.error("Installed copy must not overlap the source skill directory")
    differences = 0
    if args.demo_root is not None:
        root = args.demo_root.resolve()
        print(f"Demo source: {root}\nSkill package: {SKILL_ROOT}")
        pairs = demo_pairs(root)
        expected = {destination for _, destination in pairs}
        extras = set(package_files(SKILL_ROOT / "assets/reference_flutter")) - expected
        for extra in sorted(extras):
            print(f"EXTRA bundled resource (not removed): {extra}")
        differences += len(extras) + synchronize(pairs, args.write)
    if install_root is not None:
        print(f"Skill source: {SKILL_ROOT}\nInstalled copy: {install_root}")
        pairs = [(source, install_root / source.relative_to(SKILL_ROOT)) for source in package_files(SKILL_ROOT)]
        differences += synchronize(pairs, args.write)
    return 1 if differences else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, UnicodeError, ValueError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        raise SystemExit(2)
