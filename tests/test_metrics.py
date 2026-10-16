"""Unit tests for performance metrics module.

Phase 6: Performance Analysis: BER and Accuracy
Academic Mini-Project | Software-Based Wireless Communication Simulator
"""

import unittest
import numpy as np

from src.metrics import (
    analyze_transmission,
    calculate_accuracy,
    calculate_ber,
    count_bit_errors,
)


class TestMetrics(unittest.TestCase):
    """Test suite for Bit Error Rate (BER) and accuracy analysis functions."""

    def test_zero_errors_identical_sequences(self):
        """Test that identical sequences produce 0 bit errors."""
        bits = [1, 0, 1, 1, 0, 0, 1, 0]
        self.assertEqual(count_bit_errors(bits, bits), 0)

    def test_single_bit_error_count(self):
        """Test counting a single bit error."""
        tx = [1, 0, 1, 1, 0, 1]
        rx = [1, 0, 0, 1, 0, 1]  # Discrepancy at index 2
        self.assertEqual(count_bit_errors(tx, rx), 1)

    def test_multiple_bit_errors_count(self):
        """Test counting multiple bit errors."""
        tx = [1, 0, 1, 0, 1, 0]
        rx = [0, 1, 0, 1, 0, 1]  # All 6 bits inverted
        self.assertEqual(count_bit_errors(tx, rx), 6)

    def test_ber_zero_for_identical_sequences(self):
        """Test that BER is exactly 0.0 for identical sequences."""
        bits = [0, 1, 1, 0, 1, 0]
        self.assertEqual(calculate_ber(bits, bits), 0.0)

    def test_ber_calculation_known_sequence(self):
        """Test BER calculation for known values."""
        tx = [1, 0, 1, 1, 0, 1]  # 6 bits
        rx = [1, 0, 0, 1, 0, 1]  # 1 error
        expected_ber = 1.0 / 6.0
        self.assertAlmostEqual(calculate_ber(tx, rx), expected_ber, places=6)

    def test_accuracy_100_percent_identical_sequences(self):
        """Test that accuracy is 100.0% for error-free transmissions."""
        bits = [1, 1, 0, 0, 1]
        self.assertEqual(calculate_accuracy(bits, bits), 100.0)

    def test_accuracy_with_errors(self):
        """Test accuracy calculation for known error rate."""
        tx = [1, 0, 1, 1, 0, 1]  # 6 bits
        rx = [1, 0, 0, 1, 0, 1]  # 1 error -> 5/6 correct
        expected_accuracy = (5.0 / 6.0) * 100.0
        self.assertAlmostEqual(calculate_accuracy(tx, rx), expected_accuracy, places=5)

    def test_empty_sequences_documented_behavior(self):
        """Test that empty sequences return 0 errors, 0.0 BER, and 100.0% accuracy."""
        self.assertEqual(count_bit_errors([], []), 0)
        self.assertEqual(calculate_ber([], []), 0.0)
        self.assertEqual(calculate_accuracy([], []), 100.0)

    def test_rejection_of_unequal_sequence_lengths(self):
        """Test that sequences of unequal lengths raise ValueError."""
        tx = [1, 0, 1]
        rx = [1, 0, 1, 0]
        with self.assertRaises(ValueError):
            count_bit_errors(tx, rx)
        with self.assertRaises(ValueError):
            calculate_ber(tx, rx)
        with self.assertRaises(ValueError):
            calculate_accuracy(tx, rx)
        with self.assertRaises(ValueError):
            analyze_transmission(tx, rx)

    def test_rejection_of_invalid_bit_values(self):
        """Test rejection of non-binary numbers (e.g. 2, -1, 1.5)."""
        invalid_bits = [1, 0, 2]
        valid_bits = [1, 0, 1]
        with self.assertRaises(ValueError):
            count_bit_errors(invalid_bits, valid_bits)
        with self.assertRaises(ValueError):
            count_bit_errors(valid_bits, [-1, 0, 1])

    def test_rejection_of_booleans(self):
        """Test that booleans (True/False) are strictly rejected as bits."""
        bool_bits = [True, False, True]
        valid_bits = [1, 0, 1]
        with self.assertRaises(TypeError):
            count_bit_errors(bool_bits, valid_bits)

    def test_rejection_of_multidimensional_inputs(self):
        """Test that 2D or 3D arrays are rejected."""
        array_2d = np.array([[1, 0], [0, 1]])
        valid_bits = [1, 0, 0, 1]
        with self.assertRaises(ValueError):
            count_bit_errors(array_2d, valid_bits)

    def test_rejection_of_nan_inf_strings(self):
        """Test rejection of NaN, Inf, and strings."""
        with self.assertRaises((TypeError, ValueError)):
            count_bit_errors([1, "0", 1], [1, 0, 1])
        with self.assertRaises((TypeError, ValueError)):
            count_bit_errors([1, float("nan"), 1], [1, 0, 1])

    def test_analyze_transmission_summary_keys_and_values(self):
        """Test that analyze_transmission returns the full summary dictionary."""
        tx = [1, 0, 1, 1, 0, 1]
        rx = [1, 0, 0, 1, 0, 1]
        summary = analyze_transmission(tx, rx)

        expected_keys = {"total_bits", "recovered_bits", "bit_errors", "ber", "accuracy_percent"}
        self.assertEqual(set(summary.keys()), expected_keys)
        self.assertEqual(summary["total_bits"], 6)
        self.assertEqual(summary["recovered_bits"], 6)
        self.assertEqual(summary["bit_errors"], 1)
        self.assertAlmostEqual(summary["ber"], 1.0 / 6.0, places=6)
        self.assertAlmostEqual(summary["accuracy_percent"], (5.0 / 6.0) * 100.0, places=5)

    def test_tuple_and_numpy_input_support(self):
        """Test that tuples and 1D NumPy arrays are accepted."""
        tx_tuple = (1, 0, 1)
        rx_np = np.array([1, 1, 1], dtype=int)
        self.assertEqual(count_bit_errors(tx_tuple, rx_np), 1)


if __name__ == "__main__":
    unittest.main()
