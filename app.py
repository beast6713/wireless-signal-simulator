"""Wireless Digital Signal Modulation and Transmission Simulator.

Phase 7: Signal Visualization and Results Dashboard
Academic Mini-Project | Software-Based Wireless Communication Simulator

This module provides the complete Streamlit web application.
It integrates:
1. Text-to-binary encoding (UTF-8)
2. Carrier modulation (ASK, FSK, BPSK)
3. Simulated AWGN channel noise
4. Coherent receiver demodulation
5. Performance analysis (BER, accuracy, error count)
6. Comprehensive Matplotlib waveform and bitstream visualizations
"""

import matplotlib.pyplot as plt
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


def main() -> None:
    """Render the Streamlit user interface and simulation dashboard for Phase 7."""
    # -------------------------------------------------------------------------
    # A. Page Configuration
    # -------------------------------------------------------------------------
    st.set_page_config(
        page_title="Wireless Signal Simulator",
        page_icon="📡",
        layout="wide",
    )

    # Main Heading and Academic Description
    st.title("📡 Wireless Signal Modulation and Transmission Simulator")
    st.markdown(
        "This application is a **software-only academic simulation** of a digital wireless "
        "communication system. It models the complete end-to-end transmission pipeline: "
        "converting text into binary data, modulating carrier waveforms (ASK, FSK, BPSK), "
        "simulating noisy channel propagation (AWGN), coherent demodulation, "
        "and evaluating performance using Bit Error Rate (BER) and interactive waveform plots."
    )

    st.info(
        "ℹ️ **Simulation Notice:** All signals, noise, waveforms, demodulation, and performance "
        "metrics are computed mathematically in software. No physical hardware, microcontrollers, "
        "antennas, or actual radio transmitters are used.",
        icon="ℹ️",
    )

    st.divider()

    # -------------------------------------------------------------------------
    # Main Layout: 2 Equal Columns
    # -------------------------------------------------------------------------
    col_input, col_results = st.columns([1, 1], gap="large")

    # =========================================================================
    # LEFT COLUMN: Transmission Configuration
    # =========================================================================
    with col_input:
        # ---------------------------------------------------------------------
        # 1. Message Input Section
        # ---------------------------------------------------------------------
        st.subheader("1. Message Input")
        message_input = st.text_area(
            label="Enter Message to Transmit:",
            value="Hello Wireless World!",
            placeholder="Enter your message here...",
            height=110,
            help="Type any text message to simulate encoding and wireless transmission.",
        )

        transmit_clicked = st.button(
            "🚀 Transmit Message",
            type="primary",
            use_container_width=True,
        )

        st.markdown("---")

        # ---------------------------------------------------------------------
        # 2. Modulation Selection Section
        # ---------------------------------------------------------------------
        st.subheader("2. Modulation Settings")
        modulation_options = [
            "ASK — Amplitude Shift Keying",
            "FSK — Frequency Shift Keying",
            "BPSK — Binary Phase Shift Keying",
        ]

        selected_modulation = st.radio(
            label="Select Digital Modulation Technique:",
            options=modulation_options,
            index=0,  # ASK is the default option
            help="Choose the digital modulation technique to modulate the carrier signal.",
        )

        # Educational description based on selection
        if selected_modulation.startswith("ASK"):
            st.info(
                "**Technique Details (ASK):**\n\n"
                "In **Amplitude Shift Keying**, the amplitude of a constant-frequency carrier wave "
                "is varied in accordance with the binary data. Typically, bit `1` is represented by "
                "a high-amplitude carrier wave, while bit `0` is represented by zero amplitude (On-Off Keying).\n\n"
                "- Carrier Frequency ($f_c$): `1000 Hz`\n"
                "- Bit 1 Amplitude: `1.0` | Bit 0 Amplitude: `0.0`\n"
                "- Receiver: Matched-filter correlation with threshold $A/2$.",
                icon="📊",
            )
        elif selected_modulation.startswith("FSK"):
            st.info(
                "**Technique Details (FSK):**\n\n"
                "In **Frequency Shift Keying**, the frequency of the carrier wave switches between two "
                "distinct frequencies ($f_0$ for bit `0` and $f_1$ for bit `1`). The signal amplitude remains "
                "constant, offering better resilience against amplitude-based noise.\n\n"
                "- Bit 0 Frequency ($f_0$): `500 Hz`\n"
                "- Bit 1 Frequency ($f_1$): `1500 Hz`\n"
                "- Receiver: Dual-branch coherent correlation.",
                icon="📊",
            )
        elif selected_modulation.startswith("BPSK"):
            st.info(
                "**Technique Details (BPSK):**\n\n"
                "In **Binary Phase Shift Keying**, the phase of a constant-frequency carrier wave shifts by "
                "$180^\\circ$ ($\\pi$ radians) between bit `0` and bit `1`. BPSK provides superior power efficiency "
                "and noise immunity in digital communication systems.\n\n"
                "- Carrier Frequency ($f_c$): `1000 Hz`\n"
                "- Bit 1 Phase: $0^\\circ$ | Bit 0 Phase: $180^\\circ$ ($\\pi$ rad)\n"
                "- Receiver: Coherent phase correlation with zero-crossing decision boundary.",
                icon="📊",
            )

        st.markdown("---")

        # ---------------------------------------------------------------------
        # 3. Channel Settings Section
        # ---------------------------------------------------------------------
        st.subheader("3. Channel Settings")
        snr_value = st.slider(
            label="Signal-to-Noise Ratio (SNR) in dB",
            min_value=0,
            max_value=30,
            value=20,
            step=1,
            help="Set the ratio of signal power to noise power in decibels.",
        )

        st.caption(
            f"**Current SNR Setting:** `{snr_value} dB` — "
            "A lower SNR (e.g., 0–10 dB) simulates a severe, high-noise channel where bits are prone to corruption. "
            "A higher SNR (e.g., 20–30 dB) simulates a clean channel where signals remain sharp and easily recoverable."
        )

        # Handle simulation execution on button click
        if transmit_clicked:
            trimmed_message = message_input.strip()
            if not trimmed_message:
                st.session_state["simulation_active"] = False
                st.session_state["last_submitted_text"] = ""
                st.error(
                    "⚠️ **Validation Error:** The message cannot be empty or contain only whitespace. "
                    "Please enter a valid text message before transmitting."
                )
            else:
                try:
                    # 1. Text-to-binary conversion
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

                    # 3. Additive White Gaussian Noise (AWGN) channel
                    rx_noisy_waveform = add_awgn(tx_waveform, snr_db=float(snr_value))

                    # 4. Receiver demodulation
                    if mod_code == "ASK":
                        rx_bits = ask_demodulate(rx_noisy_waveform)
                    elif mod_code == "FSK":
                        rx_bits = fsk_demodulate(rx_noisy_waveform)
                    elif mod_code == "BPSK":
                        rx_bits = bpsk_demodulate(rx_noisy_waveform)

                    # 5. Message recovery from recovered bitstream
                    decode_success = True
                    decode_error_msg = ""
                    try:
                        recovered_text = bits_to_text(rx_bits)
                    except UnicodeDecodeError as ude:
                        decode_success = False
                        recovered_text = ""
                        decode_error_msg = f"UTF-8 Decoding Error: Noise corrupted byte boundaries ({ude.reason})."
                    except Exception as exc:
                        decode_success = False
                        recovered_text = ""
                        decode_error_msg = f"Decoding Exception: {exc}"

                    # 6. Quantitative performance metrics
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

                    st.success(
                        "✅ **Simulation Completed Successfully!**\n\n"
                        f"- Transmitted **{len(tx_bits)} bits** via **{mod_code}** at **SNR = {snr_value} dB**.\n"
                        f"- Demodulated **{len(rx_bits)} bits** | **Bit Errors:** `{metrics_summary['bit_errors']}` | "
                        f"**BER:** `{metrics_summary['ber']:.4f}` | **Accuracy:** `{metrics_summary['accuracy_percent']:.2f}%`.\n\n"
                        "*Note: This is an academic software simulation; no real RF transmission occurred.*"
                    )
                except Exception as exc:
                    st.session_state["simulation_active"] = False
                    st.error(f"⚠️ **Simulation Error:** {exc}")

        # Check if the text input has been modified since the last submission
        last_submitted = st.session_state.get("last_submitted_text", None)
        simulation_active = st.session_state.get("simulation_active", False)

        if simulation_active and message_input != last_submitted:
            st.warning(
                "⚠️ **Input Modified:** The text in the input box has changed since the last transmission. "
                "Click **🚀 Transmit Message** to update the simulation results.",
                icon="⚠️",
            )
            simulation_active = False

    # =========================================================================
    # RIGHT COLUMN: Results & Visualization Dashboard
    # =========================================================================
    with col_results:
        st.subheader("4. Simulation Results & Visualization")

        # ---------------------------------------------------------------------
        # Summary & Messages
        # ---------------------------------------------------------------------
        with st.container(border=True):
            st.markdown("##### 1. Transmission Overview & Original Message")
            if simulation_active:
                st.markdown(f"**Original Text Message:**")
                st.code(st.session_state["tx_message"], language="text")
                col_info1, col_info2, col_info3 = st.columns(3)
                with col_info1:
                    st.caption(f"**Modulation:** `{st.session_state['mod_code']}`")
                with col_info2:
                    st.caption(f"**Channel SNR:** `{st.session_state['snr_db']} dB`")
                with col_info3:
                    st.caption(f"**Duration:** `{st.session_state['duration_s']:.3f} s`")

                st.markdown("**Transmitted Bitstream (UTF-8):**")
                st.code(format_bits_for_display(st.session_state["tx_bits"]), language="text")
            else:
                st.text("Awaiting transmission... Enter a message and click 'Transmit Message'.")

        with st.container(border=True):
            st.markdown("##### 2. Demodulated Output & Recovered Message")
            if simulation_active:
                rx_bits = st.session_state["rx_bits"]
                orig_msg = st.session_state["tx_message"]
                rec_msg = st.session_state["recovered_text"]
                decode_ok = st.session_state["decode_success"]
                err_msg = st.session_state["decode_error_msg"]

                st.markdown(f"**Demodulated Bitstream:** (`{len(rx_bits)}` bits recovered)")
                st.code(format_bits_for_display(rx_bits), language="text")

                st.markdown("**Recovered Message:**")
                if decode_ok:
                    st.code(rec_msg, language="text")
                    if rec_msg == orig_msg:
                        st.success(
                            "🎉 **Perfect Message Recovery!** Demodulated text matches the original message exactly.",
                            icon="🎉",
                        )
                    else:
                        st.warning(
                            "⚠️ **Partial Message Recovery:** Valid UTF-8, but channel noise altered one or more characters.",
                            icon="⚠️",
                        )
                else:
                    st.error(
                        f"⚠️ **UTF-8 Decoding Error:** {err_msg}\n\n"
                        "Severe channel noise corrupted bit boundaries. The raw recovered bits above remain exact.",
                        icon="⚠️",
                    )
            else:
                st.text("[Pending Transmission: Submit a message to run demodulation and recovery]")

        # ---------------------------------------------------------------------
        # Performance Metrics
        # ---------------------------------------------------------------------
        with st.container(border=True):
            st.markdown("##### 3. Performance Metrics (Bit Error Rate & Accuracy)")
            if simulation_active:
                m = st.session_state.get("metrics", {})
                if m.get("bit_errors", -1) >= 0:
                    col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
                    with col_m1:
                        st.metric(label="Transmitted Bits", value=m["total_bits"])
                    with col_m2:
                        st.metric(label="Recovered Bits", value=m["recovered_bits"])
                    with col_m3:
                        st.metric(label="Bit Errors", value=m["bit_errors"])
                    with col_m4:
                        st.metric(label="BER", value=f"{m['ber']:.4f}")
                    with col_m5:
                        st.metric(label="Accuracy", value=f"{m['accuracy_percent']:.2f}%")

                    if m["bit_errors"] == 0:
                        st.success(
                            f"🎯 **Zero Bit Errors:** 100.0% accuracy achieved at SNR = {st.session_state['snr_db']} dB.",
                            icon="🎯",
                        )
                    else:
                        st.info(
                            f"📊 **Noise Degradation:** {m['bit_errors']} of {m['total_bits']} bits flipped by AWGN "
                            f"(BER = {m['ber']:.4f}).",
                            icon="📊",
                        )
                else:
                    st.error(f"⚠️ **Metrics Error:** {m.get('error', 'Length mismatch')}")
            else:
                st.text("[Pending Transmission: Submit a message to calculate performance metrics]")

        # ---------------------------------------------------------------------
        # Visual Signal Waveforms & Bitstream Dashboard
        # ---------------------------------------------------------------------
        with st.container(border=True):
            st.markdown("##### 4. Signal Waveform Visualizations")
            if simulation_active:
                tx_waveform = st.session_state["tx_waveform"]
                rx_noisy = st.session_state["rx_noisy_waveform"]
                tx_bits = st.session_state["tx_bits"]
                rx_bits = st.session_state["rx_bits"]
                mod_code = st.session_state["mod_code"]
                snr_cur = st.session_state["snr_db"]
                sample_rate = 10000.0

                # Max samples to plot for clear sinusoidal resolution (first 8 bits = 800 samples)
                plot_samples = min(800, len(tx_waveform))
                plot_bits_count = min(64, len(tx_bits))

                tab_tx, tab_rx, tab_comp, tab_bits = st.tabs([
                    "📡 Modulated Signal",
                    "⚡ Received Signal",
                    "🔍 Signal Comparison",
                    "🔢 Bit Comparison",
                ])

                with tab_tx:
                    fig_tx = plot_modulated_signal(
                        tx_waveform,
                        sample_rate=sample_rate,
                        title=f"{mod_code} Modulated Signal (Transmitter Output)",
                        max_samples=plot_samples,
                    )
                    st.pyplot(fig_tx)
                    plt.close(fig_tx)
                    st.caption(
                        f"Showing first {plot_samples} samples ({plot_samples / sample_rate * 1000:.1f} ms) "
                        f"out of {len(tx_waveform)} total samples for high-resolution waveform viewing."
                    )

                with tab_rx:
                    fig_rx = plot_received_signal(
                        rx_noisy,
                        sample_rate=sample_rate,
                        title=f"Received {mod_code} Signal with AWGN Noise (SNR = {snr_cur} dB)",
                        max_samples=plot_samples,
                    )
                    st.pyplot(fig_rx)
                    plt.close(fig_rx)
                    st.caption(
                        f"Showing received waveform distorted by simulated Gaussian channel noise at SNR = {snr_cur} dB."
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
                        "Synchronized dual-axis comparison illustrating channel distortion on the transmitted carrier."
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
                        f"Synchronized digital step plot for first {plot_bits_count} bits. "
                        "Red 'X' markers indicate individual bit discrepancies."
                    )
            else:
                st.text("[Pending Transmission: Submit a message to render interactive signal waveforms]")

    st.divider()

    # -------------------------------------------------------------------------
    # F. Educational Information Section
    # -------------------------------------------------------------------------
    st.subheader("About Digital Modulation & Performance Metrics")
    col_ask, col_fsk, col_bpsk = st.columns(3)

    with col_ask:
        st.markdown(
            "#### Amplitude Shift Keying (ASK)\n"
            "- **Modulation:** Bits modulate carrier amplitude ($A$ for bit 1, $0$ for bit 0).\n"
            "- **Demodulation:** Matched-filter correlation with threshold $A/2$.\n"
            "- **BER Performance:** Highly vulnerable to channel noise fluctuations."
        )

    with col_fsk:
        st.markdown(
            "#### Frequency Shift Keying (FSK)\n"
            "- **Modulation:** Frequency switches between $f_0$ (500 Hz) and $f_1$ (1500 Hz).\n"
            "- **Demodulation:** Dual-branch matched filters select the stronger tone.\n"
            "- **BER Performance:** Constant envelope provides better noise immunity than ASK."
        )

    with col_bpsk:
        st.markdown(
            "#### Binary Phase Shift Keying (BPSK)\n"
            "- **Modulation:** Carrier phase shifts by $180^\\circ$ ($\\pi$ rad) between bits.\n"
            "- **Demodulation:** Coherent correlation with synchronized reference carrier.\n"
            "- **BER Performance:** Theoretical optimum power efficiency and lowest BER in AWGN."
        )

    st.caption(
        "📌 *Note:* All modulation, noise addition, demodulation, and BER calculations "
        "are simulated entirely in software using Python mathematics."
    )

    st.divider()

    # -------------------------------------------------------------------------
    # G. Footer
    # -------------------------------------------------------------------------
    st.markdown(
        "<p style='text-align: center; color: #888888; font-size: 0.85rem; margin-top: 1rem;'>"
        "Academic Mini-Project | Software-Based Wireless Communication Simulation"
        "</p>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
