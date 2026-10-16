"""Digital signal modulation module.

Phase 3: Digital Signal Modulation
Academic Mini-Project | Software-Based Wireless Communication Simulator

This module implements discrete-time mathematical modulation for:
- Amplitude Shift Keying (ASK)
- Frequency Shift Keying (FSK)
- Binary Phase Shift Keying (BPSK)
"""

from typing import Any, List, Sequence, Union
import numpy as np


def _validate_bits(bits: Any) -> List[int]:
    """Validate and sanitize a binary sequence input.

    Args:
        bits: A 1D sequence (list, tuple, or 1D np.ndarray) of binary bits (0 or 1).

    Returns:
        List[int]: A validated list of integer bits (0 or 1).

    Raises:
        TypeError: If input is not a sequence, contains booleans, or non-integer elements.
        ValueError: If input is multidimensional or contains values other than 0 and 1.
    """
    # Reject non-sequences
    if not isinstance(bits, (list, tuple, np.ndarray)):
        raise TypeError(
            f"Input bits must be a list, tuple, or 1D numpy array, got {type(bits).__name__}."
        )

    # Check numpy array dimensionality
    if isinstance(bits, np.ndarray):
        if bits.ndim != 1:
            raise ValueError(
                f"Input bits array must be 1-dimensional, got {bits.ndim} dimensions."
            )

    cleaned: List[int] = []
    for idx, bit in enumerate(bits):
        # Python bool is a subclass of int, so explicitly reject booleans
        if isinstance(bit, (bool, np.bool_)):
            raise TypeError(
                f"Invalid bit at index {idx}: boolean values (True/False) are not allowed. "
                "Use integer 0 or 1."
            )
        # Verify integer type
        if not isinstance(bit, (int, np.integer)):
            raise TypeError(
                f"Invalid bit at index {idx}: expected integer, got {type(bit).__name__}."
            )
        val = int(bit)
        if val not in (0, 1):
            raise ValueError(
                f"Invalid bit value at index {idx}: expected 0 or 1, got {bit!r}."
            )
        cleaned.append(val)

    return cleaned


def _validate_common_params(
    sampling_frequency: float,
    bit_duration: float,
    amplitude: float,
) -> int:
    """Validate common signal parameters and calculate samples per bit.

    Args:
        sampling_frequency: Sampling rate in Hz (> 0).
        bit_duration: Duration of each bit in seconds (> 0).
        amplitude: Peak signal amplitude (>= 0).

    Returns:
        int: Number of discrete samples per bit.

    Raises:
        ValueError: If any parameter is out of valid bounds.
    """
    if sampling_frequency <= 0:
        raise ValueError(
            f"Sampling frequency must be positive, got {sampling_frequency}."
        )
    if bit_duration <= 0:
        raise ValueError(f"Bit duration must be positive, got {bit_duration}.")
    if amplitude < 0:
        raise ValueError(f"Amplitude must be non-negative, got {amplitude}.")

    samples_per_bit = int(round(sampling_frequency * bit_duration))
    if samples_per_bit <= 0:
        raise ValueError(
            f"Calculated samples per bit is {samples_per_bit}. "
            "Ensure sampling_frequency * bit_duration >= 1."
        )
    return samples_per_bit


def ask_modulate(
    bits: Union[Sequence[int], np.ndarray],
    sampling_frequency: float = 10000.0,
    carrier_frequency: float = 1000.0,
    bit_duration: float = 0.01,
    amplitude: float = 1.0,
) -> np.ndarray:
    """Modulate a binary sequence using Amplitude Shift Keying (ASK).

    Mathematical Model:
        s(t) = A * sin(2 * pi * f_c * t)  when bit = 1
        s(t) = 0                           when bit = 0

    Args:
        bits: Binary sequence of 0s and 1s.
        sampling_frequency: Sampling rate in Hz (default: 10000.0).
        carrier_frequency: Carrier wave frequency in Hz (default: 1000.0).
        bit_duration: Time duration of one bit in seconds (default: 0.01).
        amplitude: Peak amplitude for bit 1 (default: 1.0).

    Returns:
        np.ndarray: Discrete-time modulated signal waveform. Returns an empty
            array if bits is empty.

    Raises:
        TypeError, ValueError: If input parameters or bits are invalid.
    """
    validated_bits = _validate_bits(bits)
    if not validated_bits:
        return np.array([], dtype=float)

    samples_per_bit = _validate_common_params(
        sampling_frequency, bit_duration, amplitude
    )

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

    total_samples = len(validated_bits) * samples_per_bit
    # Time vector starting at 0 and not including the endpoint of the full duration
    t = np.arange(total_samples, dtype=float) / sampling_frequency

    # Expand bits across the duration of each bit
    bit_stream = np.repeat(validated_bits, samples_per_bit)

    # ASK: Multiply carrier by the bit stream (1 for carrier, 0 for silence)
    carrier = amplitude * np.sin(2.0 * np.pi * carrier_frequency * t)
    waveform = bit_stream * carrier

    return waveform


def fsk_modulate(
    bits: Union[Sequence[int], np.ndarray],
    sampling_frequency: float = 10000.0,
    frequency_0: float = 500.0,
    frequency_1: float = 1500.0,
    bit_duration: float = 0.01,
    amplitude: float = 1.0,
) -> np.ndarray:
    """Modulate a binary sequence using Frequency Shift Keying (FSK).

    Mathematical Model:
        s(t) = A * sin(2 * pi * f_b * t)
        where f_b = frequency_0 for bit 0, and f_b = frequency_1 for bit 1.

    Continuous time t is maintained across the entire signal.

    Args:
        bits: Binary sequence of 0s and 1s.
        sampling_frequency: Sampling rate in Hz (default: 10000.0).
        frequency_0: Carrier frequency in Hz for bit 0 (default: 500.0).
        frequency_1: Carrier frequency in Hz for bit 1 (default: 1500.0).
        bit_duration: Time duration of one bit in seconds (default: 0.01).
        amplitude: Peak amplitude of the carrier wave (default: 1.0).

    Returns:
        np.ndarray: Discrete-time modulated signal waveform. Returns an empty
            array if bits is empty.

    Raises:
        TypeError, ValueError: If input parameters or bits are invalid.
    """
    validated_bits = _validate_bits(bits)
    if not validated_bits:
        return np.array([], dtype=float)

    samples_per_bit = _validate_common_params(
        sampling_frequency, bit_duration, amplitude
    )

    nyquist = sampling_frequency / 2.0
    if frequency_0 <= 0 or frequency_0 >= nyquist:
        raise ValueError(
            f"Frequency for bit 0 ({frequency_0} Hz) must be positive and below "
            f"Nyquist frequency ({nyquist} Hz)."
        )
    if frequency_1 <= 0 or frequency_1 >= nyquist:
        raise ValueError(
            f"Frequency for bit 1 ({frequency_1} Hz) must be positive and below "
            f"Nyquist frequency ({nyquist} Hz)."
        )
    if frequency_0 == frequency_1:
        raise ValueError(
            f"frequency_0 ({frequency_0} Hz) and frequency_1 ({frequency_1} Hz) "
            "must be distinct for FSK."
        )

    total_samples = len(validated_bits) * samples_per_bit
    t = np.arange(total_samples, dtype=float) / sampling_frequency

    # Assign frequency per sample based on each bit
    bit_stream = np.repeat(validated_bits, samples_per_bit)
    freq_stream = np.where(bit_stream == 1, frequency_1, frequency_0)

    waveform = amplitude * np.sin(2.0 * np.pi * freq_stream * t)

    return waveform


def bpsk_modulate(
    bits: Union[Sequence[int], np.ndarray],
    sampling_frequency: float = 10000.0,
    carrier_frequency: float = 1000.0,
    bit_duration: float = 0.01,
    amplitude: float = 1.0,
) -> np.ndarray:
    """Modulate a binary sequence using Binary Phase Shift Keying (BPSK).

    Mathematical Model:
        s(t) = A * sin(2 * pi * f_c * t + phi_b)
        where phi_b = 0 for bit 1, and phi_b = pi for bit 0.

    Args:
        bits: Binary sequence of 0s and 1s.
        sampling_frequency: Sampling rate in Hz (default: 10000.0).
        carrier_frequency: Carrier wave frequency in Hz (default: 1000.0).
        bit_duration: Time duration of one bit in seconds (default: 0.01).
        amplitude: Peak amplitude of the carrier wave (default: 1.0).

    Returns:
        np.ndarray: Discrete-time modulated signal waveform. Returns an empty
            array if bits is empty.

    Raises:
        TypeError, ValueError: If input parameters or bits are invalid.
    """
    validated_bits = _validate_bits(bits)
    if not validated_bits:
        return np.array([], dtype=float)

    samples_per_bit = _validate_common_params(
        sampling_frequency, bit_duration, amplitude
    )

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

    total_samples = len(validated_bits) * samples_per_bit
    t = np.arange(total_samples, dtype=float) / sampling_frequency

    # Assign phase: phi = 0 for bit 1, phi = pi for bit 0
    bit_stream = np.repeat(validated_bits, samples_per_bit)
    phase_stream = np.where(bit_stream == 1, 0.0, np.pi)

    waveform = amplitude * np.sin(2.0 * np.pi * carrier_frequency * t + phase_stream)

    return waveform


def get_time_vector(
    num_bits: int,
    sampling_frequency: float = 10000.0,
    bit_duration: float = 0.01,
) -> np.ndarray:
    """Generate the discrete time vector for a given number of bits.

    Args:
        num_bits: Total number of bits.
        sampling_frequency: Sampling rate in Hz (default: 10000.0).
        bit_duration: Bit duration in seconds (default: 0.01).

    Returns:
        np.ndarray: Time array starting at 0.0 and ending before total duration.
    """
    if num_bits <= 0:
        return np.array([], dtype=float)
    samples_per_bit = _validate_common_params(sampling_frequency, bit_duration, 1.0)
    total_samples = num_bits * samples_per_bit
    return np.arange(total_samples, dtype=float) / sampling_frequency
