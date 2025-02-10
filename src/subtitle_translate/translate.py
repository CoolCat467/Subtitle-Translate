"""Translate - Tiny translator module."""

from __future__ import annotations

# Translate - Tiny translator module.
# Copyright (C) 2022-2024  CoolCat467
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

__title__ = "Tiny translator module"
__author__ = "CoolCat467"
__license__ = "GNU General Public License Version 3"


import json
import random
from functools import partial
from typing import TYPE_CHECKING, Any, Final, TypeVar, cast

import httpx
import orjson
import trio

from subtitle_translate import agents

if TYPE_CHECKING:
    from collections.abc import Awaitable, Sequence

TIMEOUT: Final[int] = 4
AGENT = random.randint(0, 100000)  # noqa: S311

T = TypeVar("T")


async def gather(*tasks: partial[Awaitable[T]]) -> list[T]:
    """Gather for trio."""

    async def collect(
        index: int,
        task: partial[Awaitable[T]],
        results: dict[int, T],
    ) -> None:
        results[index] = await task()

    results: dict[int, T] = {}
    async with trio.open_nursery() as nursery:
        for index, task in enumerate(tasks):
            nursery.start_soon(collect, index, task, results)
    return [results[i] for i in range(len(tasks))]


##def get_translation_url(sentence: str, to_language: str, source_language: str='auto') -> str:
##    "Return the url you should visit to get query translated to language to_language."
##    query = {'client': 'dict-chrome-ex',
##             'sl'    : source_language,
##             'tl'    : to_language,
##             'q'     : sentence}
##    return 'http://clients5.google.com/translate_a/t?'+urlencode(query)


##def get_translation_url(
##    sentence: str,
##    to_language: str,
##    source_language: str = "auto",
##) -> str:
##    """Return the URL you should visit to get query translated to language to_language."""
##    query = {
##        "client": "gtx",
##        "dt": "t",
##        "sl": source_language,
##        "tl": to_language,
##        "q": sentence,
##    }
##    return "https://translate.googleapis.com/translate_a/single?" + urlencode(
##        query,
##    )


def process_response(result: list[str] | list[list[Any]]) -> str:
    """Return string after processing response."""
    part = result
    while isinstance(part, list):
        next_ = part[0]
        if isinstance(next_, str):
            return next_
        if isinstance(next_, list):
            part = next_
        else:
            raise ValueError(
                f"Unexpected type {type(part)!r}, expected list or str\n{part = }",
            )
    raise RuntimeError("Unreachable")


def is_url(text: str) -> bool:
    """Return True if text is probably a URL."""
    return (
        text.startswith("http")
        and "://" in text
        and "." in text
        and " " not in text
    )


##def translate_sync(
##    sentence: str,
##    to_lang: str,
##    source_lang: str = "auto",
##) -> str:
##    """Return sentence translated from source_lang to to_lang."""
##    if is_url(sentence):
##        # skip URLs
##        return sentence
##
##    # Get URL from function, which uses urllib to generate proper query
##    url = get_translation_url(sentence, to_lang, source_lang)
##    if not url.startswith("http"):
##        raise ValueError("URL not http(s), is this intended?")
##    with urllib.request.urlopen(url, timeout=0.5) as file:
##        request_result = json.loads(file.read())
##    return process_response(request_result)


##async def get_translated_coroutine(
##    client: httpx.AsyncClient,
##    sentence: str,
##    to_lang: str,
##    source_lang: str = "auto",
##) -> str:
##    """Return the sentence translated, asynchronously."""
##    global AGENT  # pylint: disable=global-statement
##
##    if is_url(sentence):
##        # skip URLs
##        return sentence
##    # Make sure we have a timeout, so that in the event of network failures
##    # or something code doesn't get stuck
##    # Get URL from function, which uses urllib to generate proper query
##    url = get_translation_url(sentence, to_lang, source_lang)
##
##    headers = {
##        "User-Agent": "",
##        "Accept": "*/*",
##        "Accept-Language": "en-US,en-GB; q=0.5",
##        "Accept-Encoding": "gzip, deflate",
##        "Connection": "keep-alive",
##    }
##
##    while True:
##        AGENT = (AGENT + 1) % len(agents.USER_AGENTS)
##        headers["User-Agent"] = agents.USER_AGENTS[AGENT]
##
##        try:
##            # Go to that URL and get our translated response
##            response = await client.get(url, headers=headers)
##            # Wait for our response and make it json so we can look at
##            # it like a dictionary
##            return process_response(response.json())
##        except httpx.ConnectTimeout:
##            pass
##        except json.decoder.JSONDecodeError:
##            print(f"{type(response) = }\n{response = }")
##            raise


async def get_translated_coroutine(
    client: httpx.AsyncClient,
    sentence: str,
    to_lang: str,
    source_lang: str = "auto",
) -> str:
    """Return the sentence translated, asynchronously."""
    global AGENT  # pylint: disable=global-statement

    if is_url(sentence):
        # skip URLs
        return sentence
    # Make sure we have a timeout, so that in the event of network failures
    # or something code doesn't get stuck
    # Get URL from function, which uses urllib to generate proper query
    url = "https://translate-pa.googleapis.com/v1/translateHtml"

    headers = {
        "Accept": "*/*",
        "X-Goog-API-Key": "AIzaSyATBXajvzQLTDHEQbcpq0Ihe0vWDHmO520",
        "Content-Type": "application/json+protobuf",
    }

    sentence = sentence.replace("\n", "<br>")

    raw_content = [[[sentence], source_lang, to_lang], "wt_lib"]
    content = orjson.dumps(raw_content)

    while True:
        try:
            # Go to that URL and get our translated response
            response = await client.post(url, content=content, headers=headers)
            # Wait for our response and make it json so we can look at
            # it like a dictionary
            return process_response(response.json()).replace("<br>", "\n")
        except httpx.ConnectTimeout:
            pass
        except json.decoder.JSONDecodeError:
            print(f"{type(response) = }\n{response = }")
            raise
        AGENT = (AGENT + 1) % len(agents.USER_AGENTS)
        headers["User-Agent"] = agents.USER_AGENTS[AGENT]


async def translate_async(
    client: httpx.AsyncClient,
    sentences: Sequence[str],
    to_lang: str,
    source_lang: str,
) -> list[str]:
    """Translate multiple sentences asynchronously."""
    coros = cast(
        "list[partial[Awaitable[str]]]",
        [
            partial(get_translated_coroutine, client, q, to_lang, source_lang)
            for q in sentences
        ],
    )
    return await gather(*coros)


if __name__ == "__main__":
    print(f"{__title__} \nProgrammed by {__author__}.")
