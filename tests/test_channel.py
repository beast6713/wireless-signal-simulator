"""Unit tests for wireless channel noise simulation module.

Phase 4: Wireless Channel Simulation
Academic Mini-Project | Software-Based Wireless Communication Simulator
"""

import unittest
import numpy as np
from src.channel import add_awgn


class TestChannel(unittest.TestCase):
    """Test suite for Additive White Gaussian Noise (AWGN) channel model."""

    def setUp(self):
        """Set up standard sinusoidal test signal."""
        self.fs = 10000.0
        self.fc = 1000.0
        self.duration = 0.1  # 0.1 seconds -> 1000 samples
        self.t = np.arange(int(self.fs * self.duration), dtype=float) / self.fs
        self.clean_signal = np.sin(2.0 * np.pi * self.fc * self.t)

    def test_output_length_equals_input_length(self):
        """Test that received noisy signal has the exact same length as transmitted signal."""
        for snr in [0, 10, 20, 30]:
            with self.subTest(snr=snr):
                noisy = add_awgn(self.clean_signal, snr_db=snr)
                self.assertEqual(len(noisy), len(self.clean_signal))
                self.assertIsInstance(noisy, np.ndarray)

    def test_input_waveform_not_modified(self):
        """Test that the input signal array is not modified in-place."""
        original_copy = self.clean_signal.copy()
        _ = add_awgn(self.clean_signal, snr_db=15, seed=42)
        np.testing.assert_array_equal(self.clean_signal, original_copy)

    def test_empty_input_returns_empty_array(self):
        """Test that an empty input array returns an empty numpy array."""
        empty_res = add_awgn([], snr_db=20)
        self.assertIsInstance(empty_res, np.ndarray)
        self.assertEqual(len(empty_res), 0)

    def test_zero_valued_signal_remains_zero(self):
        """Test that an all-zero signal remains zero (zero power has undefined SNR)."""
        zeros = np.zeros(200, dtype=float)
        result = add_awgn(zeros, snr_db=15)
        np.testing.assert_array_equal(result, zeros)

    def test_fixed_seed_reproducibility(self):
        """Test that specifying the same random seed produces identical noise realizations."""
        run1 = add_awgn(self.clean_signal, snr_db=10, seed=123)
        run2 = add_awgn(self.clean_signal, snr_db=10, seed=123)
        np.testing.assert_array_equal(run1, run2)

    def test_different_seeds_produce_different_realizations(self):
        """Test that different random seeds produce distinct noise realizations."""
        run1 = add_awgn(self.clean_signal, snr_db=10, seed=100)
        run2 = add_awgn(self.clean_signal, snr_db=10, seed=200)
        self.assertFalse(np.array_equal(run1, run2))

    def test_output_contains_only_finite_values(self):
        """Test that the output noisy signal contains no NaN or infinite values."""
        noisy = add_awgn(self.clean_signal, snr_db=5, seed=77)
        self.assertTrue(np.all(np.isfinite(noisy)))

    def test_rejection_of_multidimensional_signals(self):
        """Test that 2D or higher dimensional arrays are rejected."""
        signal_2d = np.ones((10, 10))
        with self.assertRaises(ValueError):
            add_awgn(signal_2d, snr_db=20)

    def test_rejection_of_nan_and_inf(self):
        """Test that signals containing NaN or Inf are rejected."""
        sig_nan = np.array([1.0, np.nan, 0.5])
        sig_inf = np.array([1.0, np.inf, 0.5])
        with self.assertRaises(ValueError):
            add_awgn(sig_nan, snr_db=20)
        with self.assertRaises(ValueError):
            add_awgn(sig_inf, snr_db=20)

    def test_rejection_of_invalid_snr(self):
        """Test that SNR values outside [0, 30] dB, non-numbers, NaN, and Inf are rejected."""
        # Below minimum range
        with self.assertRaises(ValueError):
            add_awgn(self.clean_signal, snr_db=-1.0)
        # Above maximum range
        with self.assertRaises(ValueError):
            add_awgn(self.clean_signal, snr_db=35.0)
        # NaN / Inf SNR
        with self.assertRaises(ValueError):
            add_awgn(self.clean_signal, snr_db=float("nan"))
        with self.assertRaises(ValueError):
            add_awgn(self.clean_signal, snr_db=float("inf"))
        # Non-numeric / boolean SNR
        with self.assertRaises(TypeError):
            add_awgn(self.clean_signal, snr_db="20")
        with self.assertRaises(TypeError):
            add_awgn(self.clean_signal, snr_db=True)

    def test_noisy_signal_differs_from_clean_signal(self):
        """Test that noisy signal actually differs from clean input at valid SNR."""
        noisy = add_awgn(self.clean_signal, snr_db=20, seed=99)
        self.assertFalse(np.allclose(noisy, self.clean_signal))

    def test_empirical_noise_power_matches_theoretical_target(self):
        """Test that empirical noise power is reasonably close to theoretical target for large N."""
        # Long signal (N = 50,000 samples)
        t_long = np.arange(50000, dtype=float) / self.fs
        long_signal = np.sin(2.0 * np.pi * self.fc * t_long)
        p_x = float(np.mean(long_signal ** 2))  # ~ 0.5 for unit sine wave

        test_snr_db = 10.0
        snr_linear = 10.0 ** (test_snr_db / 10.0)  # 10.0
        expected_noise_power = p_x / snr_linear      # ~ 0.05

        noisy_long = add_awgn(long_signal, snr_db=test_snr_db, seed=42)
        extracted_noise = noisy_long - long_signal
        empirical_noise_power = float(np.var(extracted_noise))

        # Check empirical variance is within 5% of theoretical noise power
        self.assertAlmostEqual(
            empirical_noise_power,
            expected_noise_power,
            delta=expected_noise_power * 0.05,
        )

    def test_rejection_of_invalid_seed(self):
        """Test that non-integer seeds are rejected."""
        with self.assertRaises(TypeError):
            add_awgn(self.clean_signal, snr_db=15, seed="seed123")
        with self.assertRaises(TypeError):
            add_awgn(self.clean_signal, snr_db=15, seed=12.34)
        with self.assertRaises(TypeError):
            add_awgn(self.clean_signal, snr_db=15, seed=True)


if __name__ == "__main__":
    unittest.main()
