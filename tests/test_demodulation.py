"""Unit tests for receiver demodulation module.

Phase 5: Receiver and Demodulation
Academic Mini-Project | Software-Based Wireless Communication Simulator
"""

import unittest
import numpy as np

from src.channel import add_awgn
from src.demodulation import ask_demodulate, bpsk_demodulate, fsk_demodulate
from src.encoding import bits_to_text, text_to_bits
from src.modulation import ask_modulate, bpsk_modulate, fsk_modulate


class TestDemodulation(unittest.TestCase):
    """Test suite for ASK, FSK, and BPSK coherent demodulation functions."""

    def setUp(self):
        """Set up standard test parameters matching project defaults."""
        self.fs = 10000.0
        self.fc = 1000.0
        self.f0 = 500.0
        self.f1 = 1500.0
        self.tb = 0.01
        self.amplitude = 1.0
        self.test_bits = [1, 0, 1, 1, 0, 0, 1, 0]

    def test_noiseless_ask_recovery(self):
        """Test that ASK recovers a known bit sequence with 100% accuracy without noise."""
        waveform = ask_modulate(self.test_bits, self.fs, self.fc, self.tb, self.amplitude)
        recovered = ask_demodulate(waveform, self.fs, self.fc, self.tb, self.amplitude)
        self.assertEqual(recovered, self.test_bits)

    def test_noiseless_fsk_recovery(self):
        """Test that FSK recovers a known bit sequence with 100% accuracy without noise."""
        waveform = fsk_modulate(self.test_bits, self.fs, self.f0, self.f1, self.tb, self.amplitude)
        recovered = fsk_demodulate(waveform, self.fs, self.f0, self.f1, self.tb, self.amplitude)
        self.assertEqual(recovered, self.test_bits)

    def test_noiseless_bpsk_recovery(self):
        """Test that BPSK recovers a known bit sequence with 100% accuracy without noise."""
        waveform = bpsk_modulate(self.test_bits, self.fs, self.fc, self.tb, self.amplitude)
        recovered = bpsk_demodulate(waveform, self.fs, self.fc, self.tb, self.amplitude)
        self.assertEqual(recovered, self.test_bits)

    def test_empty_waveform_handling(self):
        """Test that all demodulators return an empty list for empty input."""
        for fn in (ask_demodulate, fsk_demodulate, bpsk_demodulate):
            with self.subTest(fn=fn.__name__):
                self.assertEqual(fn([]), [])
                self.assertEqual(fn(np.array([])), [])

    def test_rejection_of_multidimensional_signals(self):
        """Test that 2D or higher dimensional inputs are rejected."""
        signal_2d = np.ones((10, 100))
        for fn in (ask_demodulate, fsk_demodulate, bpsk_demodulate):
            with self.subTest(fn=fn.__name__):
                with self.assertRaises(ValueError):
                    fn(signal_2d)

    def test_rejection_of_nan_and_inf(self):
        """Test that signals containing NaN or Inf are rejected."""
        sig_nan = np.full(100, np.nan)
        sig_inf = np.full(100, np.inf)
        for fn in (ask_demodulate, fsk_demodulate, bpsk_demodulate):
            with self.subTest(fn=fn.__name__):
                with self.assertRaises(ValueError):
                    fn(sig_nan)
                with self.assertRaises(ValueError):
                    fn(sig_inf)

    def test_rejection_of_invalid_sampling_parameters(self):
        """Test rejection of non-positive fs, tb, or frequencies >= Nyquist."""
        valid_wf = np.ones(100)
        # Non-positive fs and tb
        with self.assertRaises(ValueError):
            ask_demodulate(valid_wf, sampling_frequency=-1000)
        with self.assertRaises(ValueError):
            ask_demodulate(valid_wf, bit_duration=0.0)

        # Frequencies >= Nyquist
        with self.assertRaises(ValueError):
            ask_demodulate(valid_wf, sampling_frequency=10000, carrier_frequency=5000)
        with self.assertRaises(ValueError):
            bpsk_demodulate(valid_wf, sampling_frequency=10000, carrier_frequency=6000)
        with self.assertRaises(ValueError):
            fsk_demodulate(valid_wf, sampling_frequency=10000, frequency_0=500, frequency_1=5000)

    def test_rejection_of_incomplete_bit_intervals(self):
        """Test that waveform lengths not divisible by samples per bit are rejected."""
        # 150 samples with samples_per_bit = 100 is not a full 2nd bit
        incomplete_wf = np.ones(150)
        for fn in (ask_demodulate, fsk_demodulate, bpsk_demodulate):
            with self.subTest(fn=fn.__name__):
                with self.assertRaises(ValueError):
                    fn(incomplete_wf)

    def test_ask_distinguishes_carrier_and_zero(self):
        """Test that ASK correctly identifies pure carrier as 1 and zero as 0."""
        single_bit_1 = ask_modulate([1])
        single_bit_0 = ask_modulate([0])
        self.assertEqual(ask_demodulate(single_bit_1), [1])
        self.assertEqual(ask_demodulate(single_bit_0), [0])

    def test_fsk_distinguishes_frequencies(self):
        """Test that FSK correctly identifies f0 as 0 and f1 as 1."""
        bit_0 = fsk_modulate([0])
        bit_1 = fsk_modulate([1])
        self.assertEqual(fsk_demodulate(bit_0), [0])
        self.assertEqual(fsk_demodulate(bit_1), [1])

    def test_bpsk_distinguishes_phases(self):
        """Test that BPSK correctly identifies 0 rad as 1 and pi rad as 0."""
        bit_1 = bpsk_modulate([1])
        bit_0 = bpsk_modulate([0])
        self.assertEqual(bpsk_demodulate(bit_1), [1])
        self.assertEqual(bpsk_demodulate(bit_0), [0])

    def test_reliable_demodulation_under_moderate_noise(self):
        """Test that ASK, FSK, and BPSK achieve 100% recovery at high/moderate SNR (25 dB)."""
        bits = [1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 1, 0]  # 'A', 'B'
        for name, mod_fn, demod_fn in [
            ("ASK", ask_modulate, ask_demodulate),
            ("FSK", fsk_modulate, fsk_demodulate),
            ("BPSK", bpsk_modulate, bpsk_demodulate),
        ]:
            with self.subTest(scheme=name):
                tx = mod_fn(bits, self.fs)
                rx = add_awgn(tx, snr_db=25.0, seed=42)
                recovered = demod_fn(rx, self.fs)
                self.assertEqual(recovered, bits)

    def test_utf8_end_to_end_message_recovery(self):
        """Test end-to-end text -> bits -> modulation -> AWGN -> demodulation -> text recovery."""
        original_message = "Hello Wireless World!"
        bits = text_to_bits(original_message)

        # Test with BPSK at SNR = 25 dB (clean recovery expected)
        tx = bpsk_modulate(bits)
        rx = add_awgn(tx, snr_db=25.0, seed=123)
        recovered_bits = bpsk_demodulate(rx)
        recovered_text = bits_to_text(recovered_bits)

        self.assertEqual(recovered_bits, bits)
        self.assertEqual(recovered_text, original_message)

    def test_invalid_utf8_handling_safely(self):
        """Test that corrupted bits that violate UTF-8 raise UnicodeDecodeError safely."""
        # 8 bits of 0xFF (11111111) is illegal in UTF-8
        illegal_bits = [1, 1, 1, 1, 1, 1, 1, 1]
        with self.assertRaises(UnicodeDecodeError):
            bits_to_text(illegal_bits)


if __name__ == "__main__":
    unittest.main()
