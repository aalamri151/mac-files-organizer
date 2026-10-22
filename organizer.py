#!/usr/bin/env python3
"""Preview or organize a folder's immediate files without overwriting files."""

import argparse
from dataclasses import dataclass
from pathlib import Path
import shutil
import sys


GROUPS = {
    "Images": "jpg jpeg png gif webp heic heif svg bmp tiff tif",
    "Documents": "pdf txt md doc docx odt rtf pages csv xls xlsx numbers ppt pptx key",
    "Audio": "mp3 wav aac flac m4a ogg aiff",
    "Videos": "mp4 mov mkv avi webm m4v",
    "Archives": "zip tar gz bz2 xz rar 7z",
    "Installers": "dmg pkg iso",
    "Code": "py js ts jsx tsx html css json yaml yml sh swift rb go rs java c cpp h",
}
EXTENSIONS = {ext: group for group, exts in GROUPS.items() for ext in exts.split()}


@dataclass(frozen=True)
class Move:
    source: Path
    destination: Path


def plan(folder: Path) -> list[Move]:
    """Ignore directories, symlinks, hidden files, and incomplete downloads."""
    moves = []
    reserved = set()
    for source in sorted(folder.iterdir()):
        if (source.name.startswith(".") or source.is_symlink()
                or not source.is_file()
                or source.suffix.lower() in {".part", ".download", ".crdownload"}):
            continue
        group = EXTENSIONS.get(source.suffix.lower().lstrip("."), "Other")
        target_dir = folder / group
        if target_dir.is_symlink():
            raise ValueError(f"Refusing symlink destination: {target_dir}")
        if target_dir.exists() and not target_dir.is_dir():
            raise ValueError(f"Destination is not a directory: {target_dir}")
        destination = target_dir / source.name
        number = 1
        while destination.exists() or destination.is_symlink() or destination in reserved:
            destination = target_dir / f"{source.stem} ({number}){source.suffix}"
            number += 1
        reserved.add(destination)
        moves.append(Move(source, destination))
    return moves


def apply(moves: list[Move]) -> None:
    for move in moves:
        if move.source.is_symlink() or not move.source.is_file():
            raise ValueError(f"Source is no longer a regular file: {move.source}")
        if move.destination.parent.is_symlink():
            raise ValueError(f"Refusing symlink destination: {move.destination.parent}")
        move.destination.parent.mkdir(exist_ok=True)
        # Exclusive creation also prevents overwrites if a file appears after preview.
        with move.source.open("rb") as source:
            with move.destination.open("xb") as destination:
                try:
                    shutil.copyfileobj(source, destination)
                    shutil.copystat(move.source, move.destination)
                except BaseException:
                    move.destination.unlink()
                    raise
        move.source.unlink()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("folder", type=Path, help="Folder to organize (not recursive)")
    parser.add_argument("--apply", action="store_true", help="Move files; otherwise preview only")
    args = parser.parse_args(argv)
    folder = args.folder.expanduser().resolve()
    if not folder.is_dir():
        parser.error(f"Not a directory: {folder}")
    try:
        moves = plan(folder)
        for move in moves:
            print(f"{move.source.name} -> {move.destination.relative_to(folder)}")
        if args.apply:
            apply(moves)
        print(f"{'Organized' if args.apply else 'Previewed'} {len(moves)} file(s).")
        if moves and not args.apply:
            print("No files changed. Run again with --apply to organize.")
        return 0
    except (OSError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
