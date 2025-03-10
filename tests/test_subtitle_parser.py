from io import StringIO

import pytest

from subtitle_translate.subtitle_parser import (
    Subtitle,
    convert_text,
    duration_to_srt_fragment,
    duration_to_vtt_fragment,
    modify_subtitles,
    parse_subtitle_text_srt,
    parse_subtitle_text_vtt,
    parse_time_fragment_srt,
    parse_time_fragment_vtt,
    parse_timestamp_srt,
    parse_timestamp_vtt,
    time_to_timestamp_srt,
    time_to_timestamp_vtt,
    write_subtitles_srt,
    write_subtitles_vtt,
)


def test_parse_timestamp_srt() -> None:
    assert parse_timestamp_srt("00:01:30,500") == 90500
    assert parse_timestamp_srt("01:00:00,000") == 3600000
    assert parse_timestamp_srt("00:00:00,000") == 0


def test_parse_timestamp_vtt() -> None:
    assert parse_timestamp_vtt("00:01:30.500") == 90500
    assert parse_timestamp_vtt("01:00:00.000") == 3600000
    assert parse_timestamp_vtt("00:00:00.000") == 0


def test_time_to_timestamp_srt() -> None:
    assert time_to_timestamp_srt(90050) == "00:01:30,050"
    assert time_to_timestamp_srt(3600000) == "01:00:00,000"
    assert time_to_timestamp_srt(0) == "00:00:00,000"


def test_time_to_timestamp_vtt() -> None:
    assert time_to_timestamp_vtt(90050) == "00:01:30.050"
    assert time_to_timestamp_vtt(3600000) == "01:00:00.000"
    assert time_to_timestamp_vtt(0) == "00:00:00.000"


def test_parse_time_fragment_srt() -> None:
    assert parse_time_fragment_srt("00:00:00,000 --> 00:00:05,000") == (
        0,
        5000,
    )
    assert parse_time_fragment_srt("00:01:00,000 --> 00:01:05,000") == (
        60000,
        65000,
    )


def test_parse_time_fragment_vtt() -> None:
    assert parse_time_fragment_vtt("00:00:00.000 --> 00:00:05.000") == (
        0,
        5000,
    )
    assert parse_time_fragment_vtt("00:01:00.000 --> 00:01:05.000") == (
        60000,
        65000,
    )


def test_duration_to_srt_fragment() -> None:
    assert (
        duration_to_srt_fragment((0, 5000)) == "00:00:00,000 --> 00:00:05,000"
    )
    assert (
        duration_to_srt_fragment((60000, 65000))
        == "00:01:00,000 --> 00:01:05,000"
    )


def test_duration_to_vtt_fragment() -> None:
    assert (
        duration_to_vtt_fragment((0, 5000)) == "00:00:00.000 --> 00:00:05.000"
    )
    assert (
        duration_to_vtt_fragment((60000, 65000))
        == "00:01:00.000 --> 00:01:05.000"
    )


def test_parse_subtitle_text_srt() -> None:
    subtitle_data = StringIO(
        """1
00:00:00,000 --> 00:00:05,000
<b>This is a subtitle.</b>

2
00:00:05,000 --> 00:00:10,000
<p>Another subtitle.</p>

""",
    )
    expected = {
        1: Subtitle((0, 5000), "<b>This is a subtitle.</b>"),
        2: Subtitle((5000, 10000), "<p>Another subtitle.</p>"),
    }
    result = dict(parse_subtitle_text_srt(subtitle_data))
    assert result == expected


def test_parse_subtitle_text_srt_multiline() -> None:
    subtitle_data = StringIO(
        """1
00:00:00,000 --> 00:00:05,000
<b>This is a subtitle.</b>

2
00:00:05,000 --> 00:00:10,000
<p>Another subtitle.
Linebreak content.</p>

""",
    )
    expected = {
        1: Subtitle((0, 5000), "<b>This is a subtitle.</b>"),
        2: Subtitle(
            (5000, 10000),
            "<p>Another subtitle.\nLinebreak content.</p>",
        ),
    }
    result = dict(parse_subtitle_text_srt(subtitle_data))
    assert result == expected


def test_parse_subtitle_text_srt_read_failure() -> None:
    subtitle_data = StringIO(
        """1
00:00:00,000 --> 00:00:05,000
<b>This is a subtitle.</b>""",
    )
    with pytest.raises(AssertionError):
        dict(parse_subtitle_text_srt(subtitle_data))


def test_parse_subtitle_text_vtt() -> None:
    subtitle_data = StringIO(
        """00:00:00.000 --> 00:00:05.000
This is a subtitle.

00:00:05.000 --> 00:00:10.000
Another subtitle.

""",
    )
    expected = (
        Subtitle((0, 5000), "This is a subtitle."),
        Subtitle((5000, 10000), "Another subtitle."),
    )
    result = tuple(parse_subtitle_text_vtt(subtitle_data))
    assert result == expected


def test_write_subtitles_srt():
    subs = {
        1: Subtitle((0, 5000), "<b>This is a subtitle.</b>"),
        2: Subtitle((5000, 10000), "<p>Another subtitle.</p>"),
    }
    output = StringIO()
    write_subtitles_srt(output, subs)
    expected_output = (
        "1\n00:00:00,000 --> 00:00:05,000\n<b>This is a subtitle.</b>\n\n"
        "2\n00:00:05,000 --> 00:00:10,000\n<p>Another subtitle.</p>\n\n"
    )
    assert output.getvalue() == expected_output


def test_write_subtitles_vtt():
    subs = (
        Subtitle((0, 5000), "This is a subtitle."),
        Subtitle((5000, 10000), "Another subtitle."),
    )
    output = StringIO()
    write_subtitles_vtt(output, subs)
    expected_output = (
        "00:00:00.000 --> 00:00:05.000\nThis is a subtitle.\n\n"
        "00:00:05.000 --> 00:00:10.000\nAnother subtitle.\n\n"
    )
    assert output.getvalue() == expected_output


def test_convert_text() -> None:
    subs = {
        1: Subtitle((0, 5000), "<b>This is a subtitle.</b>"),
        2: Subtitle((5000, 10000), "<p>Another subtitle.</p>"),
    }
    gen = ((1, subs[1]), (2, subs[2]))
    expected_subs = {
        1: Subtitle((0, 5000), "<b>This is a subtitle.</b>"),
        2: Subtitle((5000, 10000), "<p>Another subtitle.</p>"),
    }
    expected_texts = {
        1: ("This is a subtitle.",),
        2: ("Another subtitle.",),
    }
    result_subs, result_texts = convert_text(gen)
    assert result_subs == expected_subs
    assert result_texts == expected_texts


def test_modify_subtitles() -> None:
    subs = {
        1: Subtitle((0, 5000), "<b>This is a subtitle.</b>"),
        2: Subtitle((5000, 10000), "<p>Another subtitle.</p>"),
    }
    new_texts = {
        1: ("Modified subtitle.",),
        2: ("Another modified subtitle.",),
    }
    modified_subs = modify_subtitles(subs, new_texts)
    assert modified_subs[1].html == "<b>Modified subtitle.</b>"
    assert modified_subs[2].html == "<p>Another modified subtitle.</p>"
