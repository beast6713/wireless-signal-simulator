"""Unit tests for signal visualization module.

Phase 7: Signal Visualization and Results Dashboard
Academic Mini-Project | Software-Based Wireless Communication Simulator
"""

import unittest
import matplotlib.pyplot as plt
import numpy as np

from src.visualization import (
    plot_bit_comparison,
    plot_modulated_signal,
    plot_received_signal,
    plot_signal_comparison,
)


class TestVisualization(unittest.TestCase):
    """Test suite for Matplotlib plotting functions."""

    def setUp(self):
        """Set up standard test signals and bitstreams."""
        self.sample_rate = 10000.0
        self.signal_len = 400
        self.clean_signal = np.sin(2.0 * np.pi * 1000.0 * np.arange(self.signal_len) / self.sample_rate)
        self.noisy_signal = self.clean_signal + 0.1 * np.random.randn(self.signal_len)
        self.tx_bits = [1, 0, 1, 1, 0, 0, 1, 0]
        self.rx_bits = [1, 0, 0, 1, 0, 0, 1, 1]  # 2 bit errors

    def tearDown(self):
        """Close any generated figures to prevent memory leaks."""
        plt.close("all")

    def test_plot_modulated_signal_returns_figure(self):
        """Test that plot_modulated_signal returns a valid matplotlib Figure."""
        fig = plot_modulated_signal(self.clean_signal, self.sample_rate)
        self.assertIsInstance(fig, plt.Figure)
        plt.close(fig)

    def test_plot_received_signal_returns_figure(self):
        """Test that plot_received_signal returns a valid matplotlib Figure."""
        fig = plot_received_signal(self.noisy_signal, self.sample_rate)
        self.assertIsInstance(fig, plt.Figure)
        plt.close(fig)

    def test_plot_bit_comparison_returns_figure(self):
        """Test that plot_bit_comparison returns a valid Figure with step plots."""
        fig = plot_bit_comparison(self.tx_bits, self.rx_bits)
        self.assertIsInstance(fig, plt.Figure)
        plt.close(fig)

    def test_plot_signal_comparison_returns_figure(self):
        """Test that plot_signal_comparison returns a valid Figure."""
        fig = plot_signal_comparison(self.clean_signal, self.noisy_signal, self.sample_rate)
        self.assertIsInstance(fig, plt.Figure)
        plt.close(fig)

    def test_rejection_of_empty_inputs(self):
        """Test that plotting functions reject empty signals or empty bitstreams."""
        with self.assertRaises(ValueError):
            plot_modulated_signal([], self.sample_rate)
        with self.assertRaises(ValueError):
            plot_received_signal([], self.sample_rate)
        with self.assertRaises(ValueError):
            plot_bit_comparison([], [])
        with self.assertRaises(ValueError):
            plot_signal_comparison([], [], self.sample_rate)

    def test_rejection_of_invalid_sample_rate(self):
        """Test that non-positive sample rates are rejected."""
        with self.assertRaises(ValueError):
            plot_modulated_signal(self.clean_signal, sample_rate=-100.0)
        with self.assertRaises(ValueError):
            plot_received_signal(self.noisy_signal, sample_rate=0.0)
        with self.assertRaises(ValueError):
            plot_signal_comparison(self.clean_signal, self.noisy_signal, sample_rate=-50.0)

    def test_rejection_of_mismatched_lengths(self):
        """Test that length mismatches in comparison plots raise ValueError."""
        # Bit length mismatch
        with self.assertRaises(ValueError):
            plot_bit_comparison([1, 0], [1, 0, 1])

        # Signal length mismatch
        with self.assertRaises(ValueError):
            plot_signal_comparison(self.clean_signal, self.clean_signal[:200], self.sample_rate)

    def test_rejection_of_multidimensional_and_nan(self):
        """Test that 2D arrays and NaNs are rejected."""
        arr_2d = np.ones((5, 10))
        arr_nan = np.array([1.0, np.nan, 0.5])
        with self.assertRaises(ValueError):
            plot_modulated_signal(arr_2d, self.sample_rate)
        with self.assertRaises(ValueError):
            plot_modulated_signal(arr_nan, self.sample_rate)


if __name__ == "__main__":
    unittest.main()
