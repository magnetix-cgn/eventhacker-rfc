"""Validate original image assets without extracting, rendering or rewriting them."""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import warnings
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, UnidentifiedImageError


MAX_FILE_BYTES = 32 * 1024 * 1024
MAX_PIXELS = 40_000_000
SUPPORTED_FORMATS = {"PNG": "image/png", "JPEG": "image/jpeg", "WEBP": "image/webp"}


class InvalidImage(ValueError):
    """The input cannot be accepted as an original supported image file."""


@dataclass(frozen=True)
class NativeImage:
    data: bytes = field(repr=False)
    format: str
    mime_type: str
    width: int
    height: int
    sha256: str

    def metadata(self) -> dict[str, str | int]:
        return {
            "format": self.format,
            "mime_type": self.mime_type,
            "width": self.width,
            "height": self.height,
            "byte_length": len(self.data),
            "sha256": self.sha256,
        }


def inspect_native_image(data: bytes) -> NativeImage:
    """Check the actual file format and retain the exact input bytes."""
    if not isinstance(data, bytes) or not data:
        raise InvalidImage("Provide a nonempty native PNG, JPEG or WebP file.")
    if len(data) > MAX_FILE_BYTES:
        raise InvalidImage("Image exceeds the 32 MiB input limit.")

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as image:
                image_format = image.format
                width, height = image.size
                if image_format not in SUPPORTED_FORMATS:
                    raise InvalidImage("Supported image formats are PNG, JPEG and WebP.")
                if width < 1 or height < 1 or width * height > MAX_PIXELS:
                    raise InvalidImage("Image exceeds the 40 megapixel limit.")
                image.verify()
            with Image.open(io.BytesIO(data)) as image:
                image.load()
    except InvalidImage:
        raise
    except (UnidentifiedImageError, OSError, ValueError, SyntaxError,
            Image.DecompressionBombError, Image.DecompressionBombWarning) as error:
        raise InvalidImage("Input is not a valid, complete supported image file.") from error

    return NativeImage(data, image_format, SUPPORTED_FORMATS[image_format],
                       width, height, hashlib.sha256(data).hexdigest())


def read_native_image(path: Path) -> NativeImage:
    """Read with a fixed bound rather than loading an unlimited input."""
    with path.open("rb") as handle:
        return inspect_native_image(handle.read(MAX_FILE_BYTES + 1))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("image", type=Path)
    args = parser.parse_args()
    try:
        asset = read_native_image(args.image)
    except (InvalidImage, OSError) as error:
        message = str(error) if isinstance(error, InvalidImage) else "Cannot read input image."
        print(json.dumps({"ok": False, "uploaded": False, "error": message}))
        return 1
    print(json.dumps({"ok": True, "uploaded": False, "image": asset.metadata()}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
