"""Subtitle Translator - Translate subtitle files."""

# Programmed by CoolCat467

from __future__ import annotations

# Subtitle Translator - Translate subtitle files.
# Copyright (C) 2024  CoolCat467
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
__version__ = "0.0.0"
__license__ = "GNU General Public License Version 3"


import argparse

import httpx
import trio

from subtitle_translate import extricate, subtitle_parser, translate


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

    new_texts: dict[int, list[str]] = extricate.list_to_dict(keys, new_values)
    # Convert back to tuples
    return {k: tuple(v) for k, v in new_texts.items()}


async def translate_subtiles(
    source_file: str,
    dest_file: str,
    source_language: str = "auto",
    dest_language: str = "en",
) -> None:
    """Translate subtitles file asynchronously."""
    print(f"Loading subtitles file {source_file!r}...")
    subs, texts = subtitle_parser.convert_text(
        subtitle_parser.parse_file(source_file),
    )

    print(f"Parsed {len(subs)} subtitles")

    print("Translating...")
    new_texts = await translate_texts(texts, source_language, dest_language)

    sentance_count = sum(map(len, texts.values()))
    print(f"Translated {sentance_count} sentences.")

    print("Updating subtitle texts...")
    subs = subtitle_parser.modify_subtitles(subs, new_texts)

    print("Saving...")
    subtitle_parser.write_subtitles_file(dest_file, subs)
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

    # Set destination if not provided
    if args.dest_file is None:
        name, ext = args.source_file.rsplit(".", 1)
        args.dest_file = f"{name}.{args.dest_lang}.{ext}"

    await translate_subtiles(
        args.source_file,
        args.dest_file,
        args.source_lang,
        args.dest_lang,
    )


def cli_run() -> None:
    """Command Line Interface Run."""
    trio.run(run_async)


if __name__ == "__main__":
    print(f"{__title__} v{__version__}\nProgrammed by {__author__}.\n")
    cli_run()
