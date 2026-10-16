"""Receiver-side signal demodulation and bit recovery module.

Phase 5: Receiver and Demodulation
Academic Mini-Project | Software-Based Wireless Communication Simulator

This module implements coherent matched-filter and correlation-based
demodulation algorithms for:
- Amplitude Shift Keying (ASK)
- Frequency Shift Keying (FSK)
- Binary Phase Shift Keying (BPSK)
"""

from typing import Any, List
import numpy as np


def _validate_common_params(
    sampling_frequency: float,
    bit_duration: float,
    amplitude: float = 1.0,
) -> int:
    """Validate sampling parameters and calculate samples per bit.

    Args:
        sampling_frequency: Sampling rate in Hz (> 0).
        bit_duration: Duration of each bit in seconds (> 0).
        amplitude: Peak signal amplitude (> 0).

    Returns:
        int: Samples per bit.

    Raises:
        ValueError: If any parameter is non-positive.
    """
    if sampling_frequency <= 0:
        raise ValueError(
            f"Sampling frequency must be positive, got {sampling_frequency}."
        )
    if bit_duration <= 0:
        raise ValueError(f"Bit duration must be positive, got {bit_duration}.")
    if amplitude <= 0:
        raise ValueError(f"Amplitude must be positive, got {amplitude}.")

    samples_per_bit = int(round(sampling_frequency * bit_duration))
    if samples_per_bit <= 0:
        raise ValueError(
            f"Calculated samples per bit is {samples_per_bit}. "
            "Ensure sampling_frequency * bit_duration >= 1."
        )
    return samples_per_bit


def _validate_received_signal(
    received_signal: Any,
    samples_per_bit: int,
) -> np.ndarray:
    """Validate and sanitize a received discrete-time waveform.

    Args:
        received_signal: 1D array-like sequence of finite numeric values.
        samples_per_bit: Number of samples in each bit interval.

    Returns:
        np.ndarray: Validated 1D float array.

    Raises:
        TypeError: If signal contains non-numeric types or is not a sequence.
        ValueError: If signal is multidimensional, contains NaN/Inf, or has a
            length not divisible by samples_per_bit.
    """
    if not isinstance(received_signal, (list, tuple, np.ndarray)):
        raise TypeError(
            f"Received signal must be a list, tuple, or np.ndarray, got {type(received_signal).__name__}."
        )

    try:
        arr = np.asarray(received_signal, dtype=float)
    except (ValueError, TypeError) as err:
        raise TypeError(
            f"Received signal must contain numeric values only: {err}"
        ) from err

    if arr.ndim != 1:
        raise ValueError(
            f"Received signal must be 1-dimensional, got {arr.ndim} dimensions."
        )

    if len(arr) == 0:
        return np.array([], dtype=float)

    if not np.all(np.isfinite(arr)):
        raise ValueError("Received signal contains non-finite values (NaN or Inf).")

    if len(arr) % samples_per_bit != 0:
        raise ValueError(
            f"Received signal length ({len(arr)}) is not divisible by samples per bit ({samples_per_bit}). "
            "Incomplete bit interval detected."
        )

    return arr


def ask_demodulate(
    received_signal: Any,
    sampling_frequency: float = 10000.0,
    carrier_frequency: float = 1000.0,
    bit_duration: float = 0.01,
    amplitude: float = 1.0,
) -> List[int]:
    """Demodulate a received ASK signal using matched-filter correlation.

    Mathematical Model:
        For each bit interval k:
            s_ref(t) = sin(2 * pi * f_c * t)
            correlation_k = sum(y[n] * s_ref[n])
            threshold_k = (A / 2) * sum(s_ref[n]^2)

            Decision rule:
                bit = 1 if correlation_k > threshold_k else 0

        Threshold Rationale:
            For binary ASK (On-Off Keying) under AWGN with equal a priori
            probabilities, the optimal likelihood-ratio decision boundary
            lies halfway between the expected noiseless responses:
            E[corr | bit=1] = A * E_carrier, and E[corr | bit=0] = 0.
            Therefore, the optimal threshold is (A / 2) * E_carrier.

    Args:
        received_signal: 1D array of discrete signal samples.
        sampling_frequency: Sampling rate in Hz (default: 10000.0).
        carrier_frequency: Carrier frequency in Hz (default: 1000.0).
        bit_duration: Duration of one bit in seconds (default: 0.01).
        amplitude: Expected peak carrier amplitude for bit 1 (default: 1.0).

    Returns:
        List[int]: Recovered binary bit sequence (0s and 1s). Returns [] if empty.

    Raises:
        TypeError, ValueError: If input parameters or signal waveform are invalid.
    """
    samples_per_bit = _validate_common_params(
        sampling_frequency, bit_duration, amplitude
    )
    arr = _validate_received_signal(received_signal, samples_per_bit)
    if len(arr) == 0:
        return []

    if carrier_frequency <= 0:
        raise ValueError(
            f"Carrier frequency must be positive, got {carrier_frequency}."
        )
    nyquist = sampling_frequency / 2.0
    if carrier_frequency >= nyquist:
        raise ValueError(
            f"Carrier frequency ({carrier_frequency} Hz) must be strictly below "
            f"Nyquist frequency ({nyquist} Hz)."
        )

    num_bits = len(arr) // samples_per_bit
    t = np.arange(len(arr), dtype=float) / sampling_frequency
    carrier = np.sin(2.0 * np.pi * carrier_frequency * t)

    # Correlate received signal with coherent reference carrier
    corr_per_bit = np.sum((arr * carrier).reshape(num_bits, samples_per_bit), axis=1)
    ref_energy_per_bit = np.sum((carrier ** 2).reshape(num_bits, samples_per_bit), axis=1)

    threshold = (amplitude / 2.0) * ref_energy_per_bit
    recovered_bits = (corr_per_bit > threshold).astype(int).tolist()

    return recovered_bits


def fsk_demodulate(
    received_signal: Any,
    sampling_frequency: float = 10000.0,
    frequency_0: float = 500.0,
    frequency_1: float = 1500.0,
    bit_duration: float = 0.01,
    amplitude: float = 1.0,
) -> List[int]:
    """Demodulate a received FSK signal using dual-branch matched filters.

    Mathematical Model:
        For each bit interval k:
            corr_0 = sum(y[n] * sin(2 * pi * f_0 * t))
            corr_1 = sum(y[n] * sin(2 * pi * f_1 * t))

            Decision rule:
                bit = 1 if corr_1 > corr_0 else 0

        Decision Rationale:
            Dual coherent correlation branches measure energy alignment with
            frequency f_0 versus frequency f_1. The maximum correlation
            statistic identifies the most probable transmitted tone.

    Args:
        received_signal: 1D array of discrete signal samples.
        sampling_frequency: Sampling rate in Hz (default: 10000.0).
        frequency_0: Carrier frequency in Hz for bit 0 (default: 500.0).
        frequency_1: Carrier frequency in Hz for bit 1 (default: 1500.0).
        bit_duration: Duration of one bit in seconds (default: 0.01).
        amplitude: Expected peak carrier amplitude (default: 1.0).

    Returns:
        List[int]: Recovered binary bit sequence (0s and 1s). Returns [] if empty.

    Raises:
        TypeError, ValueError: If input parameters or signal waveform are invalid.
    """
    samples_per_bit = _validate_common_params(
        sampling_frequency, bit_duration, amplitude
    )
    arr = _validate_received_signal(received_signal, samples_per_bit)
    if len(arr) == 0:
        return []

    nyquist = sampling_frequency / 2.0
    if frequency_0 <= 0 or frequency_0 >= nyquist:
        raise ValueError(
            f"Frequency 0 ({frequency_0} Hz) must be positive and below Nyquist ({nyquist} Hz)."
        )
    if frequency_1 <= 0 or frequency_1 >= nyquist:
        raise ValueError(
            f"Frequency 1 ({frequency_1} Hz) must be positive and below Nyquist ({nyquist} Hz)."
        )
    if frequency_0 == frequency_1:
        raise ValueError("frequency_0 and frequency_1 must be distinct for FSK.")

    num_bits = len(arr) // samples_per_bit
    t = np.arange(len(arr), dtype=float) / sampling_frequency

    ref_0 = np.sin(2.0 * np.pi * frequency_0 * t)
    ref_1 = np.sin(2.0 * np.pi * frequency_1 * t)

    corr_0 = np.sum((arr * ref_0).reshape(num_bits, samples_per_bit), axis=1)
    corr_1 = np.sum((arr * ref_1).reshape(num_bits, samples_per_bit), axis=1)

    recovered_bits = (corr_1 > corr_0).astype(int).tolist()

    return recovered_bits


def bpsk_demodulate(
    received_signal: Any,
    sampling_frequency: float = 10000.0,
    carrier_frequency: float = 1000.0,
    bit_duration: float = 0.01,
    amplitude: float = 1.0,
) -> List[int]:
    """Demodulate a received BPSK signal using coherent phase correlation.

    Coherent Detection Notice:
        This function implements coherent BPSK detection, assuming an ideal
        synchronized local reference carrier matching Phase 3 modulation.
        Carrier recovery and phase estimation are outside the simulator scope.

    Mathematical Model:
        For each bit interval k:
            s_ref(t) = sin(2 * pi * f_c * t)
            corr_k = sum(y[n] * s_ref[n])

            Decision rule:
                bit = 1 if corr_k >= 0.0 else 0

        Decision Rationale:
            In Phase 3 BPSK:
                Bit 1 transmits +A * sin(2 * pi * f_c * t) (correlation > 0)
                Bit 0 transmits -A * sin(2 * pi * f_c * t) (correlation < 0)
            The zero boundary (corr_k = 0) provides the optimal maximum-likelihood
            decision boundary in AWGN. Deterministic tie-breaking assigns 1.

    Args:
        received_signal: 1D array of discrete signal samples.
        sampling_frequency: Sampling rate in Hz (default: 10000.0).
        carrier_frequency: Carrier frequency in Hz (default: 1000.0).
        bit_duration: Duration of one bit in seconds (default: 0.01).
        amplitude: Expected peak carrier amplitude (default: 1.0).

    Returns:
        List[int]: Recovered binary bit sequence (0s and 1s). Returns [] if empty.

    Raises:
        TypeError, ValueError: If input parameters or signal waveform are invalid.
    """
    samples_per_bit = _validate_common_params(
        sampling_frequency, bit_duration, amplitude
    )
    arr = _validate_received_signal(received_signal, samples_per_bit)
    if len(arr) == 0:
        return []

    if carrier_frequency <= 0:
        raise ValueError(
            f"Carrier frequency must be positive, got {carrier_frequency}."
        )
    nyquist = sampling_frequency / 2.0
    if carrier_frequency >= nyquist:
        raise ValueError(
            f"Carrier frequency ({carrier_frequency} Hz) must be strictly below "
            f"Nyquist frequency ({nyquist} Hz)."
        )

    num_bits = len(arr) // samples_per_bit
    t = np.arange(len(arr), dtype=float) / sampling_frequency
    carrier = np.sin(2.0 * np.pi * carrier_frequency * t)

    corr = np.sum((arr * carrier).reshape(num_bits, samples_per_bit), axis=1)

    # Decide bit 1 for positive correlation, bit 0 for negative correlation
    recovered_bits = (corr >= 0.0).astype(int).tolist()

    return recovered_bits
