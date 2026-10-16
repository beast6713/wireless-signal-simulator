# Wireless Digital Signal Modulation and Transmission Simulator Using Python

> **Academic Notice:** This software is a purely computational, mathematical simulation running locally on a computer. It does **not** transmit real physical radio waves and does **not** require any physical hardware, IoT devices, microcontrollers, sensors, antennas, or external radio communication equipment.

---

## 1. Project Overview

The **Wireless Digital Signal Modulation and Transmission Simulator** is an interactive, academic software platform built in Python that simulates the complete end-to-end pipeline of digital wireless communication.

A user inputs an arbitrary text message, converts it into binary data, modulates it onto an analog carrier wave using classical digital modulation schemes (**ASK**, **FSK**, or **BPSK**), simulates physical channel degradation by injecting **Additive White Gaussian Noise (AWGN)** across an adjustable **Signal-to-Noise Ratio (SNR)**, demodulates the received signal at the receiver, and evaluates communication performance using **Bit Error Rate (BER)**, **accuracy percentages**, and interactive waveform plots.

---

## 2. Problem Statement

Understanding digital wireless communication conceptually can be challenging when abstract mathematical formulas are detached from practical observation. Physical radio hardware, oscilloscopes, and software-defined radio (SDR) platforms are expensive, complex to configure, and often inaccessible to students.

There is a clear educational need for a self-contained, software-only simulation tool that allows students and researchers to interactively observe how digital data is modulated onto sinusoidal carrier waves, how noise corrupts signal integrity across wireless channels, how matched-filter receivers recover transmitted bits, and how error rates quantitatively scale with noise power.

---

## 3. Project Objectives

- **Educational Demonstration**: Demystify the mathematical concepts behind digital modulation, channel noise, and receiver demodulation.
- **Baseband Encoding**: Illustrate binary encoding (UTF-8 text to bitstreams) and message reconstruction.
- **Waveform Synthesis**: Mathematically generate time-domain carrier waveforms modulated by discrete binary data.
- **Channel Modeling**: Simulate realistic wireless channel impairments using Additive White Gaussian Noise (AWGN) across user-selected SNR levels (0 to 30 dB).
- **Coherent Demodulation**: Implement matched-filter correlation decision rules to recover transmitted bits.
- **Quantitative Metrics**: Calculate exact Bit Error Rate (BER) and bit accuracy percentages from binary sequences.
- **Interactive Visualizations**: Provide time-domain waveform graphs, dual-channel comparison views, and digital step plots highlighting bit discrepancies.

---

## 4. Key Features

- **End-to-End Simulation**: Complete transmitter, channel, receiver, and performance evaluation pipeline.
- **Three Modulation Techniques**: Full mathematical implementations of ASK, FSK, and BPSK.
- **Full UTF-8 Support**: Transmits and recovers English text, spaces, punctuation, numbers, accented letters, and multilingual Unicode characters.
- **Tunable AWGN Channel**: Adjustable SNR slider from 0 dB (heavy noise) to 30 dB (clean channel).
- **Robust Receiver Demodulation**: Matched-filter correlation algorithms with mathematically optimal decision thresholds.
- **Detailed Performance Analytics**: Real-time calculation of transmitted bits, recovered bits, bit error count, BER, and accuracy percentage.
- **Interactive Visualizations**:
  - Clean modulated carrier waveform.
  - Noisy received signal waveform.
  - Side-by-side synchronized signal comparison.
  - Synchronized digital step plots with red markers pinpointing bit discrepancies.
- **Beginner-Friendly Web Interface**: Clean, responsive Streamlit dashboard with real-time feedback and state tracking.
- **Comprehensive Unit Testing**: Automated test suite with 74 tests covering all modules and edge cases.

---

## 5. Technologies Used

- **Python 3**: Core language used for data manipulation, numerical algorithms, and object modeling.
- **Streamlit**: Web application framework providing the interactive graphical dashboard and real-time controls.
- **NumPy**: High-performance array operations for signal synthesis, time vectors, and stochastic noise generation.
- **Matplotlib**: Generation of 2D time-domain waveform plots and comparative step charts.
- **SciPy**: Scientific routines and signal processing utilities.
- **unittest**: Python's standard testing framework for comprehensive automated validation.

---

## 6. Explanation of the Simulation Workflow

The simulator executes a sequential, deterministic digital communication pipeline:

```text
[Input Text Message]
       │ (1. Encoding)
       ▼
[UTF-8 Binary Bitstream (0s and 1s)]
       │ (2. Modulation: ASK / FSK / BPSK)
       ▼
[Clean Transmitted Waveform s(t)]
       │ (3. Wireless Channel: AWGN at SNR dB)
       ▼
[Received Noisy Waveform y(t) = s(t) + w(t)]
       │ (4. Coherent Demodulation)
       ▼
[Recovered Binary Bitstream]
       ├─────────────────────────────────┐
       │ (5. Decoding)                   │ (6. Performance Analysis)
       ▼                                 ▼
[Recovered Text Message]          [Bit Errors, BER, Accuracy %]
       │                                 │
       └────────────────┬────────────────┘
                        │ (7. Visualization)
                        ▼
            [Interactive Dashboard]
```

1. **Text-to-Binary Encoding**: Converts each character into UTF-8 bytes and extracts 8 bits per byte in Most-Significant-Bit (MSB) order.
2. **Digital Modulation**: Maps the bitstream into discrete-time sinusoidal waveforms based on the chosen modulation technique.
3. **Channel Propagation**: Calculates average signal power and injects zero-mean Gaussian noise scaled to the selected SNR.
4. **Receiver Demodulation**: Performs matched-filter correlation over each bit interval to recover the transmitted bits.
5. **Message Recovery**: Groups the recovered bits into bytes and decodes them back into UTF-8 text.
6. **Performance Analysis**: Compares the original and recovered bitstreams to evaluate bit errors, BER, and accuracy.
7. **Visualization**: Renders high-resolution waveform graphs and bit comparison step plots.

---

## 7. Mathematical Concepts Explained

### 7.1 Amplitude Shift Keying (ASK)
In ASK, digital bits modulate the amplitude of a constant-frequency sinusoidal carrier wave:
$$s(t) = \begin{cases} A\sin(2\pi f_c t), & \text{bit} = 1 \\ 0, & \text{bit} = 0 \end{cases}$$
- **Carrier Frequency ($f_c$):** $1000\text{ Hz}$
- **Peak Amplitude ($A$):** $1.0$
- **Demodulation:** Correlates received signal with local carrier reference $\sin(2\pi f_c t)$ and compares against threshold $\frac{A}{2} \sum \sin^2(2\pi f_c t)$.
- **Characteristics:** Simplest to implement, but highly sensitive to amplitude noise.

### 7.2 Frequency Shift Keying (FSK)
In FSK, digital bits switch the transmission frequency between two discrete frequencies:
$$s(t) = A\sin(2\pi f_b t), \quad f_b = \begin{cases} f_1 = 1500\text{ Hz}, & \text{bit} = 1 \\ f_0 = 500\text{ Hz}, & \text{bit} = 0 \end{cases}$$
- **Demodulation:** Dual-branch matched filters calculate correlation with $f_0$ and $f_1$; the stronger branch wins.
- **Characteristics:** Constant envelope provides superior resistance against amplitude-based channel noise.

### 7.3 Binary Phase Shift Keying (BPSK)
In BPSK, digital bits modulate the phase of the carrier wave by $180^\circ$ ($\pi$ radians):
$$s(t) = A\sin(2\pi f_c t + \phi_b), \quad \phi_b = \begin{cases} 0, & \text{bit} = 1 \implies +A\sin(2\pi f_c t) \\ \pi, & \text{bit} = 0 \implies -A\sin(2\pi f_c t) \end{cases}$$
- **Demodulation:** Coherent correlation with $\sin(2\pi f_c t)$ using a zero-crossing decision boundary ($r_k \ge 0 \implies 1$).
- **Characteristics:** Highest power efficiency and lowest error rate in AWGN channels among binary modulation schemes.

### 7.4 Additive White Gaussian Noise (AWGN)
AWGN simulates thermal noise present in all physical communication channels:
$$y[n] = x[n] + w[n], \quad w[n] \sim \mathcal{N}(0, \sigma_w^2)$$
- The noise samples are independent, zero-mean, and normally distributed.

### 7.5 Signal-to-Noise Ratio (SNR)
SNR measures the ratio of signal power to noise power in decibels:
$$\text{SNR}_{\text{linear}} = 10^{\frac{\text{SNR}_{\text{dB}}}{10}}, \quad P_w = \frac{P_x}{\text{SNR}_{\text{linear}}}, \quad \sigma_w = \sqrt{P_w}$$
- **Lower SNR (e.g., 0–10 dB):** Severe noise; higher likelihood of bit flips and corrupted characters.
- **Higher SNR (e.g., 20–30 dB):** Clean transmission; signals are preserved with near-zero or zero errors.

### 7.6 Bit Error Rate (BER) & Bit Accuracy
- **Bit Error Rate (BER):**
  $$\text{BER} = \frac{\text{Number of bit errors}}{\text{Total number of transmitted bits}}$$
- **Bit Accuracy Percentage:**
  $$\text{Accuracy (\%)} = (1.0 - \text{BER}) \times 100.0$$

---

## 8. Project Folder Structure

```text
srwc/
├── .gitignore               # Ignored files (virtual environment, cache, bytecode)
├── .vscode/                 # VS Code workspace configuration
│   └── settings.json        # Auto-selects .venv Python interpreter
├── app.py                   # Main Streamlit web application
├── docs/                    # Technical architecture & mathematical notes
│   └── README.md
├── requirements.txt         # Project dependencies
├── README.md                # Comprehensive user guide and documentation
├── src/                     # Core simulation modules
│   ├── __init__.py          # Source package initializer
│   ├── channel.py           # AWGN channel noise simulation
│   ├── demodulation.py      # Coherent matched-filter demodulators
│   ├── encoding.py          # UTF-8 text-to-binary conversion
│   ├── metrics.py           # BER and accuracy performance analysis
│   ├── modulation.py        # ASK, FSK, and BPSK modulation algorithms
│   └── visualization.py     # Matplotlib waveform plotting helpers
└── tests/                   # Automated unit testing suite (74 tests)
    ├── test_channel.py      # Channel noise tests (13 tests)
    ├── test_demodulation.py # Demodulator tests (14 tests)
    ├── test_encoding.py     # Baseband encoding tests (12 tests)
    ├── test_metrics.py      # BER and accuracy tests (15 tests)
    ├── test_modulation.py   # Modulation waveform tests (12 tests)
    └── test_visualization.py# Plotting and figure tests (8 tests)
```

---

## 9. Setup and Installation Instructions

### Prerequisites
- **Operating System:** Windows 10 or Windows 11
- **Python Version:** Python 3.10+ (tested on Python 3.14)
- **Editor:** Visual Studio Code (recommended)

### Step-by-Step Installation (PowerShell)

1. **Open the Project Folder in VS Code:**
   Open VS Code and use `File` $\rightarrow$ `Open Folder` to select the project directory, or in terminal:
   ```powershell
   cd c:\Users\kunje\OneDrive\Desktop\Projects\srwc
   ```

2. **Create a Python Virtual Environment:**
   ```powershell
   python -m venv .venv
   ```

3. **Activate the Virtual Environment:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```
   > **PowerShell Execution Policy Tip:** If Windows blocks script execution with an execution policy error, temporarily allow scripts for the current terminal session by running:
   > ```powershell
   > Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   > ```
   > *(This adjusts the policy for the active terminal process only, without altering system-wide Windows security settings).*

4. **Upgrade pip & Install Dependencies:**
   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

---

## 10. How to Run the Application

With the virtual environment activated, launch the Streamlit app:

```powershell
python -m streamlit run app.py
```

Streamlit will launch a local web server and output:
```text
Local URL: http://localhost:8501
Network URL: http://...
```
Open `http://localhost:8501` in your browser. To stop the application at any time, press **`Ctrl + C`** in your terminal.

---

## 11. How to Run Unit Tests

Execute the automated test suite using Python's built-in `unittest` runner:

```powershell
python -m unittest discover -s tests -v
```

To run a specific module test suite:
```powershell
# Test encoding module
python -m unittest discover -s tests -p "test_encoding.py" -v

# Test modulation module
python -m unittest discover -s tests -p "test_modulation.py" -v

# Test channel module
python -m unittest discover -s tests -p "test_channel.py" -v

# Test demodulation module
python -m unittest discover -s tests -p "test_demodulation.py" -v

# Test metrics module
python -m unittest discover -s tests -p "test_metrics.py" -v

# Test visualization module
python -m unittest discover -s tests -p "test_visualization.py" -v
```

---

## 12. Example Usage Walkthrough

1. **Open the App**: Launch `python -m streamlit run app.py` and open the browser.
2. **Enter Message**: Type `Hello Wireless World!` into the text area.
3. **Select Modulation**: Choose **BPSK — Binary Phase Shift Keying**.
4. **Set Channel SNR**: Adjust the SNR slider to `25 dB` (low noise).
5. **Click Transmit Message**:
   - The app encodes the text into 168 UTF-8 bits.
   - Generates a modulated carrier waveform with 16,800 discrete samples.
   - Passes the waveform through the simulated AWGN channel.
   - Demodulates the received signal using coherent correlation.
   - Recovers the message: `Hello Wireless World!` with **0 bit errors (100% accuracy, BER: 0.0000)**.
6. **Simulate Channel Degradation**: Drag the slider down to `5 dB` and re-transmit:
   - Observe visible noise ripples on the waveform in the **Signal Comparison** tab.
   - Check the **Bit Comparison** tab to see red 'X' markers indicating noise-flipped bits.
   - Observe that the BER increases (e.g., BER: 0.0417, Accuracy: 95.83%).

---

## 13. System Limitations

- **Software Simulation Only:** Operates entirely mathematically; no physical electromagnetic propagation occurs.
- **Coherent Synchronization Assumption:** Assumes an ideally synchronized local carrier frequency and phase at the receiver. Carrier frequency offset (CFO) and phase jitter are not simulated.
- **Flat AWGN Channel:** Models thermal Gaussian noise only. Frequency-selective fading, multipath reflections, and Doppler shifts are not simulated.
- **Fixed Sampling Rate:** Sampling frequency is fixed at $10,000\text{ Hz}$ with $100\text{ samples/bit}$ to maintain computational efficiency.

---

## 14. Future Improvements

- **Multipath Fading Channels:** Introduce Rayleigh and Rician fading channel models.
- **Higher-Order Modulations:** Add QPSK, 16-QAM, and 64-QAM constellation simulations.
- **Forward Error Correction (FEC):** Implement Hamming codes or Reed-Solomon block codes to demonstrate error correction.
- **Constellation Diagrams:** Add I/Q scatter constellation plots for received symbols.
- **Non-Coherent Demodulation:** Implement envelope detection for ASK and non-coherent FSK.

---

## 15. Conclusion

The **Wireless Digital Signal Modulation and Transmission Simulator** provides an accessible, rigorous, and visually engaging educational platform for studying digital communications. By simulating the full journey from raw text to modulated carrier waves, noisy transmission channels, coherent receiver recovery, and quantitative performance metrics, this project bridges the gap between communication theory and interactive practice.
