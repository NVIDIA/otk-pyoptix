# Copyright (c) 2026 NVIDIA CORPORATION All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

"""Assemble the minimal CUDA Toolkit needed to build the extension.

The extension only links the CUDA driver and runtime, so CI downloads the
cudart and nvcc redistributables instead of a full Toolkit installer. Archives
are pinned by SHA-256; update the table together with ``CUDA_VERSION``. Hashes
come from https://developer.download.nvidia.com/compute/cuda/redist/redistrib_<version>.json.
"""

import argparse
import hashlib
import os
import shutil
import tarfile
import tempfile
import urllib.request
import zipfile
from pathlib import Path

CUDA_VERSION = "12.9.1"
REDIST_URL = "https://developer.download.nvidia.com/compute/cuda/redist"
ARCHIVES = {
    "linux-x86_64": [
        (
            "cuda_cudart/linux-x86_64/cuda_cudart-linux-x86_64-12.9.79-archive.tar.xz",
            "1f6ad42d4f530b24bfa35894ccf6b7209d2354f59101fd62ec4a6192a184ce99",
        ),
        (
            "cuda_nvcc/linux-x86_64/cuda_nvcc-linux-x86_64-12.9.86-archive.tar.xz",
            "7a1a5b652e5ef85c82b721d10672fc9a2dbaab44e9bd3c65a69517bf53998c35",
        ),
    ],
    "windows-x86_64": [
        (
            "cuda_cudart/windows-x86_64/cuda_cudart-windows-x86_64-12.9.79-archive.zip",
            "179e9c43b0735ffe67207b3da556eb5a0c50f3047961882b7657d3b822d34ef8",
        ),
        (
            "cuda_nvcc/windows-x86_64/cuda_nvcc-windows-x86_64-12.9.86-archive.zip",
            "227b109663b5e57d2718bcabb24a4ba0d9d4e52d958e327dc476f7c28691be85",
        ),
    ],
}


def _download(relative_path: str, sha256: str, directory: Path) -> Path:
    path = directory / Path(relative_path).name
    digest = hashlib.sha256()
    with urllib.request.urlopen(f"{REDIST_URL}/{relative_path}") as response, path.open("wb") as file:
        while chunk := response.read(1 << 20):
            digest.update(chunk)
            file.write(chunk)
    if digest.hexdigest() != sha256:
        raise RuntimeError(f"SHA-256 mismatch for {relative_path}: {digest.hexdigest()}")
    return path


def _extract(archive: Path, prefix: Path, directory: Path) -> None:
    # Each archive has one top-level directory; merge its contents into the prefix.
    staging = directory / "staging"
    if archive.suffix == ".zip":
        with zipfile.ZipFile(archive) as zip_file:
            zip_file.extractall(staging)
    else:
        with tarfile.open(archive) as tar_file:
            tar_file.extractall(staging, filter="data")
    (root,) = staging.iterdir()
    shutil.copytree(root, prefix, dirs_exist_ok=True)
    shutil.rmtree(staging)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--platform", choices=sorted(ARCHIVES), required=True)
    parser.add_argument("--prefix", type=Path, required=True, help="installation directory")
    args = parser.parse_args()

    prefix = args.prefix.resolve()
    prefix.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp:
        for relative_path, sha256 in ARCHIVES[args.platform]:
            print(f"Installing {relative_path}")
            _extract(_download(relative_path, sha256, Path(temp)), prefix, Path(temp))

    # Point CMake's FindCUDAToolkit at the assembled Toolkit in later steps. The
    # GPU runners have no CUDA runtime library, so builds link it statically.
    cudart_static = prefix / (
        "lib/x64/cudart_static.lib" if args.platform.startswith("windows") else "lib/libcudart_static.a"
    )
    if github_env := os.environ.get("GITHUB_ENV"):
        with open(github_env, "a", encoding="utf-8") as file:
            file.write(f"CUDA_PATH={prefix}\nCUDAToolkit_ROOT={prefix}\n")
            file.write(f"CUDART_STATIC_LIBRARY={cudart_static.as_posix()}\n")
    if github_path := os.environ.get("GITHUB_PATH"):
        with open(github_path, "a", encoding="utf-8") as file:
            file.write(f"{prefix / 'bin'}\n")
    print(f"CUDA {CUDA_VERSION} installed to {prefix}")


if __name__ == "__main__":
    main()
