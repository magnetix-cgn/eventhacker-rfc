"""Offline checks for original-byte intake and invalid input rejection."""

import hashlib
import io
import unittest
from unittest.mock import patch

from PIL import Image

from native_images import InvalidImage, inspect_native_image


def image_bytes(image_format):
    output = io.BytesIO()
    Image.new("RGB", (37, 23), "blue").save(output, format=image_format)
    return output.getvalue()


class NativeImageTests(unittest.TestCase):
    def test_supported_original_files_keep_every_byte_and_dimension(self):
        for image_format in ["PNG", "JPEG", "WEBP"]:
            with self.subTest(image_format=image_format):
                data = image_bytes(image_format)
                asset = inspect_native_image(data)
                self.assertEqual(asset.data, data)
                self.assertEqual((asset.width, asset.height), (37, 23))
                self.assertEqual(asset.format, image_format)
                self.assertEqual(asset.sha256, hashlib.sha256(data).hexdigest())

    def test_html_wrapper_is_rejected_even_with_an_embedded_image(self):
        with self.assertRaises(InvalidImage):
            inspect_native_image(b'<!doctype html><img src="data:image/png;base64,AAAA">')

    def test_unsupported_native_format_is_rejected(self):
        with self.assertRaises(InvalidImage):
            inspect_native_image(image_bytes("BMP"))

    def test_truncated_and_empty_files_are_rejected(self):
        for data in [b"", image_bytes("PNG")[:40], image_bytes("JPEG")[:25]]:
            with self.subTest(data_length=len(data)), self.assertRaises(InvalidImage):
                inspect_native_image(data)

    def test_byte_limit_is_enforced_before_decoding(self):
        with patch("native_images.MAX_FILE_BYTES", 5), self.assertRaises(InvalidImage):
            inspect_native_image(b"abcdef")

    def test_pixel_limit_is_enforced(self):
        with patch("native_images.MAX_PIXELS", 10), self.assertRaises(InvalidImage):
            inspect_native_image(image_bytes("PNG"))


if __name__ == "__main__":
    unittest.main()
