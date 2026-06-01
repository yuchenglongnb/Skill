"""Optional OCR support for downloaded image evidence."""

from __future__ import annotations

import importlib
from pathlib import Path

from tgb_pipeline.config import OCRConfig
from tgb_pipeline.images.metadata import is_probably_noise_image
from tgb_pipeline.models import ImageAsset, ImageOCR
from tgb_pipeline.storage import JSONLStore
from tgb_pipeline.utils.text_cleaning import clean_text


def run_ocr_for_image(
    image: ImageAsset,
    *,
    engine: str,
    languages: list[str],
    min_confidence: float | None,
    skip_if_engine_missing: bool = True,
) -> ImageOCR | None:
    if not image.local_path:
        return None
    backend = _load_backend(engine, skip_if_engine_missing)
    if backend is None:
        return None

    raw_result = backend(Path(image.local_path), languages=languages)
    blocks = _normalize_blocks(raw_result)
    raw_text = "\n".join(block["text"] for block in blocks if block["text"]).strip()
    confidence = None
    confidences = [block["confidence"] for block in blocks if block["confidence"] is not None]
    if confidences:
        confidence = sum(confidences) / len(confidences)

    raw = {"blocks": blocks}
    if min_confidence is not None and confidence is not None and confidence < min_confidence:
        raw["need_manual_review"] = True
    return ImageOCR(
        ocr_id=f"ocr-{image.image_id}-{engine}",
        image_id=image.image_id,
        engine=engine,
        languages=list(languages),
        raw_text=raw_text,
        normalized_text=clean_text(raw_text) if raw_text else "",
        confidence=confidence,
        raw=raw,
    )


def ocr_images(raw_dir: Path, processed_dir: Path, ocr_config: OCRConfig) -> tuple[int, int, int]:
    if not ocr_config.ocr.enabled:
        JSONLStore(processed_dir / "image_ocr.jsonl", ImageOCR, "ocr_id").rewrite_all([])
        return 0, 0, 0

    images_path = raw_dir / "images_downloaded.jsonl"
    if not images_path.exists():
        images_path = raw_dir / "images.jsonl"
    images = JSONLStore(images_path, ImageAsset, "image_id").read_all()
    output_store = JSONLStore(processed_dir / "image_ocr.jsonl", ImageOCR, "ocr_id")

    records: list[ImageOCR] = []
    ocr_count = 0
    skipped_count = 0
    failed_count = 0
    for image in images:
        local_path = Path(image.local_path) if image.local_path else None
        if local_path is None or not local_path.exists():
            skipped_count += 1
            continue
        if (
            image.raw.get("probably_noise_image")
            and not ocr_config.images.allow_noise_images_for_ocr
        ):
            skipped_count += 1
            continue
        try:
            record = run_ocr_for_image(
                image,
                engine=ocr_config.ocr.engine or "rapidocr",
                languages=ocr_config.ocr.languages,
                min_confidence=ocr_config.ocr.min_confidence,
                skip_if_engine_missing=ocr_config.ocr.skip_if_engine_missing,
            )
        except Exception:
            failed_count += 1
            continue
        if record is None:
            skipped_count += 1
            continue
        if not ocr_config.ocr.preserve_raw_text:
            record.raw_text = ""
        if not ocr_config.ocr.normalize_text:
            record.normalized_text = None
        ocr_count += 1
        records.append(record)
    output_store.rewrite_all(records)
    return ocr_count, skipped_count, failed_count


def _load_backend(engine: str, skip_if_engine_missing: bool):
    normalized = engine.casefold()
    if normalized != "rapidocr":
        raise ValueError(f"unsupported OCR engine: {engine}")
    try:
        module = importlib.import_module("rapidocr_onnxruntime")
    except ImportError as exc:
        if skip_if_engine_missing:
            return None
        raise RuntimeError(
            "rapidocr-onnxruntime is not installed; install with `python -m pip install -e \".[dev,ocr]\"`."
        ) from exc

    RapidOCR = getattr(module, "RapidOCR")

    def _backend(path: Path, *, languages: list[str]):
        engine_instance = RapidOCR()
        result, _ = engine_instance(str(path))
        return result or []

    return _backend


def _normalize_blocks(raw_result) -> list[dict[str, object]]:
    blocks: list[dict[str, object]] = []
    for item in raw_result or []:
        if isinstance(item, dict):
            blocks.append(
                {
                    "bbox": item.get("bbox"),
                    "text": str(item.get("text", "")),
                    "confidence": _coerce_confidence(item.get("confidence")),
                }
            )
            continue
        if isinstance(item, (list, tuple)) and len(item) >= 2:
            bbox = item[0]
            text_info = item[1]
            text = ""
            confidence = None
            if isinstance(text_info, (list, tuple)):
                if text_info:
                    text = str(text_info[0])
                if len(text_info) > 1:
                    confidence = _coerce_confidence(text_info[1])
            else:
                text = str(text_info)
            blocks.append({"bbox": bbox, "text": text, "confidence": confidence})
    return blocks


def _coerce_confidence(value) -> float | None:
    try:
        return float(value) if value is not None else None
    except (TypeError, ValueError):
        return None
