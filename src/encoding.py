"""Text-to-binary and binary-to-text encoding module.

Phase 2: Binary Data Conversion
Academic Mini-Project | Software-Based Wireless Communication Simulator

This module provides functions to convert text strings to UTF-8 binary bit arrays
and decode binary bit arrays back to text strings.
"""

from typing import List


def text_to_bits(text: str) -> List[int]:
    """Convert a text string into a list of UTF-8 bits (0s and 1s).

    Each character in the string is encoded into UTF-8 bytes, and each byte is
    converted into exactly 8 bits in most-significant-bit (MSB) first order,
    preserving all leading zeros.

    Args:
        text (str): The text string to convert. Can include English characters,
            punctuation, spaces, numbers, and Unicode/accented characters.

    Returns:
        List[int]: A list of integers (0 and 1) representing the UTF-8 bitstream.
            Returns an empty list if the input string is empty.

    Raises:
        TypeError: If the input is not a string.

    Examples:
        >>> text_to_bits("A")
        [0, 1, 0, 0, 0, 0, 0, 1]
        >>> text_to_bits("")
        []
    """
    if not isinstance(text, str):
        raise TypeError(f"Input text must be a str, got {type(text).__name__}")

    if not text:
        return []

    # Encode string to UTF-8 byte sequence
    utf8_bytes = text.encode("utf-8")

    # Convert each byte to 8 bits, most-significant bit (MSB) first
    bits: List[int] = []
    for byte in utf8_bytes:
        for shift in range(7, -1, -1):
            bits.append((byte >> shift) & 1)

    return bits


def bits_to_text(bits: List[int]) -> str:
    """Convert a list of UTF-8 bits (0s and 1s) back into a text string.

    Validates that the input contains only integer 0 and 1 values and that its
    length is an exact multiple of 8 bits. Groups bits into bytes (MSB first)
    and decodes using UTF-8.

    Args:
        bits (List[int]): A list of integer bits (0 and 1). Length must be a
            multiple of 8.

    Returns:
        str: The recovered UTF-8 text string. Returns an empty string if the
            input list is empty.

    Raises:
        TypeError: If the input is not a list.
        ValueError: If any element in the list is not an integer 0 or 1, or if
            the total number of bits is not divisible by 8.
        UnicodeDecodeError: If the recovered bytes do not form a valid UTF-8 sequence.

    Examples:
        >>> bits_to_text([0, 1, 0, 0, 0, 0, 0, 1])
        'A'
        >>> bits_to_text([])
        ''
    """
    if not isinstance(bits, list):
        raise TypeError(f"Input bits must be a list, got {type(bits).__name__}")

    if not bits:
        return ""

    # Validate bit values (strictly 0 or 1, not booleans or other types/numbers)
    for index, bit in enumerate(bits):
        if type(bit) is not int or bit not in (0, 1):
            raise ValueError(
                f"Invalid bit at index {index}: expected integer 0 or 1, got {bit!r} ({type(bit).__name__})"
            )

    # Validate byte boundary (multiple of 8)
    if len(bits) % 8 != 0:
        raise ValueError(
            f"Bit sequence length ({len(bits)}) is not divisible by 8. Incomplete byte received."
        )

    # Reconstruct bytes from 8-bit groups (MSB first)
    byte_array = bytearray()
    for i in range(0, len(bits), 8):
        byte_val = 0
        for bit in bits[i : i + 8]:
            byte_val = (byte_val << 1) | bit
        byte_array.append(byte_val)

    # Decode bytes as UTF-8 (raises UnicodeDecodeError on invalid sequences)
    return byte_array.decode("utf-8")


def format_bits_for_display(bits: List[int], group_size: int = 8) -> str:
    """Format a list of bits into space-separated groups of 8 for readable display.

    Args:
        bits (List[int]): List of bits (0 and 1).
        group_size (int): Number of bits per group (default is 8).

    Returns:
        str: Space-separated bit groups, e.g. "01001000 01100101".
    """
    if not bits:
        return ""

    bit_str = "".join(str(b) for b in bits)
    groups = [bit_str[i : i + group_size] for i in range(0, len(bit_str), group_size)]
    return " ".join(groups)
