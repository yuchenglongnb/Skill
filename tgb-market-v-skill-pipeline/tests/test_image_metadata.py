from pathlib import Path

from tgb_pipeline.images.metadata import (
    compute_file_sha256,
    detect_mime_type,
    is_probably_noise_image,
    read_image_size,
)
from tgb_pipeline.models import ImageAsset

PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR"
    b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
    b"\x90wS\xde"
    b"\x00\x00\x00\x0cIDAT\x08\xd7c\xf8\xff\xff?\x00\x05\xfe\x02\xfeA\xe2$\xb5"
    b"\x00\x00\x00\x00IEND\xaeB`\x82"
)


def test_image_metadata_helpers(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    image_path.write_bytes(PNG_BYTES)

    assert len(compute_file_sha256(image_path)) == 64
    assert detect_mime_type(image_path) == "image/png"
    assert read_image_size(image_path) == (1, 1)


def test_noise_image_heuristics() -> None:
    image = ImageAsset(
        image_id="img-1",
        article_id="a1",
        source_url="https://example.test/avatar_icon.png",
        page_url="https://example.test/page",
        source_type="comment",
        width=60,
        height=60,
    )

    assert is_probably_noise_image(image) is True
