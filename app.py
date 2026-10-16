"""Wireless Digital Signal Modulation and Transmission Simulator.

Interactive Academic Web Application | Software-Based Digital Wireless Communication Simulator
This module provides a modern, high-aesthetic Streamlit simulation dashboard.
It models the complete end-to-end communication pipeline:
1. Baseband UTF-8 text-to-binary encoding
2. Digital carrier modulation (ASK, FSK, BPSK)
3. Simulated AWGN channel degradation with tunable SNR
4. Coherent matched-filter receiver demodulation
5. Message recovery and Bit Error Rate (BER) analytics
6. High-resolution oscilloscope waveform and bitstream visualizations
"""

import io
from typing import Any, Dict, List, Optional
import matplotlib.pyplot as plt
import numpy as np
import scipy.io.wavfile as wavfile
import streamlit as st

from src.channel import add_awgn
from src.demodulation import ask_demodulate, bpsk_demodulate, fsk_demodulate
from src.encoding import bits_to_text, format_bits_for_display, text_to_bits
from src.metrics import analyze_transmission
from src.modulation import ask_modulate, bpsk_modulate, fsk_modulate
from src.visualization import (
    plot_bit_comparison,
    plot_modulated_signal,
    plot_received_signal,
    plot_signal_comparison,
)


def _generate_wav_bytes(waveform: np.ndarray, sample_rate: int = 10000) -> bytes:
    """Generate in-memory WAV audio bytes from a float waveform."""
    # Take at most 1 second of audio to keep playback snappy
    max_len = min(len(waveform), sample_rate)
    clip = waveform[:max_len]
    max_val = np.max(np.abs(clip))
    if max_val > 0:
        norm_clip = clip / max_val
    else:
        norm_clip = clip
    int16_data = (norm_clip * 30000.0).astype(np.int16)
    buf = io.BytesIO()
    wavfile.write(buf, sample_rate, int16_data)
    return buf.getvalue()


def _inject_custom_styles() -> None:
    """Inject custom CSS design system with futuristic glassmorphic aesthetics."""
    st.markdown(
        """
        <style>
        /* Google Fonts Import */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

        /* Global Typography */
        html, body, [class*="css"] {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
            color: #f1f5f9;
        }

        h1, h2, h3, h4, h5, h6 {
            font-family: 'Outfit', sans-serif !important;
            letter-spacing: -0.02em;
        }

        code, pre, .stCodeBlock {
            font-family: 'JetBrains Mono', monospace !important;
        }

        /* Hide Streamlit Deploy button and its modal trigger */
        .stAppDeployButton,
        [data-testid="stAppDeployButton"],
        div[data-testid="stAppDeployButton"] {
            display: none !important;
            visibility: hidden !important;
            opacity: 0 !important;
            pointer-events: none !important;
        }

        /* Hero Header Banner */
        .hero-banner {
            background: linear-gradient(135deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.8) 100%);
            border: 1px solid rgba(56, 189, 248, 0.22);
            border-radius: 20px;
            padding: 28px 32px;
            margin-bottom: 24px;
            box-shadow: 0 16px 36px -12px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.08);
            position: relative;
            overflow: hidden;
        }

        .hero-banner::before {
            content: "";
            position: absolute;
            top: -50px;
            right: -50px;
            width: 200px;
            height: 200px;
            background: radial-gradient(circle, rgba(56, 189, 248, 0.18) 0%, rgba(0, 0, 0, 0) 70%);
            border-radius: 50%;
            pointer-events: none;
        }

        .hero-pill {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            background: rgba(56, 189, 248, 0.12);
            border: 1px solid rgba(56, 189, 248, 0.35);
            color: #38bdf8;
            padding: 4px 14px;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 12px;
        }

        .pulse-dot {
            width: 7px;
            height: 7px;
            background-color: #38bdf8;
            border-radius: 50%;
            box-shadow: 0 0 10px #38bdf8;
            animation: pulse-glow 2s infinite;
        }

        @keyframes pulse-glow {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(56, 189, 248, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(56, 189, 248, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(56, 189, 248, 0); }
        }

        .hero-title {
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, #ffffff 0%, #cbd5e1 50%, #38bdf8 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin: 0 0 10px 0;
            line-height: 1.2;
        }

        .hero-desc {
            color: #94a3b8;
            font-size: 0.95rem;
            line-height: 1.55;
            margin: 0 0 16px 0;
            max-width: 900px;
        }

        .hero-chips {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }

        .hero-chip {
            background: rgba(2, 6, 23, 0.6);
            border: 1px solid rgba(148, 163, 184, 0.15);
            padding: 5px 12px;
            border-radius: 8px;
            font-size: 0.8rem;
            color: #cbd5e1;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        /* Glassmorphic Cards */
        .glass-card {
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(12px);
            border: 1px solid rgba(56, 189, 248, 0.14);
            border-radius: 16px;
            padding: 20px 24px;
            margin-bottom: 20px;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
            transition: border-color 0.25s ease, transform 0.25s ease;
        }

        .glass-card:hover {
            border-color: rgba(56, 189, 248, 0.35);
        }

        .card-header-title {
            font-size: 1.05rem;
            font-weight: 700;
            color: #f8fafc;
            display: flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 14px;
        }

        /* Status & Metric Badges */
        .badge-success {
            background: rgba(16, 185, 129, 0.15);
            border: 1px solid rgba(16, 185, 129, 0.35);
            color: #34d399;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge-warning {
            background: rgba(245, 158, 11, 0.15);
            border: 1px solid rgba(245, 158, 11, 0.35);
            color: #fbbf24;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        .badge-error {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.35);
            color: #f87171;
            padding: 4px 10px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 600;
        }

        /* KPI Metric Cards Grid */
        .kpi-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
            gap: 12px;
            margin: 16px 0;
        }

        .kpi-card {
            background: rgba(11, 19, 41, 0.85);
            border: 1px solid rgba(56, 189, 248, 0.18);
            border-radius: 12px;
            padding: 14px 16px;
            text-align: center;
            transition: all 0.2s ease;
        }

        .kpi-card:hover {
            border-color: #38bdf8;
            transform: translateY(-2px);
        }

        .kpi-label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: #94a3b8;
            margin-bottom: 4px;
        }

        .kpi-val {
            font-size: 1.4rem;
            font-weight: 700;
            font-family: 'Outfit', sans-serif;
            color: #ffffff;
        }

        .kpi-sub {
            font-size: 0.7rem;
            color: #64748b;
            margin-top: 2px;
        }

        /* Primary Button Styling */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
            border: 1px solid #38bdf8 !important;
            color: #ffffff !important;
            font-weight: 700 !important;
            font-size: 1.05rem !important;
            padding: 0.65rem 1.5rem !important;
            border-radius: 12px !important;
            box-shadow: 0 6px 20px -4px rgba(2, 132, 199, 0.5) !important;
            transition: all 0.25s ease !important;
        }

        div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%) !important;
            box-shadow: 0 8px 25px -3px rgba(56, 189, 248, 0.7) !important;
            transform: translateY(-1px) !important;
        }

        /* Preset Scenario Buttons */
        .preset-container {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }

        /* Monospace Bit Container */
        .bitstream-box {
            background: #020617;
            border: 1px solid #1e293b;
            border-radius: 10px;
            padding: 12px 14px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            color: #38bdf8;
            max-height: 120px;
            overflow-y: auto;
            word-break: break-all;
            line-height: 1.6;
        }

        /* Footer */
        .footer-text {
            text-align: center;
            color: #64748b;
            font-size: 0.85rem;
            margin-top: 36px;
            padding-bottom: 20px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_hero_header() -> None:
    """Render high-tech header banner with academic and telemetry highlights."""
    st.markdown(
        """
        <div class="hero-banner">
            <div class="hero-pill">
                <span class="pulse-dot"></span> Signal Telemetry Online • Academic Lab v1.2
            </div>
            <h1 class="hero-title">Wireless Signal Modulation & Transmission Simulator</h1>
            <p class="hero-desc">
                An end-to-end computational laboratory modeling the fundamental stages of digital wireless telecommunication:
                Baseband UTF-8 encoding, sinusoidal carrier modulation (<strong>ASK</strong>, <strong>FSK</strong>, <strong>BPSK</strong>),
                stochastic <strong>AWGN channel propagation</strong>, coherent matched-filter demodulation,
                and quantitative <strong>Bit Error Rate (BER)</strong> evaluation.
            </p>
            <div class="hero-chips">
                <div class="hero-chip">📡 <strong>Carrier:</strong> 1000 Hz / 1500 Hz</div>
                <div class="hero-chip">⚡ <strong>Sampling Rate:</strong> 10,000 Hz</div>
                <div class="hero-chip">📶 <strong>Symbol Rate:</strong> 1000 Baud</div>
                <div class="hero-chip">🎛️ <strong>Modes:</strong> ASK • FSK • BPSK</div>
                <div class="hero-chip">🛰️ <strong>Channel:</strong> AWGN (0 – 30 dB)</div>
                <div class="hero-chip">💻 <strong>Purity:</strong> 100% Software Math (No RF Hardware)</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    """Render the enhanced Streamlit user interface and simulation dashboard."""
    # -------------------------------------------------------------------------
    # Page Configuration & Styles
    # -------------------------------------------------------------------------
    st.set_page_config(
        page_title="Wireless Signal Modulation & Transmission Simulator",
        page_icon="📡",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    _inject_custom_styles()
    _render_hero_header()

    # Initialize session state keys if not present
    if "input_message" not in st.session_state:
        st.session_state["input_message"] = "Hello Wireless World!"
    if "modulation_index" not in st.session_state:
        st.session_state["modulation_index"] = 0
    if "snr_slider_val" not in st.session_state:
        st.session_state["snr_slider_val"] = 20

    # -------------------------------------------------------------------------
    # Main 2-Column Responsive Layout
    # -------------------------------------------------------------------------
    col_input, col_results = st.columns([1, 1.08], gap="large")

    # =========================================================================
    # LEFT COLUMN: Transmission Configuration & Transmitter Controls
    # =========================================================================
    with col_input:
        st.markdown(
            """
            <div class="card-header-title">
                ⚙️ <span>Transmission Control Station</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # ---------------------------------------------------------------------
        # Quick-Pick Educational Presets
        # ---------------------------------------------------------------------
        st.markdown("###### 🎯 Quick-Pick Simulation Scenarios")
        col_p1, col_p2, col_p3, col_p4 = st.columns(4)

        with col_p1:
            if st.button("⚡ Clean BPSK", help="BPSK @ 25 dB: High immunity, 0 errors", use_container_width=True):
                st.session_state["input_message"] = "Wireless Telemetry 2026"
                st.session_state["modulation_index"] = 2  # BPSK
                st.session_state["snr_slider_val"] = 25
                st.rerun()

        with col_p2:
            if st.button("🌪️ Noisy FSK", help="FSK @ 10 dB: Moderate channel degradation", use_container_width=True):
                st.session_state["input_message"] = "Deep Space Probe #7"
                st.session_state["modulation_index"] = 1  # FSK
                st.session_state["snr_slider_val"] = 10
                st.rerun()

        with col_p3:
            if st.button("⚠️ Extreme ASK", help="ASK @ 3 dB: Severe amplitude noise & bit flips", use_container_width=True):
                st.session_state["input_message"] = "Signal Alert: High AWGN"
                st.session_state["modulation_index"] = 0  # ASK
                st.session_state["snr_slider_val"] = 3
                st.rerun()

        with col_p4:
            if st.button("🌐 Multilingual", help="Unicode & Emojis @ 22 dB", use_container_width=True):
                st.session_state["input_message"] = "Hello 🌍! 🛰️ Signal"
                st.session_state["modulation_index"] = 2  # BPSK
                st.session_state["snr_slider_val"] = 22
                st.rerun()

        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)

        # ---------------------------------------------------------------------
        # 1. Message Input Section
        # ---------------------------------------------------------------------
        with st.container(border=True):
            st.markdown("##### 1. Baseband Message Input")
            message_input = st.text_area(
                label="Message to Transmit (UTF-8 Plaintext):",
                value=st.session_state["input_message"],
                placeholder="Type your message here...",
                height=95,
                help="Enter any alphanumeric text, punctuation, symbols, or Unicode characters.",
            )

            # Keep session state updated with user edits
            st.session_state["input_message"] = message_input

            char_count = len(message_input)
            byte_count = len(message_input.encode("utf-8"))
            bit_count = byte_count * 8

            col_sub1, col_sub2, col_sub3 = st.columns(3)
            with col_sub1:
                st.caption(f"📝 Characters: **{char_count}**")
            with col_sub2:
                st.caption(f"💾 UTF-8 Bytes: **{byte_count}**")
            with col_sub3:
                st.caption(f"🔢 Total Bits: **{bit_count}**")

        # ---------------------------------------------------------------------
        # 2. Modulation Selection Section
        # ---------------------------------------------------------------------
        with st.container(border=True):
            st.markdown("##### 2. Carrier Modulation Scheme")
            modulation_options = [
                "ASK — Amplitude Shift Keying (fc = 1000 Hz)",
                "FSK — Frequency Shift Keying (f0 = 500 Hz, f1 = 1500 Hz)",
                "BPSK — Binary Phase Shift Keying (fc = 1000 Hz, Δθ = 180°)",
            ]

            selected_modulation = st.radio(
                label="Select Digital Modulation Scheme:",
                options=modulation_options,
                index=st.session_state["modulation_index"],
                help="Choose which wave characteristic (amplitude, frequency, or phase) is modulated by binary bits.",
            )
            # Sync index
            st.session_state["modulation_index"] = modulation_options.index(selected_modulation)

            if selected_modulation.startswith("ASK"):
                mod_badge = "<span class='badge-warning'>Amplitude Modulated</span>"
                mod_desc = (
                    "• <strong>Bit 1:</strong> Transmits carrier wave at amplitude <code>1.0</code>.<br>"
                    "• <strong>Bit 0:</strong> Zero carrier transmission (On-Off Keying).<br>"
                    "• <strong>Receiver:</strong> Matched-filter correlation with threshold <code>A / 2</code>.<br>"
                    "• <strong>Vulnerability:</strong> High susceptibility to additive amplitude noise."
                )
            elif selected_modulation.startswith("FSK"):
                mod_badge = "<span class='badge-success'>Frequency Modulated</span>"
                mod_desc = (
                    "• <strong>Bit 0:</strong> Carrier at <code>f0 = 500 Hz</code>.<br>"
                    "• <strong>Bit 1:</strong> Carrier at <code>f1 = 1500 Hz</code>.<br>"
                    "• <strong>Receiver:</strong> Dual-branch coherent correlation with tone energy detector.<br>"
                    "• <strong>Resilience:</strong> Constant envelope protects against amplitude variations."
                )
            else:
                mod_badge = "<span class='badge-success'>Phase Modulated (Optimum)</span>"
                mod_desc = (
                    "• <strong>Bit 1:</strong> Phase at <code>0°</code> (<code>+sin(2πfc t)</code>).<br>"
                    "• <strong>Bit 0:</strong> Phase at <code>180°</code> (<code>-sin(2πfc t)</code>).<br>"
                    "• <strong>Receiver:</strong> Coherent correlation with zero-crossing threshold.<br>"
                    "• <strong>Efficiency:</strong> Theoretical maximum power efficiency and lowest BER in AWGN."
                )

            st.markdown(
                f"""
                <div style="background: rgba(2, 6, 23, 0.5); border: 1px solid rgba(56, 189, 248, 0.15); border-radius: 10px; padding: 12px 14px; margin-top: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                        <span style="font-size: 0.82rem; font-weight: 600; color: #cbd5e1;">Scheme Characteristics:</span>
                        {mod_badge}
                    </div>
                    <div style="font-size: 0.82rem; color: #94a3b8; line-height: 1.5;">
                        {mod_desc}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ---------------------------------------------------------------------
        # 3. Channel Settings Section
        # ---------------------------------------------------------------------
        with st.container(border=True):
            st.markdown("##### 3. Wireless Channel Propagation (AWGN)")

            snr_value = st.slider(
                label="Channel Signal-to-Noise Ratio (SNR) in dB:",
                min_value=0,
                max_value=30,
                value=st.session_state["snr_slider_val"],
                step=1,
                help="Adjust the ratio of signal power to noise power. Higher SNR simulates a cleaner channel.",
            )
            st.session_state["snr_slider_val"] = snr_value

            if snr_value >= 20:
                channel_quality_html = """
                <span class="badge-success">🟢 Pristine Channel (20–30 dB)</span>
                <span style="font-size: 0.8rem; color: #94a3b8;">Near-zero or 0 bit errors expected.</span>
                """
            elif snr_value >= 10:
                channel_quality_html = """
                <span class="badge-warning">🟡 Moderate Channel Noise (10–19 dB)</span>
                <span style="font-size: 0.8rem; color: #94a3b8;">Occasional bit flips depending on modulation.</span>
                """
            else:
                channel_quality_html = """
                <span class="badge-error">🔴 Severe Impairment (0–9 dB)</span>
                <span style="font-size: 0.8rem; color: #94a3b8;">High BER; frequent byte corruption anticipated.</span>
                """

            st.markdown(
                f"""
                <div style="display: flex; align-items: center; justify-content: space-between; background: rgba(2, 6, 23, 0.5); padding: 8px 12px; border-radius: 8px; border: 1px solid rgba(148, 163, 184, 0.1); margin-top: 6px;">
                    {channel_quality_html}
                </div>
                """,
                unsafe_allow_html=True,
            )

        # ---------------------------------------------------------------------
        # Transmit Button
        # ---------------------------------------------------------------------
        transmit_clicked = st.button(
            "🚀 Transmit Signal & Simulate Channel",
            type="primary",
            use_container_width=True,
        )

        # Handle simulation execution
        if transmit_clicked:
            trimmed_message = message_input.strip()
            if not trimmed_message:
                st.session_state["simulation_active"] = False
                st.session_state["last_submitted_text"] = ""
                st.error("⚠️ **Validation Error:** Please enter a valid non-empty text message.")
            else:
                try:
                    # 1. Text to binary conversion
                    tx_bits = text_to_bits(trimmed_message)

                    # 2. Modulate bits into digital carrier waveform
                    if selected_modulation.startswith("ASK"):
                        tx_waveform = ask_modulate(tx_bits)
                        mod_code = "ASK"
                    elif selected_modulation.startswith("FSK"):
                        tx_waveform = fsk_modulate(tx_bits)
                        mod_code = "FSK"
                    elif selected_modulation.startswith("BPSK"):
                        tx_waveform = bpsk_modulate(tx_bits)
                        mod_code = "BPSK"
                    else:
                        raise ValueError(f"Unknown modulation: {selected_modulation}")

                    duration_s = len(tx_waveform) / 10000.0

                    # 3. Channel AWGN noise injection
                    rx_noisy_waveform = add_awgn(tx_waveform, snr_db=float(snr_value))

                    # 4. Receiver demodulation
                    if mod_code == "ASK":
                        rx_bits = ask_demodulate(rx_noisy_waveform)
                    elif mod_code == "FSK":
                        rx_bits = fsk_demodulate(rx_noisy_waveform)
                    elif mod_code == "BPSK":
                        rx_bits = bpsk_demodulate(rx_noisy_waveform)

                    # 5. Message decoding from recovered bits
                    decode_success = True
                    decode_error_msg = ""
                    try:
                        recovered_text = bits_to_text(rx_bits)
                    except UnicodeDecodeError as ude:
                        decode_success = False
                        recovered_text = ""
                        decode_error_msg = f"UTF-8 Decoding Error: Noise altered byte parity ({ude.reason})."
                    except Exception as exc:
                        decode_success = False
                        recovered_text = ""
                        decode_error_msg = f"Decoding Exception: {exc}"

                    # 6. Quantitative metrics
                    try:
                        metrics_summary = analyze_transmission(tx_bits, rx_bits)
                    except Exception as m_err:
                        metrics_summary = {
                            "total_bits": len(tx_bits),
                            "recovered_bits": len(rx_bits),
                            "bit_errors": -1,
                            "ber": -1.0,
                            "accuracy_percent": -1.0,
                            "error": str(m_err),
                        }

                    # Store simulation state
                    st.session_state["simulation_active"] = True
                    st.session_state["last_submitted_text"] = message_input
                    st.session_state["tx_message"] = trimmed_message
                    st.session_state["tx_bits"] = tx_bits
                    st.session_state["tx_waveform"] = tx_waveform
                    st.session_state["rx_noisy_waveform"] = rx_noisy_waveform
                    st.session_state["rx_bits"] = rx_bits
                    st.session_state["recovered_text"] = recovered_text
                    st.session_state["decode_success"] = decode_success
                    st.session_state["decode_error_msg"] = decode_error_msg
                    st.session_state["metrics"] = metrics_summary
                    st.session_state["mod_code"] = mod_code
                    st.session_state["mod_name"] = selected_modulation
                    st.session_state["duration_s"] = duration_s
                    st.session_state["snr_db"] = snr_value

                except Exception as exc:
                    st.session_state["simulation_active"] = False
                    st.error(f"⚠️ **Simulation Error:** {exc}")

        # Check if the text input has been modified since the last submission
        last_submitted = st.session_state.get("last_submitted_text", None)
        simulation_active = st.session_state.get("simulation_active", False)

        if simulation_active and message_input != last_submitted:
            st.warning(
                "⚠️ **Input Modified:** The text in the input box has changed. "
                "Click **🚀 Transmit Signal** to refresh the simulation.",
                icon="⚠️",
            )
            simulation_active = False

    # =========================================================================
    # RIGHT COLUMN: Results Dashboard, Telemetry & Oscilloscope
    # =========================================================================
    with col_results:
        st.markdown(
            """
            <div class="card-header-title">
                📊 <span>Receiver Telemetry & Analytics Dashboard</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if simulation_active:
            m = st.session_state.get("metrics", {})
            orig_msg = st.session_state["tx_message"]
            rec_msg = st.session_state["recovered_text"]
            decode_ok = st.session_state["decode_success"]
            err_msg = st.session_state["decode_error_msg"]
            mod_code = st.session_state["mod_code"]
            snr_cur = st.session_state["snr_db"]
            bit_errors = m.get("bit_errors", 0)
            ber = m.get("ber", 0.0)
            accuracy = m.get("accuracy_percent", 100.0)

            # -----------------------------------------------------------------
            # Live Status Alert Banner
            # -----------------------------------------------------------------
            if bit_errors == 0 and decode_ok:
                st.markdown(
                    f"""
                    <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.35); border-radius: 12px; padding: 12px 18px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 1.3rem;">🎯</span>
                            <div>
                                <div style="font-weight: 700; color: #34d399; font-size: 0.95rem;">PERFECT TRANSMISSION & RECOVERY</div>
                                <div style="font-size: 0.8rem; color: #94a3b8;">100.0% Bit Accuracy • 0 Bit Flips • Modulation: {mod_code} at {snr_cur} dB SNR</div>
                            </div>
                        </div>
                        <span class="badge-success">0 ERRORS</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            elif decode_ok:
                st.markdown(
                    f"""
                    <div style="background: rgba(245, 158, 11, 0.12); border: 1px solid rgba(245, 158, 11, 0.35); border-radius: 12px; padding: 12px 18px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 1.3rem;">⚠️</span>
                            <div>
                                <div style="font-weight: 700; color: #fbbf24; font-size: 0.95rem;">PARTIAL TRANSMISSION RECOVERY</div>
                                <div style="font-size: 0.8rem; color: #94a3b8;">{bit_errors} bit errors occurred (BER = {ber:.4f}) • Text recovered with minor alterations</div>
                            </div>
                        </div>
                        <span class="badge-warning">{accuracy:.1f}% ACCURACY</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            else:
                st.markdown(
                    f"""
                    <div style="background: rgba(239, 68, 68, 0.12); border: 1px solid rgba(239, 68, 68, 0.35); border-radius: 12px; padding: 12px 18px; margin-bottom: 16px; display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 10px;">
                            <span style="font-size: 1.3rem;">💥</span>
                            <div>
                                <div style="font-weight: 700; color: #f87171; font-size: 0.95rem;">SEVERE CHANNEL DEGRADATION</div>
                                <div style="font-size: 0.8rem; color: #94a3b8;">{bit_errors} bit flips corrupted byte boundaries • {err_msg}</div>
                            </div>
                        </div>
                        <span class="badge-error">{accuracy:.1f}% ACCURACY</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # -----------------------------------------------------------------
            # KPI Cards Grid
            # -----------------------------------------------------------------
            st.markdown(
                f"""
                <div class="kpi-container">
                    <div class="kpi-card">
                        <div class="kpi-label">Transmitted</div>
                        <div class="kpi-val" style="color: #38bdf8;">{m['total_bits']}</div>
                        <div class="kpi-sub">Total Bits (Tx)</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Demodulated</div>
                        <div class="kpi-val" style="color: #cbd5e1;">{m['recovered_bits']}</div>
                        <div class="kpi-sub">Bits Received</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Bit Errors</div>
                        <div class="kpi-val" style="color: {'#34d399' if bit_errors == 0 else '#f87171'};">{bit_errors}</div>
                        <div class="kpi-sub">Mismatched Bits</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">BER</div>
                        <div class="kpi-val" style="color: {'#34d399' if ber == 0 else '#fbbf24'};">{ber:.4f}</div>
                        <div class="kpi-sub">Bit Error Rate</div>
                    </div>
                    <div class="kpi-card">
                        <div class="kpi-label">Accuracy</div>
                        <div class="kpi-val" style="color: {'#34d399' if accuracy == 100 else '#38bdf8'};">{accuracy:.1f}%</div>
                        <div class="kpi-sub">Transmission Health</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # Accuracy Progress Bar
            st.progress(max(0.0, min(1.0, float(accuracy) / 100.0)))

            # -----------------------------------------------------------------
            # Side-by-Side Message Comparison Cards
            # -----------------------------------------------------------------
            col_msg_tx, col_msg_rx = st.columns(2)
            with col_msg_tx:
                with st.container(border=True):
                    st.markdown("###### 📤 Original Transmitted Message")
                    st.code(orig_msg, language="text")
                    st.caption(f"Encoding: **UTF-8** • Length: **{len(orig_msg)} characters**")

            with col_msg_rx:
                with st.container(border=True):
                    st.markdown("###### 📥 Demodulated Recovered Message")
                    if decode_ok:
                        st.code(rec_msg, language="text")
                        if rec_msg == orig_msg:
                            st.caption("✅ **Identical Content:** Perfect string equality.")
                        else:
                            st.caption("⚠️ **Altered:** Noise changed 1 or more characters.")
                    else:
                        st.error("⚠️ Byte framing error: Corrupted by AWGN noise.")
                        st.caption("Raw bitstream recovered below remains available.")

            # -----------------------------------------------------------------
            # Audio Carrier Listening Synthesizer
            # -----------------------------------------------------------------
            with st.container(border=True):
                col_aud1, col_aud2 = st.columns([1.2, 1])
                with col_aud1:
                    st.markdown("###### 🎧 Audible Carrier Waveform Synthesizer")
                    st.caption(
                        "Listen to the audible carrier wave synthesized directly from your simulated signal samples (10 kHz sampling). "
                        "Notice the pitch difference in FSK, envelope pauses in ASK, and phase shifts in BPSK."
                    )
                with col_aud2:
                    tx_waveform = st.session_state["tx_waveform"]
                    audio_wav_bytes = _generate_wav_bytes(tx_waveform, sample_rate=10000)
                    st.audio(audio_wav_bytes, format="audio/wav")

            # -----------------------------------------------------------------
            # Visual Oscilloscope Waveform & Bitstream Tabs
            # -----------------------------------------------------------------
            with st.container(border=True):
                st.markdown("##### 🔬 Oscilloscope Waveform Visualizations")
                rx_noisy = st.session_state["rx_noisy_waveform"]
                tx_bits = st.session_state["tx_bits"]
                rx_bits = st.session_state["rx_bits"]
                sample_rate = 10000.0

                # Max samples to plot for clear sinusoidal resolution
                plot_samples = min(800, len(tx_waveform))
                plot_bits_count = min(64, len(tx_bits))

                tab_tx, tab_rx, tab_comp, tab_bits, tab_raw = st.tabs([
                    "📡 Transmitted Signal",
                    "⚡ Channel Output (AWGN)",
                    "🔍 Dual-Trace Comparison",
                    "🔢 Bit Step Plot",
                    "💾 Raw Bitstreams",
                ])

                with tab_tx:
                    fig_tx = plot_modulated_signal(
                        tx_waveform,
                        sample_rate=sample_rate,
                        title=f"{mod_code} Modulated Carrier Waveform (Transmitter Output)",
                        max_samples=plot_samples,
                    )
                    st.pyplot(fig_tx)
                    plt.close(fig_tx)
                    st.caption(
                        f"Displaying first **{plot_samples} samples** ({plot_samples / sample_rate * 1000:.1f} ms) "
                        f"out of {len(tx_waveform)} total samples for high-resolution sinusoidal wave inspection."
                    )

                with tab_rx:
                    fig_rx = plot_received_signal(
                        rx_noisy,
                        sample_rate=sample_rate,
                        title=f"Received {mod_code} Signal with Simulated AWGN Noise (SNR = {snr_cur} dB)",
                        max_samples=plot_samples,
                    )
                    st.pyplot(fig_rx)
                    plt.close(fig_rx)
                    st.caption(
                        f"Noisy waveform after traveling through AWGN channel with SNR = **{snr_cur} dB**."
                    )

                with tab_comp:
                    fig_comp = plot_signal_comparison(
                        tx_waveform,
                        rx_noisy,
                        sample_rate=sample_rate,
                        max_samples=plot_samples,
                    )
                    st.pyplot(fig_comp)
                    plt.close(fig_comp)
                    st.caption(
                        "Synchronized dual-trace display showing clean carrier (top) vs. noise-corrupted signal with reference overlay (bottom)."
                    )

                with tab_bits:
                    fig_bits = plot_bit_comparison(
                        tx_bits,
                        rx_bits,
                        max_bits=plot_bits_count,
                    )
                    st.pyplot(fig_bits)
                    plt.close(fig_bits)
                    st.caption(
                        f"Synchronized digital step plot for first **{plot_bits_count} bits**. "
                        "Vibrant red 'X' markers pinpoint specific bit flip errors caused by channel noise."
                    )

                with tab_raw:
                    st.markdown("###### Transmitted Bitstream (UTF-8 Bytes):")
                    st.code(format_bits_for_display(tx_bits), language="text")
                    st.markdown("###### Demodulated Bitstream:")
                    st.code(format_bits_for_display(rx_bits), language="text")
        else:
            # Empty / Awaiting Transmission Placeholder
            st.markdown(
                """
                <div style="background: rgba(15, 23, 42, 0.4); border: 1px dashed rgba(56, 189, 248, 0.25); border-radius: 16px; padding: 48px 24px; text-align: center;">
                    <div style="font-size: 3rem; margin-bottom: 12px;">📡</div>
                    <div style="font-size: 1.15rem; font-weight: 700; color: #f1f5f9; margin-bottom: 6px;">
                        Awaiting Transmission Sequence
                    </div>
                    <div style="font-size: 0.88rem; color: #94a3b8; max-width: 440px; margin: 0 auto 20px auto; line-height: 1.5;">
                        Configure your message, modulation scheme, and channel SNR on the left, then click
                        <strong>Transmit Signal</strong> or select a <strong>Quick-Pick Scenario</strong> above to run the simulation.
                    </div>
                    <div style="display: inline-flex; gap: 8px; font-size: 0.8rem; color: #38bdf8; background: rgba(56, 189, 248, 0.1); padding: 6px 14px; border-radius: 9999px;">
                        ⚡ Matched Filters Ready • AWGN Channel Standing By
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    st.divider()

    # -------------------------------------------------------------------------
    # Educational Theory Section
    # -------------------------------------------------------------------------
    with st.expander("📚 Digital Modulation Theory & Analytical Mathematical Principles", expanded=False):
        col_ask_th, col_fsk_th, col_bpsk_th = st.columns(3)

        with col_ask_th:
            st.markdown(
                """
                #### Amplitude Shift Keying (ASK)
                $$s(t) = \\begin{cases} A\\sin(2\\pi f_c t), & \\text{bit} = 1 \\\\ 0, & \\text{bit} = 0 \\end{cases}$$
                - **Carrier ($f_c$):** 1000 Hz
                - **Decision Rule:** $r_k \\ge \\frac{A}{2} \\sum \\sin^2(2\\pi f_c t) \\implies 1$
                - **Trade-off:** Minimal circuit complexity, but highest sensitivity to channel noise and amplitude fading.
                """
            )

        with col_fsk_th:
            st.markdown(
                """
                #### Frequency Shift Keying (FSK)
                $$s(t) = A\\sin(2\\pi f_b t), \\quad f_b \\in \\{500\\text{ Hz}, 1500\\text{ Hz}\\}$$
                - **Tones ($f_0, f_1$):** 500 Hz (bit 0) vs. 1500 Hz (bit 1)
                - **Decision Rule:** $\\sum y[n]\\sin(2\\pi f_1 t) > \\sum y[n]\\sin(2\\pi f_0 t) \\implies 1$
                - **Trade-off:** Constant envelope provides superior immunity against amplitude perturbations.
                """
            )

        with col_bpsk_th:
            st.markdown(
                """
                #### Binary Phase Shift Keying (BPSK)
                $$s(t) = \\begin{cases} +A\\sin(2\\pi f_c t), & \\text{bit} = 1 \\\\ -A\\sin(2\\pi f_c t), & \\text{bit} = 0 \\end{cases}$$
                - **Phase Shift:** $\\Delta\\theta = 180^\\circ$ ($\\pi$ radians)
                - **Decision Rule:** Correlate with carrier; zero-crossing boundary ($r_k \\ge 0 \\implies 1$)
                - **Trade-off:** Optimum power efficiency and lowest theoretical Bit Error Rate in AWGN.
                """
            )

        st.markdown("---")
        st.markdown(
            """
            ##### Signal-to-Noise Ratio (SNR) & AWGN Formulation
            $$\\text{SNR}_{\\text{linear}} = 10^{\\frac{\\text{SNR}_{\\text{dB}}}{10}}, \\quad P_{\\text{noise}} = \\frac{P_{\\text{signal}}}{\\text{SNR}_{\\text{linear}}}, \\quad w[n] \\sim \\mathcal{N}(0, P_{\\text{noise}})$$
            All signal waveforms and noise samples are generated dynamically using discrete-time double-precision floating-point arithmetic.
            """
        )

    # -------------------------------------------------------------------------
    # Footer
    # -------------------------------------------------------------------------
    st.markdown(
        """
        <div class="footer-text">
            📡 <strong>Wireless Digital Signal Modulation and Transmission Simulator</strong><br>
            Academic Mini-Project | Software-Only Simulation | Developed with Python, Streamlit, NumPy, SciPy & Matplotlib
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
