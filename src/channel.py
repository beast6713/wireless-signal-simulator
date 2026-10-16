"""Simulated wireless communication channel module (noise addition).

Phase 4: Wireless Channel Simulation
Academic Mini-Project | Software-Based Wireless Communication Simulator

This module simulates the physical transmission medium by adding Additive White
Gaussian Noise (AWGN) to a modulated carrier waveform based on a user-selected
Signal-to-Noise Ratio (SNR in dB).
"""

from typing import Any, Optional
import numpy as np


def add_awgn(
    signal: Any,
    snr_db: float,
    seed: Optional[int] = None,
) -> np.ndarray:
    """Add Additive White Gaussian Noise (AWGN) to a transmitted signal waveform.

    Mathematical Model:
        y[n] = x[n] + w[n]

        Where:
            x[n] is the transmitted discrete-time signal.
            w[n] ~ N(0, sigma_w^2) is independent zero-mean Gaussian noise.
            y[n] is the received noisy signal.

        Average signal power:
            P_x = (1 / N) * sum(x[n]^2)

        Linear SNR:
            SNR_linear = 10^(SNR_dB / 10)

        Required noise power:
            P_w = P_x / SNR_linear

        Noise standard deviation:
            sigma_w = sqrt(P_w)

    Academic Simulation Notice:
        This is a real-valued AWGN simulation computed mathematically from the
        waveform's average power. No actual RF hardware, antennas, or physical
        wireless transmissions occur.

    Args:
        signal: A 1-dimensional array-like sequence (list, tuple, np.ndarray)
            of finite numeric values.
        snr_db: Signal-to-Noise Ratio in decibels. Supported range is [0.0, 30.0] dB.
        seed: Optional integer seed for the random number generator (useful for
            reproducible unit testing).

    Returns:
        np.ndarray: Received noisy signal with the exact same length as the input.
            Returns an empty float array if the input signal is empty.
            Returns a copy of the zero signal if the input signal power is 0.

    Raises:
        TypeError: If signal contains non-numeric values, or if snr_db / seed
            have invalid types.
        ValueError: If signal is multidimensional, contains NaN or infinite values,
            or if snr_db is outside the supported range [0.0, 30.0] dB.
    """
    # Reject non-sequences
    if not isinstance(signal, (list, tuple, np.ndarray)):
        raise TypeError(
            f"Input signal must be a list, tuple, or np.ndarray, got {type(signal).__name__}."
        )

    # Convert to NumPy float array and check for non-numeric types
    try:
        arr = np.asarray(signal, dtype=float)
    except (ValueError, TypeError) as err:
        raise TypeError(f"Signal must contain numeric values only: {err}") from err

    # Check dimensionality
    if arr.ndim != 1:
        raise ValueError(
            f"Input signal must be 1-dimensional, got {arr.ndim} dimensions."
        )

    # Handle empty input array
    if len(arr) == 0:
        return np.array([], dtype=float)

    # Check for NaN and Inf
    if not np.all(np.isfinite(arr)):
        raise ValueError("Signal contains non-finite values (NaN or Inf).")

    # Validate SNR value
    if not isinstance(snr_db, (int, float, np.floating, np.integer)) or isinstance(snr_db, bool):
        raise TypeError(f"SNR must be a numeric value, got {type(snr_db).__name__}.")
    if not np.isfinite(snr_db):
        raise ValueError(f"SNR must be a finite number, got {snr_db}.")
    if snr_db < 0.0 or snr_db > 30.0:
        raise ValueError(
            f"SNR ({snr_db} dB) is outside the supported range of [0.0, 30.0] dB."
        )

    # Validate seed parameter
    if seed is not None:
        if not isinstance(seed, (int, np.integer)) or isinstance(seed, bool):
            raise TypeError(f"Seed must be an integer, got {type(seed).__name__}.")

    # Calculate average signal power P_x
    p_x = float(np.mean(arr ** 2))

    # A zero-power signal cannot have a defined SNR; return copy unchanged
    if p_x == 0.0:
        return arr.copy()

    # Convert SNR from decibels to linear scale
    snr_linear = 10.0 ** (float(snr_db) / 10.0)

    # Calculate required noise power P_w and standard deviation sigma_w
    p_w = p_x / snr_linear
    sigma_w = np.sqrt(p_w)

    # Generate Gaussian noise using independent random number generator
    rng = np.random.default_rng(seed)
    noise = rng.normal(loc=0.0, scale=sigma_w, size=len(arr))

    # Received noisy signal y[n] = x[n] + w[n]
    noisy_signal = arr + noise

    return noisy_signal
