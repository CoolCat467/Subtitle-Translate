"""Subtitle Parser - Parse subtitle files."""

# Programmed by CoolCat467

from __future__ import annotations

# Subtitle Parser - Parse subtitle files.
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

__title__ = "Subtitle Parser"
__author__ = "CoolCat467"
__version__ = "0.0.0"
__license__ = "GNU General Public License Version 3"


from typing import IO, TYPE_CHECKING, Final, NamedTuple

from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from collections.abc import Generator


# Default text tags
TEXT_TAGS: Final = (
    "h1",
    "h2",
    "h3",
    "h4",
    "h5",
    "h6",
    "b",
    "p",
    "span",
    "strong",
    "em",
    "i",
    "u",
    "small",
    "mark",
    "del",
    "ins",
    "blockquote",
    "address",
    "code",
    "textarea",
)


class Subtitle(NamedTuple):
    """Subtitle object."""

    duration: tuple[int, int]
    html: str


def parse_timestamp(timestamp: str) -> int:
    """Parse timestamp. Return milliseconds."""
    r_h, r_m, r_s_ms = timestamp.split(":", 2)
    h = int(r_h)
    m = int(r_m)
    r_s, r_ms = r_s_ms.split(",", 1)
    s = int(r_s)
    ms = int(r_ms)
    return h * 3600000 + m * 60000 + s * 1000 + ms


def time_to_timestamp(time_: int) -> str:
    """Return timestamp from given time."""
    h, time_ = divmod(time_, 3600000)
    m, time_ = divmod(time_, 60000)
    s, ms = divmod(time_, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def parse_time_fragment(time_fragment: str) -> tuple[int, int]:
    """Parse time fragment."""
    raw_start, raw_end = time_fragment.split(" --> ", 1)
    return parse_timestamp(raw_start), parse_timestamp(raw_end)


def duration_to_fragment(duration: tuple[int, int]) -> str:
    """Return time fragment from duration."""
    start, end = duration
    start_str = time_to_timestamp(start)
    end_str = time_to_timestamp(end)
    return f"{start_str} --> {end_str}"


def parse_subtitle_text(
    file: IO[str],
) -> Generator[tuple[int, Subtitle], None, None]:
    """Yield subtitle id and subtitles from file."""
    mode = 0
    id_: int = 0
    time_fragment: tuple[int, int] = (0, 0)
    html: str = ""
    for line in file:
        line = line.strip()
        if mode == 0:  # Read id number
            id_ = int(line)
            mode += 1
        elif mode == 1:  # Read duration
            raw_time_fragment = line
            time_fragment = parse_time_fragment(raw_time_fragment)
            mode += 1
        elif mode == 2:  # Read HTML until blank line
            if line:
                html += f"{line}\n"
            else:  # Hit blank line
                mode = 0
                yield id_, Subtitle(time_fragment, html[:-1])
                html = ""
    assert not html, "Missing newline after subtitle HTML"


def write_subtitles(file: IO[str], subs: dict[int, Subtitle]) -> None:
    """Write subtitles to file."""
    for subtitle_id, subtitle in subs.items():
        file.write(f"{subtitle_id}\n")
        file.write(f"{duration_to_fragment(subtitle.duration)}\n")
        file.write(f"{subtitle.html}\n\n")


def parse_file(filepath: str) -> Generator[tuple[int, Subtitle], None, None]:
    """Yield subtitle id and subtitle from given filepath."""
    with open(filepath, encoding="utf-8") as fp:
        yield from parse_subtitle_text(fp)


def write_subtitles_file(filepath: str, subs: dict[int, Subtitle]) -> None:
    """Write subs to given filepath."""
    with open(filepath, "w", encoding="utf-8") as fp:
        write_subtitles(fp, subs)


def convert_text(
    gen: Generator[tuple[int, Subtitle], None, None],
    text_tags: tuple[str, ...] = TEXT_TAGS,
) -> tuple[dict[int, Subtitle], dict[int, tuple[str, ...]]]:
    """Read subtitle generator and return subs dictionary and text data."""
    subs: dict[int, Subtitle] = {}
    texts: dict[int, tuple[str, ...]] = {}
    for subtitle_id, subtitle in gen:
        # Get strings from html
        html = subtitle.html
        soup = BeautifulSoup(html, "lxml")
        text: tuple[str, ...] = ()
        for tag in soup.find_all(text_tags):
            string = tag.string
            if string is not None:
                text += (str(tag.string),)
        # Only save if useful
        if text:
            texts[subtitle_id] = text
        # Save subtitle
        subs[subtitle_id] = subtitle
    return subs, texts


def modify_subtitles(
    subs: dict[int, Subtitle],
    new_texts: dict[int, tuple[str, ...]],
    text_tags: tuple[str, ...] = TEXT_TAGS,
) -> dict[int, Subtitle]:
    """Rewrite subtitle html to use new text. Tags MUST be identical."""
    for subtitle_id, subtitle in subs.items():
        # Parse HTML
        html = subtitle.html
        soup = BeautifulSoup(html, "lxml")
        new_text_data = new_texts.get(subtitle_id)
        # Ignore if not exist
        if new_text_data is None:
            continue
        # Here is why tags must be identical.
        # Find text tag blocks and get associated new text data for block
        for tag, new_text in zip(
            soup.find_all(text_tags),
            new_text_data,
            strict=True,
        ):
            if tag.string is None:
                continue
            # Overwrite block text
            tag.string = new_text
        # Get new modified HTML
        new_html = soup.encode().decode()
        # BeautifulSoup adds html tags, which is usually correct,
        # but does not match subtitle files I have seen so far.
        new_html = new_html.removeprefix("<html><body>")
        new_html = new_html.removesuffix("</body></html>")
        # Overwrite subtitle
        subs[subtitle_id] = subtitle._replace(html=new_html)
    return subs


def run() -> None:
    """Run program."""
    # subs_gen = parse_file("<filename>.srt")
    from io import StringIO

    file = StringIO(
        """1
00:00:00,000 --> 24:00:00,000
<b>This is a 24-hour long subtitle text.</b>

""",
    )
    subs_gen = parse_subtitle_text(file)
    subs, texts = convert_text(subs_gen)
    print("\n".join(f"{k}: {v}" for k, v in texts.items()))
    print(f"Parsed {len(subs)} subtitles")
    subs = modify_subtitles(subs, texts)
    out_file = StringIO()
    write_subtitles(out_file, subs)
    print("Saved.\n--------------")
    print(out_file.getvalue())
    print("--------------")


if __name__ == "__main__":
    print(f"{__title__} v{__version__}\nProgrammed by {__author__}.\n")
    run()
