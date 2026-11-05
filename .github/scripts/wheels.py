# Copyright (c) 2026 NVIDIA CORPORATION All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Inspect and validate the distributions built by the wheel workflows.

digest DIRECTORY
    Print one SHA-256 that covers the name and content of every wheel in
    DIRECTORY. In the C locale it equals ``sha256sum *.whl | sha256sum``.
check PLATFORM DIRECTORY
    Check that DIRECTORY holds the wheels that the platform workflow should
    build for the version in pyproject.toml.
collect --tag TAG --out DIRECTORY --sdist DIRECTORY --wheels PLATFORM=DIRECTORY ...
    Check that the wheels and the sdist are exactly what a release of TAG
    should publish, and copy them to one directory.

Run with ``python -I`` and no third-party packages.
"""

import argparse
import hashlib
import re
import shutil
import tarfile
import tomllib
import zipfile
from email.parser import BytesParser
from pathlib import Path

DISTRIBUTION = "pyoptix"
# The wheels contain only the core module and no dependencies. Anything else,
# such as tests, examples or a library bundled by auditwheel, is a mistake.
PACKAGES = {"optix"}
# The CUDA runtime is linked statically. A reference to its shared library means
# that setting was lost, and the wheel would not import without a CUDA Toolkit.
CUDA_RUNTIME_LIBRARIES = (b"cudart64_", b"libcudart.so")

# Platform tags of the wheels that each platform workflow builds.
_MANYLINUX = r"manylinux(?:_\d+_\d+|\d+)_x86_64"
PLATFORM_TAGS = {
    "linux-x86_64": re.compile(rf"{_MANYLINUX}(?:\.{_MANYLINUX})*"),
    "windows-x86_64": re.compile(r"win_amd64"),
}


def _wheel_tags(wheel: Path) -> tuple[str, str, str]:
    """Return the (python, abi, platform) tags from a wheel file name."""
    parts = wheel.name.removesuffix(".whl").split("-")
    if len(parts) not in (5, 6):
        raise SystemExit(f"Not a wheel file name: {wheel.name}")
    return parts[-3], parts[-2], parts[-1]


def _wheels(directory: Path) -> list[Path]:
    wheels = sorted(directory.glob("*.whl"))
    if not wheels:
        raise SystemExit(f"No wheels in {directory}")
    return wheels


def digest(directory: Path) -> str:
    lines = "".join(
        f"{hashlib.sha256(wheel.read_bytes()).hexdigest()}  {wheel.name}\n" for wheel in _wheels(directory)
    )
    return hashlib.sha256(lines.encode()).hexdigest()


def _check_metadata(source: str, metadata, version: str) -> None:
    if metadata["Name"] != DISTRIBUTION:
        raise SystemExit(f"{source}: unexpected distribution {metadata['Name']}")
    if metadata["Version"] != version:
        raise SystemExit(f"{source}: version {metadata['Version']} does not match the expected version {version}")


def _check_wheel(wheel: Path, version: str) -> None:
    with zipfile.ZipFile(wheel) as archive:
        top_level = {name.split("/")[0] for name in archive.namelist()}
        dist_infos = {name for name in top_level if name.endswith(".dist-info")}
        unexpected = top_level - PACKAGES - dist_infos
        if unexpected:
            files = sorted(name for name in archive.namelist() if name.split("/")[0] in unexpected)
            raise SystemExit(f"{wheel.name}: unexpected contents {files[:10]}; expected only {sorted(PACKAGES)}")
        if len(dist_infos) != 1:
            raise SystemExit(f"{wheel.name}: expected one .dist-info directory, found {sorted(dist_infos)}")
        (dist_info,) = dist_infos
        metadata = BytesParser().parsebytes(archive.read(f"{dist_info}/METADATA"))
        for name in archive.namelist():
            if name.endswith((".so", ".pyd")):
                data = archive.read(name)
                found = [library.decode() for library in CUDA_RUNTIME_LIBRARIES if library in data]
                if found:
                    raise SystemExit(f"{wheel.name}: {name} refers to the CUDA runtime library {found}")
    _check_metadata(wheel.name, metadata, version)
    if metadata.get_all("Requires-Dist"):
        raise SystemExit(f"{wheel.name}: the wheel must not declare dependencies: {metadata.get_all('Requires-Dist')}")


def _check_sdist(sdist: Path, version: str) -> None:
    if sdist.name != f"{DISTRIBUTION}-{version}.tar.gz":
        raise SystemExit(f"Unexpected sdist name: {sdist.name}")
    with tarfile.open(sdist) as archive:
        # The sdist includes every file that git does not ignore.
        build_output = [name for name in archive.getnames() if name.endswith((".whl", ".tar.gz"))]
        if build_output:
            raise SystemExit(f"{sdist.name}: contains build output {build_output}")
        member = archive.extractfile(f"{DISTRIBUTION}-{version}/PKG-INFO")
        if member is None:
            raise SystemExit(f"{sdist.name}: missing PKG-INFO")
        metadata = BytesParser().parsebytes(member.read())
    _check_metadata(sdist.name, metadata, version)


def _pyproject() -> dict:
    return tomllib.loads(Path("pyproject.toml").read_text(encoding="utf-8"))


def check(platform: str, directory: Path, version: str) -> list[Path]:
    """Check the wheels built for one platform and return them."""
    # The Python versions come from the same list that cibuildwheel builds.
    expected = set()
    for selector in _pyproject()["tool"]["cibuildwheel"]["build"]:
        if not re.fullmatch(r"cp3\d+-\*", selector):
            raise SystemExit(f"Unsupported tool.cibuildwheel.build selector: {selector}")
        expected.add(selector.removesuffix("-*"))

    wheels = _wheels(directory)
    found = []
    for wheel in wheels:
        python_tag, abi_tag, platform_tag = _wheel_tags(wheel)
        if abi_tag != python_tag:
            raise SystemExit(f"{wheel.name}: expected the {python_tag} ABI")
        if not PLATFORM_TAGS[platform].fullmatch(platform_tag):
            raise SystemExit(f"{wheel.name}: unexpected {platform} platform tag {platform_tag}")
        _check_wheel(wheel, version)
        found.append(python_tag)
    if sorted(found) != sorted(expected):
        raise SystemExit(f"{platform}: expected wheels for {sorted(expected)}, found {sorted(found)}")
    return wheels


def collect(tag: str, wheel_dirs: dict[str, Path], sdist_dir: Path, out_dir: Path) -> None:
    if not re.fullmatch(r"v\d.*", tag):
        raise SystemExit(f"Tag must look like v<version>, got {tag}")
    version = tag.removeprefix("v")

    out_dir.mkdir(parents=True)
    for platform, directory in wheel_dirs.items():
        for wheel in check(platform, directory, version):
            shutil.copy2(wheel, out_dir / wheel.name)

    sdists = list(sdist_dir.glob("*.tar.gz"))
    if len(sdists) != 1:
        raise SystemExit(f"Expected one sdist, found {len(sdists)}")
    _check_sdist(sdists[0], version)
    shutil.copy2(sdists[0], out_dir / sdists[0].name)
    print(f"Collected {len(list(out_dir.iterdir()))} distributions for {tag}:")
    for path in sorted(out_dir.iterdir()):
        print(f"  {path.name}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("digest").add_argument("directory", type=Path)
    check_parser = commands.add_parser("check")
    check_parser.add_argument("platform", choices=sorted(PLATFORM_TAGS))
    check_parser.add_argument("directory", type=Path)
    collect_parser = commands.add_parser("collect")
    collect_parser.add_argument("--tag", required=True)
    collect_parser.add_argument("--out", type=Path, required=True)
    collect_parser.add_argument("--sdist", type=Path, required=True)
    collect_parser.add_argument(
        "--wheels",
        action="append",
        required=True,
        metavar="PLATFORM=DIRECTORY",
        help=f"wheels built for one platform ({', '.join(sorted(PLATFORM_TAGS))})",
    )
    args = parser.parse_args()

    if args.command == "digest":
        print(digest(args.directory))
    elif args.command == "check":
        wheels = check(args.platform, args.directory, _pyproject()["project"]["version"])
        print(f"Checked {len(wheels)} {args.platform} wheels:")
        for wheel in wheels:
            print(f"  {wheel.name}")
    else:
        wheel_dirs = {}
        for spec in args.wheels:
            platform, _, directory = spec.partition("=")
            if platform not in PLATFORM_TAGS or not directory:
                raise SystemExit(f"Expected PLATFORM=DIRECTORY with a platform from {sorted(PLATFORM_TAGS)}, got {spec}")
            wheel_dirs[platform] = Path(directory)
        collect(args.tag, wheel_dirs, args.sdist, args.out)


if __name__ == "__main__":
    main()
