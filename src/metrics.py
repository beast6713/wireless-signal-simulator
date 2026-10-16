"""Performance metrics module for digital communication analysis.

Phase 6: Performance Analysis: BER and Accuracy
Academic Mini-Project | Software-Based Wireless Communication Simulator

This module provides tools to quantify communication quality by comparing
transmitted and received binary bitstreams:
- count_bit_errors: Counts bit discrepancies
- calculate_ber: Computes Bit Error Rate (BER)
- calculate_accuracy: Computes percentage accuracy
- analyze_transmission: Returns a comprehensive performance summary dictionary
"""

from typing import Any, Dict, List, Union
import numpy as np


def _validate_bit_sequence(seq: Any, name: str = "Bit sequence") -> List[int]:
    """Validate and sanitize a binary sequence.

    Args:
        seq: 1D sequence (list, tuple, np.ndarray) of binary bits (0 or 1).
        name: Name of the parameter for error reporting.

    Returns:
        List[int]: Validated list of integer bits (0 or 1).

    Raises:
        TypeError: If seq is a non-sequence, contains booleans, or non-integer elements.
        ValueError: If seq is multidimensional, contains NaN/Inf, or values other than 0 and 1.
    """
    if not isinstance(seq, (list, tuple, np.ndarray)):
        raise TypeError(
            f"{name} must be a list, tuple, or 1D np.ndarray, got {type(seq).__name__}."
        )

    if isinstance(seq, np.ndarray):
        if seq.ndim != 1:
            raise ValueError(
                f"{name} must be 1-dimensional, got {seq.ndim} dimensions."
            )

    cleaned: List[int] = []
    for idx, bit in enumerate(seq):
        # Explicitly reject Python booleans which inherit from int
        if isinstance(bit, (bool, np.bool_)):
            raise TypeError(
                f"Invalid bit in {name} at index {idx}: boolean values (True/False) are not allowed. "
                "Use integer 0 or 1."
            )
        if not isinstance(bit, (int, np.integer)):
            raise TypeError(
                f"Invalid bit in {name} at index {idx}: expected integer, got {type(bit).__name__}."
            )
        val = int(bit)
        if val not in (0, 1):
            raise ValueError(
                f"Invalid bit value in {name} at index {idx}: expected 0 or 1, got {bit!r}."
            )
        cleaned.append(val)

    return cleaned


def count_bit_errors(
    transmitted_bits: Any,
    received_bits: Any,
) -> int:
    """Count the number of bit disagreements between transmitted and received sequences.

    Args:
        transmitted_bits: Sequence of transmitted integer bits (0 or 1).
        received_bits: Sequence of received integer bits (0 or 1).

    Returns:
        int: Number of positions where transmitted_bits[i] != received_bits[i].
            Returns 0 if both sequences are empty.

    Raises:
        TypeError: If inputs are invalid types or contain booleans / non-integers.
        ValueError: If sequences have unequal lengths or invalid bit values.

    Examples:
        >>> count_bit_errors([1, 0, 1, 1, 0, 1], [1, 0, 0, 1, 0, 1])
        1
        >>> count_bit_errors([], [])
        0
    """
    tx = _validate_bit_sequence(transmitted_bits, "transmitted_bits")
    rx = _validate_bit_sequence(received_bits, "received_bits")

    if len(tx) != len(rx):
        raise ValueError(
            f"Transmitted bit count ({len(tx)}) does not match received bit count ({len(rx)}). "
            "Sequences must have equal length to evaluate bit errors."
        )

    if len(tx) == 0:
        return 0

    return int(np.sum(np.array(tx) != np.array(rx)))


def calculate_ber(
    transmitted_bits: Any,
    received_bits: Any,
) -> float:
    """Calculate the Bit Error Rate (BER) between transmitted and received bitstreams.

    Mathematical Model:
        BER = Number of bit errors / Total transmitted bits

    Empty Sequence Policy:
        For two empty sequences (length 0), returns 0.0, representing zero
        observed errors over a null transmission.

    Args:
        transmitted_bits: Sequence of transmitted integer bits (0 or 1).
        received_bits: Sequence of received integer bits (0 or 1).

    Returns:
        float: Bit Error Rate in the range [0.0, 1.0].

    Raises:
        TypeError: If inputs contain invalid types.
        ValueError: If sequence lengths do not match or contain invalid bit values.

    Examples:
        >>> calculate_ber([1, 0, 1, 1], [1, 0, 0, 1])
        0.25
    """
    tx = _validate_bit_sequence(transmitted_bits, "transmitted_bits")
    rx = _validate_bit_sequence(received_bits, "received_bits")

    if len(tx) != len(rx):
        raise ValueError(
            f"Transmitted bit count ({len(tx)}) does not match received bit count ({len(rx)})."
        )

    if len(tx) == 0:
        return 0.0

    errors = count_bit_errors(tx, rx)
    return float(errors / len(tx))


def calculate_accuracy(
    transmitted_bits: Any,
    received_bits: Any,
) -> float:
    """Calculate bit transmission accuracy as a percentage.

    Mathematical Model:
        Accuracy (%) = (1.0 - BER) * 100.0

    Empty Sequence Policy:
        For two empty sequences, returns 100.0%, consistent with BER = 0.0.

    Args:
        transmitted_bits: Sequence of transmitted integer bits (0 or 1).
        received_bits: Sequence of received integer bits (0 or 1).

    Returns:
        float: Accuracy percentage in the range [0.0, 100.0].

    Raises:
        TypeError, ValueError: If inputs are invalid or lengths do not match.

    Examples:
        >>> calculate_accuracy([1, 0, 1, 1], [1, 0, 0, 1])
        75.0
    """
    ber = calculate_ber(transmitted_bits, received_bits)
    return float((1.0 - ber) * 100.0)


def analyze_transmission(
    transmitted_bits: Any,
    received_bits: Any,
) -> Dict[str, Union[int, float]]:
    """Generate a comprehensive metrics summary of the transmission pipeline.

    Args:
        transmitted_bits: Sequence of transmitted integer bits (0 or 1).
        received_bits: Sequence of received integer bits (0 or 1).

    Returns:
        Dict with keys:
            - 'total_bits' (int): Total number of transmitted bits.
            - 'recovered_bits' (int): Total number of recovered bits.
            - 'bit_errors' (int): Number of bit discrepancies.
            - 'ber' (float): Bit Error Rate [0.0, 1.0].
            - 'accuracy_percent' (float): Transmission accuracy percentage [0.0, 100.0].

    Raises:
        TypeError, ValueError: If sequences are invalid or lengths do not match.

    Examples:
        >>> summary = analyze_transmission([1, 0, 1, 1, 0, 1], [1, 0, 0, 1, 0, 1])
        >>> summary['bit_errors']
        1
        >>> round(summary['accuracy_percent'], 2)
        83.33
    """
    tx = _validate_bit_sequence(transmitted_bits, "transmitted_bits")
    rx = _validate_bit_sequence(received_bits, "received_bits")

    if len(tx) != len(rx):
        raise ValueError(
            f"Transmitted bits ({len(tx)}) and recovered bits ({len(rx)}) have unequal lengths. "
            "Cannot compute bit-by-bit error statistics."
        )

    errors = count_bit_errors(tx, rx)
    total = len(tx)
    ber = float(errors / total) if total > 0 else 0.0
    accuracy = float((1.0 - ber) * 100.0)

    return {
        "total_bits": total,
        "recovered_bits": len(rx),
        "bit_errors": errors,
        "ber": ber,
        "accuracy_percent": accuracy,
    }
