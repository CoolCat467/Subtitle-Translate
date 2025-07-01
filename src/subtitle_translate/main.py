"""Subtitle Translator - Translate subtitle files."""

# Programmed by CoolCat467

from __future__ import annotations

# Subtitle Translator - Translate subtitle files.
# Copyright (C) 2024-2025  CoolCat467
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

__title__ = "Subtitle Translator"
__author__ = "CoolCat467"
__version__ = "0.1.0"
__license__ = "GNU General Public License Version 3"


import argparse
import json
import sys
from typing import TYPE_CHECKING

import httpx
import trio

from subtitle_translate import extricate, subtitle_parser, translate

if TYPE_CHECKING:
    from collections.abc import Iterable


async def translate_texts(
    texts: dict[int, tuple[str, ...]],
    source_lang: str,
    dest_lang: str = "en",
) -> dict[int, tuple[str, ...]]:
    """Translate text from source_lang to dest_lang."""
    # Need keys and values to be separated so we can translate only the
    # values and not the keys.
    # Values have to be lists for extricate as of writing.
    keys, values = extricate.dict_to_list(
        {k: [x.replace("\n", " ") for x in v] for k, v in texts.items()},
    )

    async with httpx.AsyncClient(http2=True) as client:
        new_values = await translate.translate_async(
            client,
            values,
            dest_lang,
            source_lang,
        )

    new_texts = extricate.list_to_dict(keys, new_values)
    # Convert back to tuples
    return {k: tuple(v) for k, v in new_texts.items()}


async def translate_subtitles(
    generator: Iterable[tuple[int, subtitle_parser.Subtitle]],
    source_language: str = "auto",
    dest_language: str = "en",
) -> tuple[dict[int, subtitle_parser.Subtitle], dict[int, tuple[str, ...]]]:
    """Translate subtitles file asynchronously."""
    subs, texts = subtitle_parser.convert_text(generator)

    print(f"Parsed {len(subs)} subtitles")

    print("Translating...")
    new_texts = await translate_texts(texts, source_language, dest_language)

    sentence_count = sum(map(len, texts.values()))
    print(f"Translated {sentence_count} sentences.")

    return subs, new_texts


async def translate_subtitles_srt(
    source_file: str,
    dest_file: str | None = None,
    source_language: str = "auto",
    dest_language: str = "en",
) -> None:
    """Translate subtitles file asynchronously."""
    # Set destination if not provided
    if dest_file is None:
        name, ext = source_file.rsplit(".", 1)
        dest_file = f"{name}.{dest_language}.{ext}"

    print(f"Loading subtitles file {source_file!r}...")
    subs, new_texts = await translate_subtitles(
        subtitle_parser.parse_file_srt(source_file),
        source_language=source_language,
        dest_language=dest_language,
    )

    print("Updating subtitle texts...")
    subs = subtitle_parser.modify_subtitles(subs, new_texts)

    print("Saving...")
    subtitle_parser.write_subtitles_srt_file(dest_file, subs)
    print("Save complete.")
    print(f"Saved to {dest_file!r}")


async def translate_subtitles_vtt(
    source_file: str,
    dest_file: str | None = None,
    source_language: str = "auto",
    dest_language: str = "en",
) -> None:
    """Translate subtitles file asynchronously."""
    print(f"Loading subtitles file {source_file!r}...")
    gen = subtitle_parser.parse_file_vtt(source_file)
    header = next(gen)

    new_header = []
    for line in header:
        assert isinstance(line, str)
        if source_language == "auto" and line.startswith("Language: "):
            key, value = line.split(" ", 1)
            source_language = value
            line = f"{key} {dest_language}"
        new_header.append(line)

    # Set destination if not provided
    if dest_file is None:
        name, ext = source_file.rsplit(".", 1)
        source_lang_ext = f".{source_language}"
        if source_lang_ext in name:
            name = name.removesuffix(source_lang_ext)
        dest_file = f"{name}.{dest_language}.{ext}"

    subs, new_texts = await translate_subtitles(
        enumerate(x for x in gen if isinstance(x, subtitle_parser.Subtitle)),
    )

    print("Updating subtitle texts...")
    subs = subtitle_parser.modify_subtitles_plain(subs, new_texts)

    print("Saving...")
    subtitle_parser.write_subtitles_vtt_file(
        dest_file,
        new_header,
        subs.values(),
    )
    print("Save complete.")
    print(f"Saved to {dest_file!r}")


async def translate_json(
    source_file: str,
    dest_file: str | None = None,
    source_language: str = "auto",
    dest_language: str = "en",
) -> None:
    """Translate subtitles file asynchronously."""
    # Set destination if not provided
    if dest_file is None:
        name, ext = source_file.rsplit(".", 1)
        dest_file = f"{name}.{dest_language}.{ext}"

    print(f"Loading subtitles file {source_file!r}...")

    async with await trio.open_file(source_file, encoding="utf-8") as fp:
        texts = json.loads(await fp.read())

    # Need keys and values to be separated so we can translate only the
    # values and not the keys.
    # Values have to be lists for extricate as of writing.
    keys, values = extricate.dict_to_list(texts)

    print(f"Parsed {len(keys)} subtitles")

    print("Translating...")

    async with httpx.AsyncClient(http2=True) as client:
        new_values = await translate.translate_async(
            client,
            values,
            dest_language,
            source_language,
        )

    new_texts = extricate.list_to_dict(keys, new_values)

    sentence_count = sum(map(len, new_texts.values()))
    print(f"Translated {sentence_count} sentences.")

    print("Saving...")
    async with await trio.open_file(dest_file, "w", encoding="utf-8") as fp:
        await fp.write(json.dumps(new_texts, indent=2))
    print("Save complete.")
    print(f"Saved to {dest_file!r}")


async def run_async() -> None:
    """Run program asynchronously."""
    parser = argparse.ArgumentParser(
        description="Translate subtitles from one language to another.",
        epilog=(
            "Extract subtitles with this:\n"
            "`ffmpeg -i Movie.mkv -map 0:s:0 subs.srt`\n"
            "Might need to change the last 0 if more than one sub track."
        ),
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"{__title__} v{__version__}",
        help="Show the program version and exit.",
    )
    parser.add_argument(
        "source_file",
        type=str,
        help="The source subtitle file to translate.",
    )
    parser.add_argument(
        "--source-lang",
        type=str,
        default="auto",
        help=(
            "The language of the source subtitles (default: 'auto').\n"
            "Must be a ISO 639-1:2002 language code or 'auto' to guess."
        ),
    )
    parser.add_argument(
        "--source-type",
        type=str,
        default="auto",
        help=(
            "Subtitle source type (default: 'auto').\n"
            "Must be either 'srt' or 'vtt', 'json', or 'auto' to guess from filename."
        ),
    )
    parser.add_argument(
        "--dest-lang",
        type=str,
        default="en",
        help=(
            "The language to translate the subtitles to (default: 'en').\n"
            "Must be a ISO 639-1:2002 language code."
        ),
    )
    parser.add_argument(
        "--dest-file",
        type=str,
        help="The destination subtitle file (default: '<source-file>.<source-lang>.<source-file ext>').",
    )

    args = parser.parse_args()

    if args.source_type == "auto":
        name, ext = args.source_file.rsplit(".", 1)
        args.source_type = ext

    if args.source_type == "srt":
        await translate_subtitles_srt(
            args.source_file,
            args.dest_file,
            args.source_lang,
            args.dest_lang,
        )
    elif args.source_type == "vtt":
        await translate_subtitles_vtt(
            args.source_file,
            args.dest_file,
            args.source_lang,
            args.dest_lang,
        )
    elif args.source_type == "json":
        await translate_json(
            args.source_file,
            args.dest_file,
            args.source_lang,
            args.dest_lang,
        )
    else:
        print(f"Unhandled source type {args.source_type!r}.")
        sys.exit(1)


def cli_run() -> None:
    """Command Line Interface Run."""
    trio.run(run_async)


if __name__ == "__main__":
    print(f"{__title__} v{__version__}\nProgrammed by {__author__}.\n")
    cli_run()
