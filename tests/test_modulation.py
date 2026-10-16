"""Unit tests for digital modulation module.

Phase 3: Digital Signal Modulation
Academic Mini-Project | Software-Based Wireless Communication Simulator
"""

import unittest
import numpy as np
from src.modulation import (
    ask_modulate,
    fsk_modulate,
    bpsk_modulate,
    get_time_vector,
)


class TestModulation(unittest.TestCase):
    """Test suite for ASK, FSK, and BPSK modulation algorithms."""

    def setUp(self):
        """Set up test parameters matching project defaults."""
        self.fs = 10000.0       # 10 kHz
        self.fc = 1000.0        # 1 kHz
        self.f0 = 500.0         # 500 Hz
        self.f1 = 1500.0        # 1500 Hz
        self.tb = 0.01          # 10 ms per bit -> 100 samples/bit
        self.amplitude = 1.0
        self.samples_per_bit = int(round(self.fs * self.tb))  # 100

    def test_sample_counts(self):
        """Test that ASK, FSK, and BPSK produce exactly len(bits) * samples_per_bit samples."""
        bits = [1, 0, 1, 1, 0]
        expected_len = len(bits) * self.samples_per_bit  # 5 * 100 = 500

        sig_ask = ask_modulate(bits, self.fs, self.fc, self.tb, self.amplitude)
        sig_fsk = fsk_modulate(bits, self.fs, self.f0, self.f1, self.tb, self.amplitude)
        sig_bpsk = bpsk_modulate(bits, self.fs, self.fc, self.tb, self.amplitude)

        self.assertEqual(len(sig_ask), expected_len)
        self.assertEqual(len(sig_fsk), expected_len)
        self.assertEqual(len(sig_bpsk), expected_len)

    def test_ask_amplitudes(self):
        """Test that ASK produces zero amplitude for bit 0 and carrier for bit 1."""
        bits = [1, 0]
        sig_ask = ask_modulate(bits, self.fs, self.fc, self.tb, self.amplitude)

        bit1_samples = sig_ask[: self.samples_per_bit]
        bit0_samples = sig_ask[self.samples_per_bit :]

        # Bit 0 should be completely zero
        np.testing.assert_allclose(bit0_samples, 0.0, atol=1e-12)

        # Bit 1 should have peak amplitude close to self.amplitude (> 0.9 for 10 samples/cycle)
        self.assertGreater(float(np.max(bit1_samples)), 0.9)
        self.assertLessEqual(float(np.max(bit1_samples)), self.amplitude)

    def test_bpsk_opposite_phases(self):
        """Test that BPSK represents bit 0 and bit 1 with opposite carrier phases (pi shift)."""
        # Over the same time interval [0, Tb), bit 1 should be +sin(...) and bit 0 should be -sin(...)
        sig_1 = bpsk_modulate([1], self.fs, self.fc, self.tb, self.amplitude)
        sig_0 = bpsk_modulate([0], self.fs, self.fc, self.tb, self.amplitude)

        # sig_0 should be exactly -sig_1
        np.testing.assert_allclose(sig_0, -sig_1, atol=1e-12)

    def test_fsk_frequencies(self):
        """Test that FSK generates waveforms with the specified frequencies for bit 0 and bit 1."""
        # For bit 0: s(t) = A * sin(2 * pi * f0 * t)
        # For bit 1: s(t) = A * sin(2 * pi * f1 * t)
        t = get_time_vector(1, self.fs, self.tb)

        expected_bit0 = self.amplitude * np.sin(2.0 * np.pi * self.f0 * t)
        expected_bit1 = self.amplitude * np.sin(2.0 * np.pi * self.f1 * t)

        sig_0 = fsk_modulate([0], self.fs, self.f0, self.f1, self.tb, self.amplitude)
        sig_1 = fsk_modulate([1], self.fs, self.f0, self.f1, self.tb, self.amplitude)

        np.testing.assert_allclose(sig_0, expected_bit0, atol=1e-12)
        np.testing.assert_allclose(sig_1, expected_bit1, atol=1e-12)

    def test_empty_bit_sequence(self):
        """Test that empty sequences produce empty NumPy arrays."""
        for fn in (ask_modulate, fsk_modulate, bpsk_modulate):
            with self.subTest(fn=fn.__name__):
                res = fn([])
                self.assertIsInstance(res, np.ndarray)
                self.assertEqual(len(res), 0)

    def test_rejection_of_invalid_bit_values(self):
        """Test rejection of non-binary numbers and strings."""
        invalid_sequences = [
            [0, 1, 2],
            [0, -1, 1],
            [0, "1", 0],
            [0, 1.5, 0],
        ]
        for seq in invalid_sequences:
            for fn in (ask_modulate, fsk_modulate, bpsk_modulate):
                with self.subTest(fn=fn.__name__, seq=seq):
                    with self.assertRaises((ValueError, TypeError)):
                        fn(seq)

    def test_rejection_of_booleans(self):
        """Test that boolean values (True, False) are strictly rejected as bits."""
        bool_seq = [True, False, True]
        for fn in (ask_modulate, fsk_modulate, bpsk_modulate):
            with self.subTest(fn=fn.__name__):
                with self.assertRaises(TypeError):
                    fn(bool_seq)

    def test_rejection_of_multidimensional_arrays(self):
        """Test that 2D or 3D arrays are rejected."""
        array_2d = np.array([[0, 1], [1, 0]])
        for fn in (ask_modulate, fsk_modulate, bpsk_modulate):
            with self.subTest(fn=fn.__name__):
                with self.assertRaises(ValueError):
                    fn(array_2d)

    def test_rejection_of_invalid_frequencies(self):
        """Test that non-positive frequencies or frequencies >= Nyquist are rejected."""
        # Non-positive carrier frequency
        with self.assertRaises(ValueError):
            ask_modulate([1], self.fs, carrier_frequency=0.0)
        with self.assertRaises(ValueError):
            bpsk_modulate([1], self.fs, carrier_frequency=-100.0)

        # Carrier frequency >= Nyquist (fs / 2 = 5000 Hz)
        with self.assertRaises(ValueError):
            ask_modulate([1], self.fs, carrier_frequency=5000.0)
        with self.assertRaises(ValueError):
            ask_modulate([1], self.fs, carrier_frequency=6000.0)

        # FSK frequency checks
        with self.assertRaises(ValueError):
            fsk_modulate([0], self.fs, frequency_0=-50.0, frequency_1=1500.0)
        with self.assertRaises(ValueError):
            fsk_modulate([0], self.fs, frequency_0=500.0, frequency_1=5500.0)
        with self.assertRaises(ValueError):
            fsk_modulate([0], self.fs, frequency_0=1000.0, frequency_1=1000.0)

    def test_rejection_of_invalid_sampling_and_duration(self):
        """Test that non-positive sampling frequency or bit duration is rejected."""
        with self.assertRaises(ValueError):
            ask_modulate([1], sampling_frequency=-1000.0)
        with self.assertRaises(ValueError):
            ask_modulate([1], bit_duration=0.0)
        with self.assertRaises(ValueError):
            ask_modulate([1], amplitude=-1.0)

    def test_waveforms_finite(self):
        """Test that generated waveforms contain only finite numbers (no NaN or Inf)."""
        bits = [1, 0, 1, 0, 0, 1]
        for fn in (ask_modulate, fsk_modulate, bpsk_modulate):
            with self.subTest(fn=fn.__name__):
                wf = fn(bits)
                self.assertTrue(np.all(np.isfinite(wf)))

    def test_tuple_and_numpy_input_support(self):
        """Test that tuple and 1D NumPy array inputs are accepted."""
        tuple_bits = (1, 0, 1)
        np_bits = np.array([1, 0, 1], dtype=int)

        wf_tuple = ask_modulate(tuple_bits)
        wf_np = ask_modulate(np_bits)

        self.assertEqual(len(wf_tuple), 300)
        self.assertEqual(len(wf_np), 300)
        np.testing.assert_allclose(wf_tuple, wf_np)


if __name__ == "__main__":
    unittest.main()
