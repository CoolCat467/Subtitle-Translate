# Subtitle-Translate
Script for translating Subtitle (.srt) files with google translate.

<!-- BADGIE TIME -->

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/CoolCat467/Subtitle-Translate/main.svg)](https://results.pre-commit.ci/latest/github/CoolCat467/Subtitle-Translate/main)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)
[![code style: black](https://img.shields.io/badge/code_style-black-000000.svg)](https://github.com/psf/black)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

<!-- END BADGIE TIME -->

## Installation
```console
pip install git+https://github.com/CoolCat467/Localization-Translation-Utility.git
```

## Usage
If you don't already have a separate subtitle file, you can
extract subtitles from your video file with something like this:
```console
ffmpeg -i Movie.mkv -map 0:s:0 subtitles.srt
```
You might need to change the last 0 if there is more than one subtitle
track in your file.
Please note that this will absolutely not work at all if your video file
does have a baked-in subtitle track!

```console
> subtitle_translate
usage: subtitle_translate [-h] [--version] [--source-lang SOURCE_LANG] [--dest-lang DEST_LANG] [--dest-file DEST_FILE] source_file

Translate subtitles from one language to another.

positional arguments:
  source_file       The source subtitle file to translate.

options:
  -h, --help        show this help message and exit
  --version         Show the program version and exit.
  --source-lang SOURCE_LANG
                    The language of the source subtitles (default: 'auto'). Must be a ISO 639-1:2002 language code or 'auto' to
                    guess.
  --dest-lang DEST_LANG
                    The language to translate the subtitles to (default: 'en'). Must be a ISO 639-1:2002 language code.
  --dest-file DEST_FILE
                    The destination subtitle file (default: '<source-file>.<source-lang>.<source-file ext>').
```

When run with any valid source file, program save translated results in <dest-file> in the current working directory.



General code layout:

`main.py` is the command line interface handler.

`subtitle_parser.py` handles reading, parsing, and writing subtitle files.

`translate.py` handles talking to Google Translate.

`extricate.py` (name means taking apart and putting back together) is used by the translation
module to split dictionaries into a keys list and a values list so it can translate all the
values and then rebuild the dictionary by re-combining the keys list and the new translated
values list.

`agents.py` from https://github.com/Animenosekai/useragents/blob/main/pyuseragents/data/list.py
is by Anime no Sekai and has a ton of random user agents to use so Google Translate
doesn't get suspicious of us sending tens of thousands of requests without an API key
