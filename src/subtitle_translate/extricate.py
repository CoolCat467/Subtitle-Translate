"""Extricate - Take dictionaries apart and put them back together."""

# Programmed by CoolCat467

from __future__ import annotations

# Extricate - Take apart and put back together dictionaries
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

__title__ = "Extricate"
__author__ = "CoolCat467"
__license__ = "GNU General Public License Version 3"


from typing import TYPE_CHECKING, Any, Final

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable


def wrap_quotes(text: str, quotes: str = '"') -> str:
    """Return text wrapped in quotes."""
    return f"{quotes}{text}{quotes}"


def unwrap_quotes(text: str, layers: int = 1) -> str:
    """Unwrap given layers of quotes."""
    return text[layers:-layers]


def combine_end(data: Iterable[str], end: str = "and") -> str:
    """Join values of text with the last one properly."""
    data = list(data)
    if len(data) >= 2:
        data[-1] = f"{end} {data[-1]}"
    if len(data) > 2:
        return ", ".join(data)
    return " ".join(data)


TYPE_CHAR: Final = {
    "str": "!",
    "int": "@",
    "float": "#",
    "bool": "$",
    "dict": "%",
    "list": "^",
    "NoneType": "&",
}
CHAR_TYPE: Final = {v: k for k, v in TYPE_CHAR.items()}

SEP: Final = "*"


def dict_to_list(data: Any) -> tuple[list[str], list[str]]:
    """Convert dictionary to two lists, one of keys, one of values."""

    def read_block(data: Any) -> tuple[list[str], list[str]]:
        """Read block."""
        keys: list[str] = []
        values: list[str] = []

        match type(data).__name__:
            case "dict" as dtype:
                assert isinstance(data, dict)  # Mypy doesn't understand
                # If empty dict
                if not data:
                    keys.append(wrap_quotes(f"{SEP}", TYPE_CHAR[dtype]))
                    values.append("")
                # Will not run if no data to enumerate
                for key, value in data.items():
                    # Ensure key won't break everything
                    intersect = set(str(key)) & (set(CHAR_TYPE) | {SEP})
                    if intersect:
                        raise ValueError(
                            'Dict key contains CHAR_TYPE value(s) "'
                            f"{''.join(intersect)}" + '"',
                        )

                    key = wrap_quotes(key, TYPE_CHAR[type(key).__name__])
                    for block_k, block_v in zip(
                        *read_block(value),
                        strict=True,
                    ):
                        keys.append(
                            wrap_quotes(
                                f"{key}{SEP}{block_k}",
                                TYPE_CHAR[dtype],
                            ),
                        )
                        values.append(block_v)
            case "list" as dtype:
                assert isinstance(data, list)  # Mypy doesn't understand
                # If empty list
                if not data:
                    keys.append(wrap_quotes(f"{SEP}", TYPE_CHAR[dtype]))
                    values.append("")
                # Will not run if no data to enumerate
                for key, value in enumerate(data):
                    for block_k, block_v in zip(
                        *read_block(value),
                        strict=True,
                    ):
                        keys.append(
                            wrap_quotes(
                                f"{key}{SEP}{block_k}",
                                TYPE_CHAR[dtype],
                            ),
                        )
                        values.append(block_v)
            case "str" | "int" | "bool" | "float" | "NoneType" as dtype:
                keys.append(wrap_quotes("", TYPE_CHAR[dtype]))
                values.append(str(data))
            case _ as dtype:
                raise TypeError(
                    f'Expected type {combine_end(TYPE_CHAR, "or")}, got "{dtype}"',
                )
        return keys, values

    return read_block(data)


class Segment:
    """Segment with item. Basically like a pointer."""

    __slots__ = ("item",)

    def __init__(self, item: Any = None) -> None:
        """Initialize Segment."""
        self.item = item

    def __repr__(self) -> str:
        """Return representation of self."""
        if self.item is None:
            return "Segment()"
        return f"Segment({self.item!r})"

    def is_container(self) -> bool:
        """Return if is container."""
        return isinstance(self.item, list | dict)

    def unwrap(self) -> Any:
        """Unwrap contained item."""
        if not self.is_container():
            return self.item
        match type(self.item).__name__:
            case "dict":
                assert isinstance(self.item, dict)  # Mypy doesn't understand
                dict_data = {}
                for key, item in self.item.items():
                    if isinstance(item, Segment):
                        dict_data[key] = item.unwrap()
                        continue
                    dict_data[key] = item
                return dict_data
            case "list":
                assert isinstance(self.item, list)  # Mypy doesn't understand
                list_data = []
                for item in self.item:
                    if isinstance(item, Segment):
                        list_data.append(item.unwrap())
                        continue
                    list_data.append(item)
                return list_data
            case _ as dtype:
                raise ValueError(f'Expected dict or list, got "{dtype}"')


def list_to_dict(keys: list[str], values: list[str]) -> Any:
    """Convert split lists of compiled keys and values back into dictionary."""

    def handle_map(
        segment: Segment,
        key: str,
        value: str,
        map_func: Callable[[Any], Any],
    ) -> None:
        """Unwrap key and either set segment item or continue to unwrap."""
        index = unwrap_quotes(key)
        if index == "":
            segment.item = map_func(value)
            return
        unwrap_key(segment, index, map_func(value))

    def unwrap_key(segment: Segment, key: str, value: Any) -> None:
        """Take apart key and set segment item to value in the right place."""
        head = key[0]
        if head == "":
            segment.item = value
            return
        if head not in CHAR_TYPE:
            raise ValueError(f'Key type character "{head}" unrecognized')
        match CHAR_TYPE[head]:
            case "dict":
                if not isinstance(segment.item, dict):
                    segment.item = {}
                raw_key, index = unwrap_quotes(key).split(SEP, 1)

                if raw_key:
                    dkey: int | str
                    if raw_key[0] not in CHAR_TYPE:
                        raise ValueError(
                            f'Key type character "{raw_key[0]}" unrecognized',
                        )
                    match CHAR_TYPE[raw_key[0]]:
                        case "str":
                            dkey = unwrap_quotes(raw_key)
                        case "int":
                            dkey = int(unwrap_quotes(raw_key))
                        case _ as dtype:
                            raise TypeError(
                                f'Expected str or int, got "{dtype}"',
                            )

                    if dkey not in segment.item:
                        segment.item[dkey] = Segment()
                    unwrap_key(segment.item[dkey], index, value)
            case "list":
                if not isinstance(segment.item, list):
                    segment.item = []
                indice_str, index = unwrap_quotes(key).split(SEP, 1)
                if indice_str:
                    indice = int(indice_str)
                    while indice >= len(segment.item):
                        segment.item.append(Segment())
                    unwrap_key(segment.item[indice], index, value)
            case "str":
                handle_map(segment, key, value, str)
            case "int":
                handle_map(segment, key, value, int)
            case "bool":
                handle_map(segment, key, value, bool)
            case "float":
                handle_map(segment, key, value, float)
            case "NoneType":
                handle_map(segment, key, value, lambda x: None)
            case _ as dtype:
                raise TypeError(
                    f'Expected type {combine_end(TYPE_CHAR, "or")}, got "{dtype}"',
                )

    data = Segment()
    for key, value in zip(keys, values, strict=True):
        unwrap_key(data, key, value)
    return data.unwrap()


if __name__ == "__main__":
    print(f"{__title__}\nProgrammed by {__author__}.\n")
