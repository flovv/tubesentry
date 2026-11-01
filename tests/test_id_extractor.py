from __future__ import annotations

from tubesentry.io.ingestor import extract_youtube_identifiers


def test_direct_channel_id() -> None:
    ch_id, handle = extract_youtube_identifiers("UCbCmjCuTUZos6Inko4u57UQ")
    assert ch_id == "UCbCmjCuTUZos6Inko4u57UQ"
    assert handle is None


def test_standard_channel_url() -> None:
    ch_id, handle = extract_youtube_identifiers("https://www.youtube.com/channel/UCX6OQ3DkcsbYNE6H8uQQuVA")
    assert ch_id == "UCX6OQ3DkcsbYNE6H8uQQuVA"
    assert handle is None


def test_http_channel_url() -> None:
    ch_id, handle = extract_youtube_identifiers("http://youtube.com/channel/UCvlE5gTbOvjiolFlEm-c_Ow")
    assert ch_id == "UCvlE5gTbOvjiolFlEm-c_Ow"
    assert handle is None


def test_channel_handle() -> None:
    ch_id, handle = extract_youtube_identifiers("https://www.youtube.com/@CoComelon")
    assert ch_id is None
    assert handle == "@CoComelon"


def test_bare_handle() -> None:
    ch_id, handle = extract_youtube_identifiers("@LofiGirlOfficial")
    assert ch_id is None
    assert handle == "@LofiGirlOfficial"


def test_watch_video_url() -> None:
    ch_id, vid = extract_youtube_identifiers("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    assert ch_id is None
    assert vid == "dQw4w9WgXcQ"


def test_youtu_be_shortlink() -> None:
    ch_id, vid = extract_youtube_identifiers("https://youtu.be/9bZkp7q19f0")
    assert ch_id is None
    assert vid == "9bZkp7q19f0"


def test_invalid_or_website_placement() -> None:
    ch_id, extra = extract_youtube_identifiers("https://nytimes.com/tech")
    assert ch_id is None
    assert extra is None


def test_none_or_empty() -> None:
    assert extract_youtube_identifiers("") == (None, None)
    assert extract_youtube_identifiers(None) == (None, None)  # type: ignore[arg-type]
