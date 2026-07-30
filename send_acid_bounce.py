#!/usr/bin/env python3
"""
Send the "Acid Bounce" patch to Digitone 2 track 7 via MIDI CC.

BEFORE RUNNING:
  1. Stop playback in Reason
  2. On the Digitone 2, select track 7
  3. Set SYN machine to FM TONE:  [FUNC] + [SYN] → FM TONE
  4. Set FLTR machine to COMB-:   [FUNC] + [FLTR] → COMB-
  5. Run this script
  6. Save the preset:  [PRESET/KIT] → PRESET → SAVE → Bank D, slot 1

Uses the Digitone 2's MIDI CC map (Appendix C of the manual).
Track 7 = MIDI channel 7 (zero-indexed: 6).
"""

import mido
import time
import sys

PORT_NAME = "Elektron Digitone II"
CHANNEL = 6  # Track 7 = MIDI channel 7 = zero-indexed 6

DELAY = 0.02  # 20ms between CCs to avoid flooding


def send_cc(port, cc, value, channel=CHANNEL):
    """Send a single CC message, clamping value to 0-127."""
    value = max(0, min(127, int(value)))
    msg = mido.Message("control_change", channel=channel, control=cc, value=value)
    port.send(msg)
    time.sleep(DELAY)


def main():
    print(f"Opening MIDI port: {PORT_NAME}")
    try:
        port = mido.open_output(PORT_NAME)
    except (IOError, OSError) as e:
        print(f"ERROR: Could not open port '{PORT_NAME}': {e}")
        print("Is the Digitone 2 connected via USB?")
        sys.exit(1)

    print(f"Sending 'Acid Bounce' patch to track 7 (MIDI ch {CHANNEL + 1})...")
    print()

    # ─── SYN PAGE 1 (FM Tone) ───────────────────────────────────
    # Knobs A-G: ALGO, RATIO A, RATIO B, HARM, DTUN, FDBK, MIX
    print("  SYN Page 1...")
    send_cc(port, 40, 18)   # ALGO = 2 (scaled: ~18/127 across 1-8)
    send_cc(port, 41, 24)   # RATIO A = 1.00 (early in ratio table)
    send_cc(port, 42, 55)   # RATIO B = ~2.00/3.00 (mid-range)
    send_cc(port, 43, 96)   # HARM = +5.00 (bipolar -26 to +26, center=64)
    send_cc(port, 44, 40)   # DTUN = 40
    send_cc(port, 45, 70)   # FDBK = 70
    send_cc(port, 46, 64)   # MIX = 0 (bipolar center = 64)

    # ─── SYN PAGE 2 (FM Tone operator envelopes) ────────────────
    # Knobs A-H: ATK(A), DEC(A), END(A), LEV(A), ATK(B), DEC(B), END(B), LEV(B)
    print("  SYN Page 2...")
    send_cc(port, 48, 0)    # ATK A = 0 (snappy)
    send_cc(port, 49, 80)   # DEC A = 80
    send_cc(port, 50, 20)   # END A = 20
    send_cc(port, 51, 90)   # LEV A = 90 (FM amount!)
    send_cc(port, 52, 0)    # ATK B = 0
    send_cc(port, 53, 50)   # DEC B = 50
    send_cc(port, 54, 10)   # END B = 10
    send_cc(port, 55, 100)  # LEV B = 100

    # ─── FLTR PAGE 1 (Comb-) ────────────────────────────────────
    # ATK(CC20), DEC(CC21), SUS(CC22), REL(CC23), FREQ(CC16),
    # FDBK(CC17=knobF), LPF(CC18=knobG), ENV.DEPTH(CC24)
    print("  FLTR Page 1 (Comb-)...")
    send_cc(port, 20, 0)    # ATK = 0
    send_cc(port, 21, 90)   # DEC = 90
    send_cc(port, 22, 0)    # SUS = 0
    send_cc(port, 23, 60)   # REL = 60
    send_cc(port, 16, 60)   # FREQ = 60
    send_cc(port, 17, 85)   # FDBK = 85 (watch volume!)
    send_cc(port, 18, 80)   # LPF = 80
    send_cc(port, 24, 96)   # ENV.DEPTH = +50 (bipolar, center=64, so 64+32=96)

    # ─── FLTR PAGE 2 (Base-Width filter) ─────────────────────────
    print("  FLTR Page 2...")
    send_cc(port, 27, 10)   # BASE = 10
    send_cc(port, 28, 100)  # WDTH = 100

    # ─── AMP PAGE ────────────────────────────────────────────────
    print("  AMP...")
    send_cc(port, 84, 0)    # ATK = 0
    send_cc(port, 85, 40)   # HOLD = 40
    send_cc(port, 86, 70)   # DEC = 70
    send_cc(port, 89, 64)   # PAN = center (bipolar, 64 = 0)
    send_cc(port, 90, 100)  # VOL = 100

    # ─── FX PAGE ─────────────────────────────────────────────────
    print("  FX...")
    send_cc(port, 78, 127)  # BR = 16 bits (max = no bit reduction)
    send_cc(port, 81, 30)   # OVER = 30 (light overdrive)
    send_cc(port, 79, 0)    # SRR = 0 (no sample rate reduction)
    send_cc(port, 30, 50)   # DEL send = 50
    send_cc(port, 31, 25)   # REV send = 25
    send_cc(port, 29, 40)   # CHR send = 40

    # ─── LFO 1 → Filter Frequency ───────────────────────────────
    # Sweeps the comb filter frequency for constant movement
    print("  LFO 1 (→ FLTR Freq)...")
    send_cc(port, 102, 80)  # SPD = 16 (bipolar, center=64 → 64+16=80)
    send_cc(port, 103, 8)   # MULT = x1 BPM (low value range)
    send_cc(port, 104, 64)  # FADE = 0 (bipolar center)
    send_cc(port, 105, 51)  # DEST = FLTR Frequency (destination index 51)
    send_cc(port, 106, 0)   # WAVE = TRI (first waveform)
    send_cc(port, 107, 0)   # SPH = 0 (start at beginning)
    send_cc(port, 108, 0)   # MODE = FREE
    send_cc(port, 109, 60)  # DEPTH = 60

    # ─── LFO 2 → Detune (wobbly detuning) ───────────────────────
    print("  LFO 2 (→ SYN Detune)...")
    send_cc(port, 111, 68)  # SPD = slow (just above center)
    send_cc(port, 112, 8)   # MULT = x1 BPM
    send_cc(port, 113, 64)  # FADE = 0
    send_cc(port, 114, 19)  # DEST = SYN knob E page 1 (DTUN, index 19)
    send_cc(port, 115, 1)   # WAVE = SINE
    send_cc(port, 116, 0)   # SPH = 0
    send_cc(port, 117, 0)   # MODE = FREE
    send_cc(port, 118, 35)  # DEPTH = 35

    # ─── LFO 3 → MIX (timbral shifting) ─────────────────────────
    # LFO 3 has no CC numbers — NRPN only (MSB=1, LSBs 58-72)
    # Sending via NRPN: CC99=MSB select, CC98=LSB select, CC6=data entry
    print("  LFO 3 (→ SYN Mix) via NRPN...")
    nrpn_params = [
        (58, 66),   # SPD = slow (just above center)
        (59, 8),    # MULT = x1 BPM
        (60, 64),   # FADE = 0
        (61, 21),   # DEST = SYN knob G page 1 (MIX, index 21)
        (62, 0),    # WAVE = TRI
        (70, 0),    # SPH = 0
        (71, 0),    # MODE = FREE
        (72, 50),   # DEPTH = 50
    ]
    for nrpn_lsb, value in nrpn_params:
        send_cc(port, 99, 1)           # NRPN MSB = 1
        send_cc(port, 98, nrpn_lsb)   # NRPN LSB
        send_cc(port, 6, value)        # Data Entry MSB
        time.sleep(DELAY)

    port.close()
    print()
    print("Done! All parameters sent to track 7.")
    print()
    print("NEXT STEPS:")
    print("  1. Play some notes on the Digitone to hear the patch")
    print("  2. Tweak any values that don't sound right")
    print("  3. Save:  [PRESET/KIT] → PRESET → SAVE → Bank D, slot 1")
    print()
    print("NOTE: Some values (ALGO, RATIO) use scaled ranges that may")
    print("need manual tweaking on the unit. The LFO destinations should")
    print("be correct but verify them on the MOD pages.")


if __name__ == "__main__":
    main()
