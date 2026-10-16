"""Signal plotting and waveform visualization module.

Phase 7: Signal Visualization and Results Dashboard
Academic Mini-Project | Software-Based Wireless Communication Simulator

This module provides reusable Matplotlib plotting functions for:
- Modulated carrier waveforms
- Received noisy waveforms (AWGN)
- Synchronized signal comparison (transmitted vs. received)
- Binary bitstream comparison (step plot showing bit errors)
"""

from typing import Any, List, Optional
import matplotlib.pyplot as plt
import numpy as np


def _validate_signal(signal: Any, name: str = "Signal") -> np.ndarray:
    """Validate and sanitize a 1D numeric signal array.

    Args:
        signal: 1D array-like sequence of finite numeric values.
        name: Name of signal for descriptive error messages.

    Returns:
        np.ndarray: 1D float numpy array.

    Raises:
        TypeError: If signal contains non-numeric elements or is not a sequence.
        ValueError: If signal is empty, multidimensional, or contains NaN/Inf.
    """
    if not isinstance(signal, (list, tuple, np.ndarray)):
        raise TypeError(
            f"{name} must be a list, tuple, or np.ndarray, got {type(signal).__name__}."
        )

    try:
        arr = np.asarray(signal, dtype=float)
    except (ValueError, TypeError) as err:
        raise TypeError(f"{name} must contain numeric values only: {err}") from err

    if arr.ndim != 1:
        raise ValueError(f"{name} must be 1-dimensional, got {arr.ndim} dimensions.")

    if len(arr) == 0:
        raise ValueError(f"{name} cannot be empty.")

    if not np.all(np.isfinite(arr)):
        raise ValueError(f"{name} contains non-finite values (NaN or Inf).")

    return arr


def _validate_bits(bits: Any, name: str = "Bit sequence") -> List[int]:
    """Validate a binary bit sequence containing only integer 0 and 1.

    Args:
        bits: 1D sequence of binary bits.
        name: Name of sequence for error messages.

    Returns:
        List[int]: Validated integer bits.

    Raises:
        TypeError: If sequence contains booleans or non-integers.
        ValueError: If sequence is empty, multidimensional, or contains non-binary values.
    """
    if not isinstance(bits, (list, tuple, np.ndarray)):
        raise TypeError(
            f"{name} must be a list, tuple, or np.ndarray, got {type(bits).__name__}."
        )

    if isinstance(bits, np.ndarray) and bits.ndim != 1:
        raise ValueError(f"{name} must be 1-dimensional, got {bits.ndim} dimensions.")

    if len(bits) == 0:
        raise ValueError(f"{name} cannot be empty.")

    cleaned: List[int] = []
    for idx, b in enumerate(bits):
        if isinstance(b, (bool, np.bool_)):
            raise TypeError(
                f"Invalid bit in {name} at index {idx}: booleans are not allowed."
            )
        if not isinstance(b, (int, np.integer)):
            raise TypeError(
                f"Invalid bit in {name} at index {idx}: expected integer, got {type(b).__name__}."
            )
        val = int(b)
        if val not in (0, 1):
            raise ValueError(
                f"Invalid bit value in {name} at index {idx}: expected 0 or 1, got {b!r}."
            )
        cleaned.append(val)

    return cleaned


def plot_modulated_signal(
    signal: Any,
    sample_rate: float,
    title: str = "Modulated Signal",
    max_samples: Optional[int] = None,
) -> plt.Figure:
    """Plot the transmitted modulated signal waveform against time in seconds.

    Args:
        signal: 1D array of discrete signal samples.
        sample_rate: Sampling frequency in Hz (> 0).
        title: Plot title (default: "Modulated Signal").
        max_samples: Optional limit on the number of samples plotted for visual clarity.

    Returns:
        plt.Figure: Matplotlib figure ready for rendering in Streamlit.

    Raises:
        ValueError, TypeError: If signal or sample_rate is invalid.
    """
    arr = _validate_signal(signal, "Modulated signal")
    if sample_rate <= 0:
        raise ValueError(f"Sample rate must be positive, got {sample_rate}.")

    if max_samples is not None and max_samples > 0:
        arr = arr[:max_samples]

    t = np.arange(len(arr), dtype=float) / sample_rate

    fig, ax = plt.subplots(figsize=(10, 3.2), layout="constrained")
    ax.plot(t, arr, color="#0066cc", linewidth=1.2, label="Modulated Waveform")
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("Time (s)", fontsize=9)
    ax.set_ylabel("Amplitude", fontsize=9)
    ax.set_ylim(-1.3, 1.3)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", fontsize=8)

    return fig


def plot_received_signal(
    signal: Any,
    sample_rate: float,
    title: str = "Received Signal with AWGN Noise",
    max_samples: Optional[int] = None,
) -> plt.Figure:
    """Plot the noisy received waveform against time after passing through the AWGN channel.

    Args:
        signal: 1D array of noisy received signal samples.
        sample_rate: Sampling frequency in Hz (> 0).
        title: Plot title (default: "Received Signal with AWGN Noise").
        max_samples: Optional limit on the number of samples plotted.

    Returns:
        plt.Figure: Matplotlib figure ready for rendering in Streamlit.

    Raises:
        ValueError, TypeError: If signal or sample_rate is invalid.
    """
    arr = _validate_signal(signal, "Received signal")
    if sample_rate <= 0:
        raise ValueError(f"Sample rate must be positive, got {sample_rate}.")

    if max_samples is not None and max_samples > 0:
        arr = arr[:max_samples]

    t = np.arange(len(arr), dtype=float) / sample_rate

    fig, ax = plt.subplots(figsize=(10, 3.2), layout="constrained")
    ax.plot(t, arr, color="#d9534f", linewidth=1.1, label="Received Signal (with AWGN)")
    ax.set_title(title, fontsize=11, fontweight="bold")
    ax.set_xlabel("Time (s)", fontsize=9)
    ax.set_ylabel("Amplitude", fontsize=9)
    ax.grid(True, linestyle=":", alpha=0.6)
    ax.legend(loc="upper right", fontsize=8)

    return fig


def plot_bit_comparison(
    transmitted_bits: Any,
    received_bits: Any,
    max_bits: Optional[int] = None,
) -> plt.Figure:
    """Plot transmitted and recovered bits using synchronized step plots to highlight errors.

    Args:
        transmitted_bits: Sequence of transmitted integer bits (0 or 1).
        received_bits: Sequence of recovered integer bits (0 or 1).
        max_bits: Optional limit on the number of bits plotted for clarity.

    Returns:
        plt.Figure: Matplotlib figure comparing transmitted and recovered bitstreams.

    Raises:
        ValueError, TypeError: If bit sequences are invalid or have incompatible lengths.
    """
    tx = _validate_bits(transmitted_bits, "Transmitted bits")
    rx = _validate_bits(received_bits, "Received bits")

    if len(tx) != len(rx):
        raise ValueError(
            f"Bit sequences must have identical lengths: transmitted ({len(tx)}) vs received ({len(rx)})."
        )

    if max_bits is not None and max_bits > 0:
        tx = tx[:max_bits]
        rx = rx[:max_bits]

    n = len(tx)
    # Generate bit interval edges for step plotting: 0, 1, 2, ..., n
    indices = np.arange(n)
    step_x = np.arange(n + 1)
    step_tx = np.append(tx, tx[-1])
    step_rx = np.append(rx, rx[-1])

    # Identify bit discrepancy positions
    error_indices = [i for i in range(n) if tx[i] != rx[i]]

    fig, (ax_tx, ax_rx) = plt.subplots(
        2, 1, figsize=(10, 3.8), sharex=True, layout="constrained"
    )

    # Subplot 1: Transmitted Bits
    ax_tx.step(step_x, step_tx, where="post", color="#0066cc", linewidth=1.5, label="Transmitted Bits")
    ax_tx.set_title("Transmitted vs. Recovered Binary Bitstream", fontsize=11, fontweight="bold")
    ax_tx.set_ylabel("Tx Level", fontsize=9)
    ax_tx.set_ylim(-0.25, 1.25)
    ax_tx.set_yticks([0, 1])
    ax_tx.grid(True, linestyle=":", alpha=0.6)
    ax_tx.legend(loc="upper right", fontsize=8)

    # Subplot 2: Recovered Bits
    ax_rx.step(step_x, step_rx, where="post", color="#28a745", linewidth=1.5, label="Recovered Bits")
    # Highlight bit errors with red markers
    if error_indices:
        err_x = [i + 0.5 for i in error_indices]
        err_y = [rx[i] for i in error_indices]
        ax_rx.scatter(
            err_x, err_y, color="#d9534f", s=60, zorder=5, marker="x", linewidths=2.0, label="Bit Error"
        )
    ax_rx.set_xlabel("Bit Index", fontsize=9)
    ax_rx.set_ylabel("Rx Level", fontsize=9)
    ax_rx.set_ylim(-0.25, 1.25)
    ax_rx.set_yticks([0, 1])
    ax_rx.grid(True, linestyle=":", alpha=0.6)
    ax_rx.legend(loc="upper right", fontsize=8)

    return fig


def plot_signal_comparison(
    modulated_signal: Any,
    received_signal: Any,
    sample_rate: float,
    max_samples: Optional[int] = None,
) -> plt.Figure:
    """Plot the transmitted and received noisy waveforms side-by-side on synchronized axes.

    Args:
        modulated_signal: 1D array of clean modulated samples.
        received_signal: 1D array of noisy received samples.
        sample_rate: Sampling frequency in Hz (> 0).
        max_samples: Optional limit on the number of samples plotted for clarity.

    Returns:
        plt.Figure: Matplotlib figure displaying both signals for direct visual comparison.

    Raises:
        ValueError, TypeError: If signals are invalid or lengths do not match.
    """
    tx = _validate_signal(modulated_signal, "Modulated signal")
    rx = _validate_signal(received_signal, "Received signal")

    if len(tx) != len(rx):
        raise ValueError(
            f"Signal lengths must be equal for comparison: modulated ({len(tx)}) vs received ({len(rx)})."
        )

    if sample_rate <= 0:
        raise ValueError(f"Sample rate must be positive, got {sample_rate}.")

    if max_samples is not None and max_samples > 0:
        tx = tx[:max_samples]
        rx = rx[:max_samples]

    t = np.arange(len(tx), dtype=float) / sample_rate

    fig, (ax_top, ax_bot) = plt.subplots(
        2, 1, figsize=(10, 4.4), sharex=True, layout="constrained"
    )

    # Subplot 1: Clean Transmitted Waveform
    ax_top.plot(t, tx, color="#0066cc", linewidth=1.2, label="Clean Modulated Signal")
    ax_top.set_title("Signal Comparison: Transmitter vs. Channel Output", fontsize=11, fontweight="bold")
    ax_top.set_ylabel("Amplitude", fontsize=9)
    ax_top.set_ylim(-1.3, 1.3)
    ax_top.grid(True, linestyle=":", alpha=0.6)
    ax_top.legend(loc="upper right", fontsize=8)

    # Subplot 2: Noisy Received Waveform
    ax_bot.plot(t, rx, color="#d9534f", linewidth=1.1, alpha=0.9, label="Noisy Received Signal (AWGN)")
    ax_bot.plot(t, tx, color="#0066cc", linestyle="--", linewidth=0.8, alpha=0.5, label="Clean Reference")
    ax_bot.set_xlabel("Time (s)", fontsize=9)
    ax_bot.set_ylabel("Amplitude", fontsize=9)
    ax_bot.grid(True, linestyle=":", alpha=0.6)
    ax_bot.legend(loc="upper right", fontsize=8)

    return fig
