#!/usr/bin/env python3
"""Build a minimal, reproducible plugin ZIP for review or manual distribution."""

import argparse
import hashlib
import json
from pathlib import Path
import struct
import zipfile


ROOT = Path(__file__).resolve().parents[1]
FILES = {
    ".claude-plugin/plugin.json": ".claude-plugin/plugin.json",
    ".codex-plugin/plugin.json": ".codex-plugin/plugin.json",
    "assets/icon.png": "assets/icon.png",
    "assets/icon.svg": "assets/icon.svg",
    "distribution/README.md": "README.md",
    "LICENSE": "LICENSE",
    "skills/write-goal/SKILL.md": "skills/write-goal/SKILL.md",
    "skills/write-goal/agents/openai.yaml": "skills/write-goal/agents/openai.yaml",
}


def build(root: Path, output: Path) -> dict:
    root, output = root.resolve(), output.resolve()
    if output.suffix != ".zip" or output.is_relative_to(root):
        raise ValueError("Choose a .zip output outside the source checkout")
    payloads = {}
    for source, target in FILES.items():
        path = root / source
        if path.is_symlink() or not path.resolve().is_relative_to(root) or not path.is_file():
            raise ValueError(f"Missing or unsupported package source: {source}")
        payloads[target] = path.read_bytes() if path.suffix == ".png" else path.read_text(encoding="utf-8").encode("utf-8")

    claude = json.loads(payloads[".claude-plugin/plugin.json"])
    codex = json.loads(payloads[".codex-plugin/plugin.json"])
    if (claude["name"], claude["version"]) != (codex["name"], codex["version"]):
        raise ValueError("Host package identity and version must agree")
    image = payloads["assets/icon.png"]
    if len(image) > 2 * 1024 * 1024 or image[:8] != b"\x89PNG\r\n\x1a\n" or len(image) < 24:
        raise ValueError("Listing icon must be a PNG under 2 MiB")
    width, height = struct.unpack(">II", image[16:24])
    if width != height or not 512 <= width <= 2048:
        raise ValueError("Listing icon must be square, 512–2048 pixels")
    for reference in (claude["icon"], codex["interface"]["logo"], codex["interface"]["composerIcon"]):
        if not reference.startswith("./") or reference[2:] not in payloads:
            raise ValueError(f"Unpackaged listing asset: {reference}")

    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for target, content in sorted(payloads.items()):
            info = zipfile.ZipInfo(target, date_time=(1980, 1, 1, 0, 0, 0))
            info.create_system = 3
            info.external_attr = 0o100644 << 16
            info.compress_type = zipfile.ZIP_DEFLATED
            archive.writestr(info, content, compresslevel=9)
    with zipfile.ZipFile(output) as archive:
        if archive.testzip() is not None or set(archive.namelist()) != set(payloads):
            raise ValueError("Built archive failed integrity checks")
    digest = hashlib.sha256(output.read_bytes()).hexdigest()
    output.with_suffix(".sha256").write_text(f"{digest}  {output.name}\n", encoding="utf-8")
    return {"name": claude["name"], "version": claude["version"], "files": len(payloads), "sha256": digest}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(build(ROOT, args.output), indent=2))
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, f"Packaging failed: {error}\n")


if __name__ == "__main__":
    main()
