from pathlib import Path

from tgb_pipeline.images.download import download_image_asset
from tgb_pipeline.models import ImageAsset

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde"
    b"\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xe2$\xb5"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


class MockResponse:
    def __init__(self, content: bytes, content_type: str = "image/png") -> None:
        self.content = content
        self.headers = {"Content-Type": content_type}

    def raise_for_status(self) -> None:
        return None


class MockSession:
    def __init__(self, response: MockResponse | None = None, error: Exception | None = None) -> None:
        self.response = response
        self.error = error
        self.calls = 0

    def get(self, url: str, timeout: float):
        self.calls += 1
        if self.error:
            raise self.error
        return self.response


def make_image() -> ImageAsset:
    return ImageAsset(
        image_id="img-1",
        article_id="a1",
        source_url="https://example.test/image.png",
        page_url="https://example.test/page",
        source_type="article_body",
    )


def test_download_image_asset_populates_local_metadata(tmp_path: Path) -> None:
    updated = download_image_asset(
        make_image(),
        image_root=tmp_path,
        session=MockSession(response=MockResponse(PNG_BYTES)),
    )

    assert updated.local_path is not None
    assert Path(updated.local_path).is_file()
    assert updated.sha256 is not None
    assert updated.mime_type == "image/png"
    assert updated.width == 1
    assert updated.height == 1


def test_download_image_asset_records_error(tmp_path: Path) -> None:
    updated = download_image_asset(
        make_image(),
        image_root=tmp_path,
        session=MockSession(error=RuntimeError("boom")),
        max_retries=0,
    )

    assert updated.local_path is None
    assert "boom" in updated.raw["download_error"]


def test_download_image_asset_skips_existing(tmp_path: Path) -> None:
    first = download_image_asset(
        make_image(),
        image_root=tmp_path,
        session=MockSession(response=MockResponse(PNG_BYTES)),
    )
    session = MockSession(response=MockResponse(b"ignored"))

    second = download_image_asset(
        first,
        image_root=tmp_path,
        session=session,
        skip_existing=True,
    )

    assert session.calls == 0
    assert second.local_path == first.local_path
