#!/usr/bin/env python3
"""
reason_to_digitone.py
─────────────────────
Reason DAW → Elektron Digitone 2 MIDI Bridge

Listens to Reason's IAC Driver output (MIDI notes + MIDI clock on one port),
forwards all note/CC data transparently to the Digitone 2, and fires Program
Change messages at pattern boundaries so the Digitone 2 advances through
patterns automatically — one pattern per loop of the Reason song.

SETUP CHECKLIST
───────────────
Reason:
  1. Preferences → Sync tab → MIDI Clock Output: IAC Driver Bus 1
  2. Tick "Send MIDI clock while sequencer is stopped"
  3. Transport panel → enable "Send MIDI Clock"
  4. Each MIDI Out Device → set channel to match Digitone track (see CHANNEL_MAP)

Digitone 2:
  1. Each track → SYN page → CHAN = matching channel number
  2. SETTINGS → MIDI CONFIG → SYNC → Clock Receive: OFF
  3. SETTINGS → MIDI CONFIG → SYNC → Transport Receive: OFF
  4. SETTINGS → MIDI CONFIG → SYNC → PRG CH RECEIVE: ON
  5. Connect via USB

Run:
  python3 reason_to_digitone.py          # normal recording
  python3 reason_to_digitone.py --ports  # list available MIDI ports and exit
  python3 reason_to_digitone.py --dry    # dry run (no Digitone connection, timing test only)
"""

import mido
import sys
import time
import argparse
from dataclasses import dataclass, field
from typing import Optional


# ══════════════════════════════════════════════════════════════════════════════
# CONFIG — edit these before running
# ══════════════════════════════════════════════════════════════════════════════

# Find exact names by running: python3 reason_to_digitone.py --ports
IAC_INPUT_PORT  = "IAC Driver Bus 1"   # Reason MIDI output + clock
DIGITONE_OUTPUT = "Digitone 2"         # Digitone 2 USB MIDI port name

# Song / session settings
BPM             = 120      # Must match Reason's tempo
STEPS_PER_PAT   = 64       # Steps per pattern (32, 64, or 128)
PPQN            = 24       # MIDI clock standard: 24 pulses per quarter note
STEPS_PER_BEAT  = 4        # 16th note resolution (don't change unless using triplets)

# Pattern range for this session
START_PATTERN   = 0        # 0=A01, 1=A02, 15=A16, 16=B01 ... 127=H16
MAX_PATTERNS    = 128      # Total Digitone patterns available

# Timing tweak: send Program Change this many pulses before the pattern ends
# so Digitone has time to queue the next pattern and switch on the downbeat.
# 12 pulses = half a 16th note at any BPM. Increase if Digitone switches late.
PC_EARLY_PULSES = 12

# Channel map: for logging/verification only (script passes all channels through)
# Key = MIDI channel (1-indexed), Value = description
CHANNEL_MAP = {
    1: "TB-303 (TD-3)",
    2: "Tetr4",
    3: "Minilogue",
    10: "TR-8S",
}


# ══════════════════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def pattern_name(index: int) -> str:
    """Convert 0-based pattern index to Elektron bank/pattern name (e.g. 0 → A01)."""
    bank = chr(65 + (index // 16))
    num  = (index % 16) + 1
    return f"{bank}{num:02d}"


def pulses_per_pattern(steps: int = STEPS_PER_PAT) -> int:
    """Number of MIDI clock pulses in one full pattern."""
    pulses_per_step = PPQN // STEPS_PER_BEAT   # 6 pulses per 16th note
    return steps * pulses_per_step


def list_ports() -> None:
    """Print all available MIDI input and output port names."""
    print("\n── Available MIDI INPUT ports ──")
    inputs = mido.get_input_names()
    if inputs:
        for name in inputs:
            marker = " ◄ (configured)" if name == IAC_INPUT_PORT else ""
            print(f"  {name}{marker}")
    else:
        print("  (none found)")

    print("\n── Available MIDI OUTPUT ports ──")
    outputs = mido.get_output_names()
    if outputs:
        for name in outputs:
            marker = " ◄ (configured)" if name == DIGITONE_OUTPUT else ""
            print(f"  {name}{marker}")
    else:
        print("  (none found)")
    print()


def validate_ports(dry_run: bool = False) -> bool:
    """Check that configured ports exist. Returns True if OK."""
    ok = True
    if IAC_INPUT_PORT not in mido.get_input_names():
        print(f"✗ Input port not found:  '{IAC_INPUT_PORT}'")
        ok = False
    else:
        print(f"✓ Input port found:      '{IAC_INPUT_PORT}'")

    if not dry_run:
        if DIGITONE_OUTPUT not in mido.get_output_names():
            print(f"✗ Output port not found: '{DIGITONE_OUTPUT}'")
            ok = False
        else:
            print(f"✓ Output port found:     '{DIGITONE_OUTPUT}'")

    if not ok:
        print()
        list_ports()
    return ok


# ══════════════════════════════════════════════════════════════════════════════
# BRIDGE
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class BridgeState:
    pulse_count:    int  = 0
    pattern_index:  int  = START_PATTERN
    running:        bool = False
    pc_sent:        bool = False
    channels_seen:  set  = field(default_factory=set)
    notes_forwarded: int = 0
    session_start:  Optional[float] = None


def print_preflight(pat_pulses: int) -> None:
    end_pat = min(START_PATTERN + MAX_PATTERNS, MAX_PATTERNS) - 1
    duration_s = (pat_pulses / PPQN) * (60 / BPM) * (MAX_PATTERNS - START_PATTERN)
    duration_m = duration_s / 60

    print("══════════════════════════════════════════")
    print("  Reason → Digitone 2 Bridge")
    print("══════════════════════════════════════════")
    print(f"  IAC input  : {IAC_INPUT_PORT}")
    print(f"  Digitone   : {DIGITONE_OUTPUT}")
    print(f"  BPM        : {BPM}")
    print(f"  Steps/pat  : {STEPS_PER_PAT}")
    print(f"  Pulses/pat : {pat_pulses}")
    print(f"  PC fires   : {pat_pulses - PC_EARLY_PULSES} pulses in ({PC_EARLY_PULSES} early)")
    print(f"  Patterns   : {pattern_name(START_PATTERN)} → {pattern_name(end_pat)}")
    print(f"  Max time   : ~{duration_m:.1f} min")
    print("──────────────────────────────────────────")
    print("  Waiting for MIDI clock from Reason...")
    print("  (press Play in Reason to start)\n")


def run_bridge(dry_run: bool = False) -> None:
    pat_pulses  = pulses_per_pattern()
    pc_trigger  = pat_pulses - PC_EARLY_PULSES
    state       = BridgeState(pattern_index=START_PATTERN)

    print_preflight(pat_pulses)

    # In dry-run mode we open the input but send to a null output
    def open_output():
        if dry_run:
            return mido.open_output("MidiDigi-DryRun", virtual=True)
        return mido.open_output(DIGITONE_OUTPUT)

    with mido.open_input(IAC_INPUT_PORT) as inport, open_output() as outport:
        for msg in inport:

            # ── CLOCK ────────────────────────────────────────────────────────
            if msg.type == 'clock':
                if not state.running:
                    continue

                state.pulse_count += 1

                # Fire PC early — once per pattern boundary
                if state.pulse_count >= pc_trigger and not state.pc_sent:
                    next_index = state.pattern_index + 1
                    if next_index < MAX_PATTERNS:
                        pc_msg = mido.Message('program_change',
                                              program=next_index,
                                              channel=0)
                        if not dry_run:
                            outport.send(pc_msg)
                        state.pc_sent = True
                        print(f"  ▶ PC {next_index:3d} → {pattern_name(next_index)}"
                              f"  (pulse {state.pulse_count}/{pat_pulses})"
                              f"{'  [DRY RUN]' if dry_run else ''}")

                # Pattern boundary
                if state.pulse_count >= pat_pulses:
                    state.pulse_count   = 0
                    state.pattern_index += 1
                    state.pc_sent       = False

                    if state.pattern_index >= MAX_PATTERNS:
                        print("\n  All patterns filled. Stopping.")
                        break

                    elapsed = time.time() - state.session_start if state.session_start else 0
                    print(f"  ■ Now recording: {pattern_name(state.pattern_index)}"
                          f"  ({elapsed:.0f}s elapsed,"
                          f" channels: {sorted(state.channels_seen)})")

            # ── TRANSPORT ────────────────────────────────────────────────────
            elif msg.type == 'start':
                state.running       = True
                state.pulse_count   = 0
                state.pc_sent       = False
                state.session_start = time.time()
                print(f"  ► START  — recording into {pattern_name(state.pattern_index)}")

            elif msg.type == 'stop':
                state.running = False
                elapsed = time.time() - state.session_start if state.session_start else 0

                # All-notes-off on every active channel — prevents stuck notes on
                # the Digitone if Reason stops while notes are held.
                if not dry_run:
                    for ch in range(16):
                        try:
                            outport.send(mido.Message('control_change',
                                                      channel=ch, control=123, value=0))
                        except OSError:
                            pass  # already disconnected, best-effort only

                print(f"  ■ STOP   — last pattern: {pattern_name(state.pattern_index)}")
                print(f"    Notes forwarded : {state.notes_forwarded}")
                print(f"    Channels seen   : {sorted(state.channels_seen)}")
                print(f"    Session time    : {elapsed:.1f}s")

                # Check if any expected channels were missing
                expected = set(CHANNEL_MAP.keys())
                missing  = expected - state.channels_seen
                if missing:
                    missing_names = [f"ch{c} ({CHANNEL_MAP[c]})" for c in sorted(missing)]
                    print(f"  ⚠ No data seen on: {', '.join(missing_names)}")
                print()

            elif msg.type == 'continue':
                # Reason sends 'continue' when resuming after a reposition (loop mode).
                # We can't know the new song position, so reset the pulse counter to
                # re-align to the nearest pattern boundary and warn the user.
                state.running     = True
                state.pulse_count = 0
                state.pc_sent     = False
                if state.session_start is None:
                    state.session_start = time.time()
                print(f"  ► CONTINUE — pulse counter reset; recording into"
                      f" {pattern_name(state.pattern_index)}")
                print(f"  ⚠ Loop detected — pattern boundary may not align with Reason."
                      f" Disable loop mode in Reason for accurate recording.")

            # ── NOTE / CC DATA (pass through) ────────────────────────────────
            elif msg.type in ('note_on', 'note_off',
                              'control_change', 'pitchwheel',
                              'aftertouch', 'polytouch'):
                if not dry_run:
                    try:
                        outport.send(msg)
                    except OSError as e:
                        print(f"  ✗ Send error (Digitone disconnected?): {e}")
                        print(f"    Reconnect Digitone and restart the script.")
                        break

                if hasattr(msg, 'channel'):
                    ch = msg.channel + 1   # mido is 0-indexed, humans are 1-indexed
                    state.channels_seen.add(ch)

                if msg.type in ('note_on', 'note_off'):
                    state.notes_forwarded += 1

            # ── SYSEX / OTHER (pass through silently) ────────────────────────
            elif msg.type == 'sysex':
                if not dry_run:
                    try:
                        outport.send(msg)
                    except OSError:
                        pass  # sysex failure is non-critical


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    global START_PATTERN, STEPS_PER_PAT, PC_EARLY_PULSES

    parser = argparse.ArgumentParser(
        description="Reason → Digitone 2 MIDI Bridge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
examples:
  python3 reason_to_digitone.py            # normal recording session
  python3 reason_to_digitone.py --ports    # list MIDI ports and exit
  python3 reason_to_digitone.py --dry      # dry run, no Digitone needed
  python3 reason_to_digitone.py --start 16 # start from pattern B01
  python3 reason_to_digitone.py --steps 32 # use 32-step patterns
        """
    )
    parser.add_argument('--ports',  action='store_true', help='list MIDI ports and exit')
    parser.add_argument('--dry',    action='store_true', help='dry run (no Digitone required)')
    parser.add_argument('--start',  type=int, default=None, help='override start pattern index (0-127)')
    parser.add_argument('--steps',  type=int, default=None, help='override steps per pattern (32/64/128)')
    parser.add_argument('--early',  type=int, default=None,
                        help=f'pulses before pattern end to send PC (default: {PC_EARLY_PULSES})')
    args = parser.parse_args()

    if args.ports:
        list_ports()
        return

    # Apply CLI overrides
    if args.start is not None:
        if not 0 <= args.start <= 127:
            print("ERROR: --start must be 0–127")
            sys.exit(1)
        START_PATTERN = args.start
    if args.steps is not None:
        if args.steps not in (32, 64, 128):
            print("ERROR: --steps must be 32, 64, or 128")
            sys.exit(1)
        STEPS_PER_PAT = args.steps
    if args.early is not None:
        if not 0 <= args.early <= pulses_per_pattern() // 2:
            print(f"ERROR: --early must be 0–{pulses_per_pattern() // 2}")
            sys.exit(1)
        PC_EARLY_PULSES = args.early

    # Port validation
    if not validate_ports(dry_run=args.dry):
        sys.exit(1)
    print()

    try:
        run_bridge(dry_run=args.dry)
    except KeyboardInterrupt:
        print("\n  Interrupted. Bye.")


if __name__ == '__main__':
    main()
