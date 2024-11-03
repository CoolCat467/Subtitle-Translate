import subtitle_translate


def test_attributes() -> None:
    assert isinstance(subtitle_translate.__author__, str)
    assert isinstance(subtitle_translate.__license__, str)
    assert isinstance(subtitle_translate.__version__, str)
    assert callable(subtitle_translate.cli_run)
