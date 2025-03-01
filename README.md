# Subtitle-Translate
Script for translating Subtitle (.srt and .vtt) files with google translate.

[![CI](https://github.com/CoolCat467/Subtitle-Translate/actions/workflows/ci.yml/badge.svg)](https://github.com/CoolCat467/Subtitle-Translate/actions/workflows/ci.yml)
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
This script also supports `.vtt` files as of v0.1.0.
Please note that this will absolutely not work at all if your video file
does have a baked-in subtitle track!

### Example
Say `subtitles.srt` is in French, but you want it to be English. In that case, run
```bash
subtitle_translate --source-lang fr subtitles.srt
```
which will create `subtitles.en.srt` in the current working directory because we didn't specify `--dest-file` and it used the default
output filename formatting.

Another example, say `subtitles.ko.vtt` is in Korean but you want it in English.
```bash
subtitle_translate subtitles.ko.vtt
```
which will create `subtitles.en.vtt` in the current working directory, because in `vtt` processing mode it's smarter and
reads the `Language: ko` tag from the file header and knows it's in Korean. Reminder, if `--source-lang` not specified and can't
find language from file header if in `vtt` mode, it will default to `auto` and have google translate guess what the source
language is, which while it works might not be as accurate.

### Command Help Information
```console
> subtitle_translate
usage: subtitle_translate [-h] [--version] [--source-lang SOURCE_LANG] [--source-type SOURCE_TYPE] [--dest-lang DEST_LANG]
                          [--dest-file DEST_FILE]
                          source_file

Translate subtitles from one language to another.

positional arguments:
  source_file       The source subtitle file to translate.

options:
  -h, --help        show this help message and exit
  --version         Show the program version and exit.
  --source-lang SOURCE_LANG
                    The language of the source subtitles (default: 'auto'). Must be a ISO 639-1:2002 language code or 'auto' to
                    guess.
  --source-type SOURCE_TYPE
                    Subtitle source type (default: 'auto'). Must be either 'srt' or 'vtt', or 'auto' to guess from filename.
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


### Links
* Source Code - https://github.com/CoolCat467/Subtitle-Translate.git
* Issues      - https://github.com/CoolCat467/Subtitle-Translate/issues

### License
-------
Code and documentation are available according to the GNU General Public License v3.0 (see [LICENSE](https://github.com/CoolCat467/Subtitle-Translate/blob/HEAD/LICENSE)).
