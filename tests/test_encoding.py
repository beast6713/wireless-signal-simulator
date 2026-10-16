"""Unit tests for text-to-binary and binary-to-text encoding module.

Phase 2: Binary Data Conversion
Academic Mini-Project | Software-Based Wireless Communication Simulator
"""

import unittest
from src.encoding import text_to_bits, bits_to_text, format_bits_for_display


class TestEncoding(unittest.TestCase):
    """Test suite for UTF-8 text encoding and decoding routines."""

    def test_single_character_a_to_bits(self):
        """Test conversion of single character 'A' (ASCII 65, 0x41) into 8 bits."""
        expected = [0, 1, 0, 0, 0, 0, 0, 1]
        result = text_to_bits("A")
        self.assertEqual(result, expected)
        self.assertEqual(len(result), 8)

    def test_hello_to_bits(self):
        """Test conversion of 'Hello' into bits (5 bytes * 8 = 40 bits)."""
        bits = text_to_bits("Hello")
        self.assertEqual(len(bits), 40)
        # Verify first byte 'H' (ASCII 72 = 0b01001000)
        self.assertEqual(bits[:8], [0, 1, 0, 0, 1, 0, 0, 0])
        # Verify second byte 'e' (ASCII 101 = 0b01100101)
        self.assertEqual(bits[8:16], [0, 1, 1, 0, 0, 1, 0, 1])

    def test_round_trip_ordinary_english(self):
        """Test round-trip conversion for standard English sentences."""
        original = "The quick brown fox jumps over the lazy dog."
        bits = text_to_bits(original)
        recovered = bits_to_text(bits)
        self.assertEqual(recovered, original)

    def test_spaces_and_punctuation_preservation(self):
        """Test preservation of whitespace, tabs, and punctuation symbols."""
        original = "Special symbols: !@#$%^&*()_+-=[]{};':\",.<>/?\t \n"
        bits = text_to_bits(original)
        recovered = bits_to_text(bits)
        self.assertEqual(recovered, original)

    def test_unicode_and_multilingual_support(self):
        """Test round-trip support for multi-byte UTF-8 characters (accents, Japanese, Cyrillic, emoji)."""
        test_strings = [
            "café résumé naïve",
            "こんにちは世界",
            "Привет мир",
            "Wireless 📡 📶 Communication",
        ]
        for original in test_strings:
            with self.subTest(text=original):
                bits = text_to_bits(original)
                # Verify that length in bits is exactly len(bytes) * 8
                self.assertEqual(len(bits), len(original.encode("utf-8")) * 8)
                recovered = bits_to_text(bits)
                self.assertEqual(recovered, original)

    def test_empty_string_handling(self):
        """Test that empty string returns an empty list and empty list returns empty string."""
        self.assertEqual(text_to_bits(""), [])
        self.assertEqual(bits_to_text([]), "")

    def test_rejection_of_non_string_input(self):
        """Test that text_to_bits raises TypeError when input is not a string."""
        invalid_inputs = [123, None, ["A"], 45.67, b"bytes"]
        for item in invalid_inputs:
            with self.subTest(input=item):
                with self.assertRaises(TypeError):
                    text_to_bits(item)  # type: ignore

    def test_rejection_of_invalid_bit_values(self):
        """Test that bits_to_text rejects bit values other than integer 0 and 1."""
        invalid_bit_lists = [
            [0, 1, 0, 2, 0, 0, 0, 1],       # Contains 2
            [0, 1, 0, -1, 0, 0, 0, 1],      # Contains -1
            [0, 1, 0, "1", 0, 0, 0, 1],     # Contains string
            [0, 1, 0, True, 0, 0, 0, 1],    # Contains boolean True
            [0, 1, 0, None, 0, 0, 0, 1],    # Contains None
        ]
        for item in invalid_bit_lists:
            with self.subTest(bits=item):
                with self.assertRaises(ValueError):
                    bits_to_text(item)  # type: ignore

    def test_rejection_of_non_list_bits_input(self):
        """Test that bits_to_text raises TypeError when input is not a list."""
        with self.assertRaises(TypeError):
            bits_to_text("01000001")  # type: ignore

    def test_rejection_of_incomplete_bytes(self):
        """Test that bits_to_text rejects bit lengths that are not multiples of 8."""
        incomplete_lengths = [1, 7, 9, 15, 23]
        for length in incomplete_lengths:
            with self.subTest(length=length):
                bits = [1] * length
                with self.assertRaises(ValueError):
                    bits_to_text(bits)

    def test_rejection_of_invalid_utf8_sequence(self):
        """Test that bits_to_text raises UnicodeDecodeError for invalid UTF-8 byte sequences."""
        # Byte 0xFF (255) is never valid in UTF-8
        invalid_byte_bits = [1, 1, 1, 1, 1, 1, 1, 1]
        with self.assertRaises(UnicodeDecodeError):
            bits_to_text(invalid_byte_bits)

        # Single continuation byte 0x80 (10000000) without a leading byte is invalid UTF-8
        invalid_continuation = [1, 0, 0, 0, 0, 0, 0, 0]
        with self.assertRaises(UnicodeDecodeError):
            bits_to_text(invalid_continuation)

    def test_format_bits_for_display(self):
        """Test formatting of bits into space-separated 8-bit groups."""
        bits = [0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1, 0]  # 'A', 'B'
        formatted = format_bits_for_display(bits)
        self.assertEqual(formatted, "01000001 01000010")
        self.assertEqual(format_bits_for_display([]), "")


if __name__ == "__main__":
    unittest.main()
