from sitebooker.services.crawler import _normalize_url, _same_domain


def test_normalize_url_removes_fragment() -> None:
    url = _normalize_url("https://example.com/docs/", "page#section")
    assert url == "https://example.com/docs/page"


def test_same_domain() -> None:
    assert _same_domain("https://example.com/a", "https://example.com/b")
    assert not _same_domain("https://example.com/a", "https://other.com/b")
