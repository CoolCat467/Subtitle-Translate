from __future__ import annotations

import pytest

from subtitle_translate import extricate


def test_wrap_quotes() -> None:
    assert extricate.wrap_quotes("waffles") == '"waffles"'
    assert extricate.wrap_quotes("waffles", "xX") == "xXwafflesxX"
    assert extricate.wrap_quotes("text here", "<p>") == "<p>text here<p>"


def test_unwrap_quotes() -> None:
    assert extricate.unwrap_quotes('"tasty soup"', 1) == "tasty soup"


@pytest.mark.parametrize(
    "test_v",
    [
        {
            "cat": {
                3: "5",
                7: [4, 3, 3],
                4: [
                    "cat",
                    {"meep": "e", "a": 3, "": [235, "woe", [], None, {}]},
                ],
            },
            "meep": [1, 2, [2, 3, "4"]],
        },
        ["cat"],
        5,
        "cat",
        ["cat", "bean", {3: "mouse", "mouse": 4}, 17],
        [[[["cat", 0], 4], "8"], ["3", "nine", ["14"]]],
        {
            "success": True,
            "result": {
                "file_id": 1609,
                "publication_name": "Notepad+",
                "source_url": "https://raw.githubusercontent.com/kogtyvPl/numpade/main/main.lua",
                "path": "Main.lua",
                "version": 1.07,
                "user_name": "kogtyv",
                "whats_new": "Добавлены расширения файлов: .txt .num .ntxt .npd",
                "whats_new_version": 1.07,
                "category_id": 1,
                "license_id": 1,
                "timestamp": 1630854990,
                "initial_description": "Програма для редактирования текстовых файлов (.txt) идея: Bumer_32. приложение создал: kogtyv. Редактируй свои красивые тексты :)",
                "translated_description": "Програма для редактирования текстовых файлов (.txt) идея: Bumer_32. приложение создал: kogtyv. Редактируй свои красивые тексты :)",
                "icon_url": "https://raw.githubusercontent.com/kogtyvPl/numpade/main/Icon.pic",
                "average_rating": 3.0,
                "dependencies": [1610, 100, 1403, 1685, 1686, 1687, 1688],
                "dependencies_data": {
                    "100": {
                        "source_url": "https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/GUI.lua",
                        "path": "GUI.lua",
                        "publication_name": "GUI",
                        "category_id": 2,
                        "version": 1.83,
                    },
                    "73": {
                        "source_url": "https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Image.lua",
                        "path": "Image.lua",
                        "publication_name": "Image",
                        "category_id": 2,
                        "version": 1.18,
                    },
                    "92": {
                        "source_url": "https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Color.lua",
                        "path": "Color.lua",
                        "publication_name": "Color",
                        "category_id": 2,
                        "version": 1.14,
                    },
                    "1062": {
                        "source_url": "https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Bit32.lua",
                        "path": "Bit32.lua",
                        "publication_name": "Bit32",
                        "category_id": 2,
                        "version": 1.01,
                    },
                    "97": {
                        "source_url": "https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Screen.lua",
                        "path": "Screen.lua",
                        "publication_name": "Screen",
                        "category_id": 2,
                        "version": 1.21,
                    },
                    "1058": {
                        "source_url": "https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Paths.lua",
                        "path": "Paths.lua",
                        "publication_name": "Paths",
                        "category_id": 2,
                        "version": 1.04,
                    },
                    "1059": {
                        "source_url": "https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Text.lua",
                        "path": "Text.lua",
                        "publication_name": "Text",
                        "category_id": 2,
                        "version": 1.01,
                    },
                    "1060": {
                        "source_url": "https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Number.lua",
                        "path": "Number.lua",
                        "publication_name": "Number",
                        "category_id": 2,
                        "version": 1.01,
                    },
                    "1403": {
                        "source_url": "https://raw.githubusercontent.com/IgorTimofeev/MineOS/master/Libraries/Filesystem.lua",
                        "path": "Filesystem.lua",
                        "publication_name": "Filesystem",
                        "category_id": 2,
                        "version": 1.02,
                    },
                    "1610": {
                        "source_url": "https://raw.githubusercontent.com/kogtyvPl/numpade/main/Icon.pic",
                        "path": "Icon.pic",
                        "version": 1.07,
                    },
                    "1685": {
                        "source_url": "https://github.com/kogtyvPl/numpade/raw/main/Extensions%20files/num/Icon.pic",
                        "path": "Extensions/.num/Icon.pic",
                        "version": 1,
                    },
                    "1686": {
                        "source_url": "https://github.com/kogtyvPl/numpade/raw/main/Extensions%20files/txt/Icon.pic",
                        "path": "Extensions/.txt/Icon.pic",
                        "version": 1,
                    },
                    "1687": {
                        "source_url": "https://github.com/kogtyvPl/numpade/raw/main/Extensions%20files/npd/Icon.pic",
                        "path": "Extensions/.npd/Icon.pic",
                        "version": 1,
                    },
                    "1688": {
                        "source_url": "https://github.com/kogtyvPl/numpade/raw/main/Extensions%20files/ntxt/Icon.pic",
                        "path": "Extensions/.ntxt/Icon.pic",
                        "version": 1,
                    },
                },
                "all_dependencies": [
                    100,
                    73,
                    92,
                    1062,
                    97,
                    1058,
                    1059,
                    1060,
                    1403,
                    1610,
                    1685,
                    1686,
                    1687,
                    1688,
                ],
            },
        },
    ],
)
def test_take_apart_and_recombine(test_v: object) -> None:
    keys, values = extricate.dict_to_list(test_v)
    assert len(keys) == len(values)
    result = extricate.list_to_dict(keys, values)
    assert test_v == result
