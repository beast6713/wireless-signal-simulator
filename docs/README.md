# Wireless Digital Signal Modulation and Transmission Simulator
## Technical Documentation & Architecture Specification

> **Academic Notice:** This software is a purely computational, mathematical simulation running locally on a computer. It does **not** transmit real physical radio waves and does **not** require any physical hardware, IoT devices, microcontrollers, sensors, antennas, or external radio communication equipment.

---

## 1. System Architecture

The simulator is structured into distinct, modular Python components following the classical digital communication block diagram:

```text
[Input Text Message]
       │
       ▼
┌──────────────────┐
│ src/encoding.py  │  Text ──> UTF-8 Bytes ──> Binary Bitstream (0s and 1s)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│src/modulation.py │  Bits ──> Carrier Waveform s(t) [ASK / FSK / BPSK]
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  src/channel.py  │  AWGN Noise Injection: y(t) = s(t) + w(t) at SNR (dB)
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│src/demodulation.py│ Matched-Filter / Coherent Correlation ──> Recovered Bits
└────────┬─────────┘
         ├─────────────────────────────────────────┐
         │                                         │
         ▼                                         ▼
┌──────────────────┐                     ┌──────────────────┐
│ src/encoding.py  │                     │  src/metrics.py  │
│ (bits_to_text)   │                     │ (analyze_trans.) │
└────────┬─────────┘                     └────────┬─────────┘
         │                                         │
         ▼                                         ▼
[Recovered Message]                       [BER & Accuracy %]
         │                                         │
         └────────────────────┬────────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │src/visualization │ ──> Waveforms, Overlays & Step Plots
                    │     app.py       │ ──> Interactive Streamlit Dashboard
                    └──────────────────┘
```

---

## 2. Module Responsibilities

| Module | File | Key Functions | Responsibility |
| :--- | :--- | :--- | :--- |
| **Encoding** | `src/encoding.py` | `text_to_bits()`, `bits_to_text()`, `format_bits_for_display()` | Converts arbitrary text into 8-bit UTF-8 octets and decodes bit arrays back into characters. Rejects malformed UTF-8 gracefully. |
| **Modulation** | `src/modulation.py` | `ask_modulate()`, `fsk_modulate()`, `bpsk_modulate()`, `get_time_vector()` | Synthesizes continuous-time sinusoidal carrier waves sampled at $f_s = 10,000\text{ Hz}$ with $T_b = 0.01\text{ s}$ ($100\text{ samples/bit}$). |
| **Channel** | `src/channel.py` | `add_awgn()` | Computes mean signal power $P_x$, calculates noise power $P_w = P_x / 10^{(\text{SNR}/10)}$, and adds independent zero-mean Gaussian noise $w[n] \sim \mathcal{N}(0, \sigma_w^2)$. |
| **Demodulation**| `src/demodulation.py` | `ask_demodulate()`, `fsk_demodulate()`, `bpsk_demodulate()` | Implements coherent matched-filter correlation over each bit interval. Employs optimal decision thresholds for each scheme. |
| **Metrics** | `src/metrics.py` | `count_bit_errors()`, `calculate_ber()`, `calculate_accuracy()`, `analyze_transmission()` | Evaluates bit discrepancy count, Bit Error Rate (BER), and percentage accuracy from binary bitstreams. |
| **Visualization**| `src/visualization.py`| `plot_modulated_signal()`, `plot_received_signal()`, `plot_signal_comparison()`, `plot_bit_comparison()` | Generates Matplotlib `Figure` objects illustrating transmitted carriers, noisy channels, dual-axis comparisons, and digital step plots. |
| **User Interface**| `app.py` | `main()` | Provides the interactive Streamlit dashboard, tying the entire simulation pipeline together with state tracking and responsive error handling. |

---

## 3. Mathematical Foundations

### 3.1 Base Parameters
- **Sampling Frequency ($f_s$):** $10,000\text{ Hz}$
- **Bit Duration ($T_b$):** $0.01\text{ s}$ ($10\text{ ms}$)
- **Samples per Bit ($N_s$):** $f_s \times T_b = 100\text{ samples}$
- **Carrier Frequency ($f_c$):** $1,000\text{ Hz}$ ($10\text{ samples/cycle}$)
- **Peak Signal Amplitude ($A$):** $1.0$

### 3.2 Modulation Schemes
1. **Amplitude Shift Keying (ASK / OOK):**
   $$s(t) = \begin{cases} A\sin(2\pi f_c t), & b = 1 \\ 0, & b = 0 \end{cases}$$
2. **Frequency Shift Keying (FSK):**
   $$s(t) = A\sin(2\pi f_b t), \quad f_b = \begin{cases} f_1 = 1500\text{ Hz}, & b = 1 \\ f_0 = 500\text{ Hz}, & b = 0 \end{cases}$$
3. **Binary Phase Shift Keying (BPSK):**
   $$s(t) = A\sin(2\pi f_c t + \phi_b), \quad \phi_b = \begin{cases} 0, & b = 1 \implies +A\sin(2\pi f_c t) \\ \pi, & b = 0 \implies -A\sin(2\pi f_c t) \end{cases}$$

### 3.3 Channel Noise (AWGN)
- **Average Signal Power:**
  $$P_x = \frac{1}{M}\sum_{n=0}^{M-1} x[n]^2$$
- **Linear SNR Conversion:**
  $$\text{SNR}_{\text{linear}} = 10^{\frac{\text{SNR}_{\text{dB}}}{10}}$$
- **Gaussian Noise Distribution:**
  $$w[n] \sim \mathcal{N}\left(0, \frac{P_x}{\text{SNR}_{\text{linear}}}\right), \quad y[n] = x[n] + w[n]$$

### 3.4 Coherent Demodulation & Decision Rules
1. **ASK:** Correlation statistic $r_k = \sum_{n=0}^{N_s-1} y_k[n]\sin(2\pi f_c t_n)$.
   $$\text{Decision: } \hat{b}_k = 1 \iff r_k > \frac{A}{2} \sum_{n=0}^{N_s-1} \sin^2(2\pi f_c t_n)$$
2. **FSK:** Dual-branch matched filtering:
   $$\hat{b}_k = 1 \iff \sum y_k[n]\sin(2\pi f_1 t_n) > \sum y_k[n]\sin(2\pi f_0 t_n)$$
3. **BPSK:** Coherent correlation with synchronized reference:
   $$\hat{b}_k = 1 \iff \sum y_k[n]\sin(2\pi f_c t_n) \ge 0.0$$

### 3.5 Performance Metrics
- **Bit Error Rate (BER):**
  $$\text{BER} = \frac{\sum_{i=0}^{N-1} (b_{\text{tx}}[i] \neq b_{\text{rx}}[i])}{N}$$
- **Bit Accuracy Percentage:**
  $$\text{Accuracy (\%)} = (1.0 - \text{BER}) \times 100.0$$

---

## 4. Simulation Assumptions & Technical Constraints

1. **Software Simulation Only:** No physical radio transmission, wireless spectrum radiation, or IoT hardware is used.
2. **Coherent Synchronization:** The receiver assumes ideal carrier phase and frequency synchronization with the transmitter.
3. **Additive White Gaussian Noise Medium:** Assumes an unguided, flat, non-dispersive channel without multi-path fading, Doppler spread, or inter-symbol interference (ISI).
4. **Independent Noise Trials:** Each transmission pass generates a new stochastic Gaussian noise realization unless an explicit random seed is provided.
5. **Decoupled Bit-Level Analysis:** BER and accuracy are computed from raw bit comparisons. Thus, performance metrics remain valid even when severe channel noise corrupts UTF-8 byte syntax.

---

## 5. Verification & Testing Strategy

The repository includes a comprehensive unit testing suite using Python's standard `unittest` framework:

- **`tests/test_encoding.py`**: Validates UTF-8 encoding, multi-byte Unicode strings (accents, emojis, non-English scripts), whitespace preservation, and error handling.
- **`tests/test_modulation.py`**: Validates sample counts, peak amplitudes, tone frequencies, opposite phase shifts, and input validation.
- **`tests/test_channel.py`**: Validates signal non-mutability, length preservation, zero-signal handling, seed repeatability, and noise power scaling against theoretical formulas.
- **`tests/test_demodulation.py`**: Validates noiseless recovery, AWGN noise tolerance, incomplete bit rejection, and edge cases.
- **`tests/test_metrics.py`**: Validates bit error counts, mathematical BER, accuracy bounds, empty sequence policies, and dictionary summaries.
- **`tests/test_visualization.py`**: Validates Matplotlib Figure object generation, parameter constraints, and clean memory cleanup without opening GUI windows.

To execute the complete automated test suite:
```powershell
python -m unittest discover -s tests -v
```
