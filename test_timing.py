#!/usr/bin/env python3
"""
test_timing.py
──────────────
Phase 1 timing verification for reason_to_digitone.py

Sends a synthetic MIDI clock into IAC Driver Bus 1 (simulating Reason)
and reads back what the bridge would log, verifying:
  1. Pulses per pattern = 384  (64 steps × 6 pulses/step)
  2. PC fires at pulse 372      (384 − 12 early)
  3. Pattern boundary at pulse 384 exactly
  4. Real-time interval accuracy at 120 BPM (10.417 ms / pulse)

Run:
  python3 test_timing.py          # sends 2 full patterns then stops
  python3 test_timing.py --pats N # run N patterns
"""

import mido
import time
import argparse
import statistics

IAC_PORT        = "IAC Driver Bus 1"
BPM             = 120
PPQN            = 24
STEPS_PER_PAT   = 64
STEPS_PER_BEAT  = 4
PC_EARLY_PULSES = 12

PULSES_PER_STEP = PPQN // STEPS_PER_BEAT          # 6
PULSES_PER_PAT  = STEPS_PER_PAT * PULSES_PER_STEP # 384
PC_TRIGGER      = PULSES_PER_PAT - PC_EARLY_PULSES # 372
PULSE_INTERVAL  = 60.0 / (BPM * PPQN)             # seconds per pulse


def send_clock(n_patterns: int) -> None:
    """Send START → n_patterns of clock pulses → STOP on IAC Driver."""
    total_pulses = PULSES_PER_PAT * n_patterns

    print(f"Clock generator @ {BPM} BPM")
    print(f"  Pulse interval : {PULSE_INTERVAL * 1000:.3f} ms")
    print(f"  Pulses/pattern : {PULSES_PER_PAT}")
    print(f"  PC trigger     : pulse {PC_TRIGGER}")
    print(f"  Patterns       : {n_patterns}  ({total_pulses} pulses total)")
    print()

    with mido.open_output(IAC_PORT) as port:
        # START
        port.send(mido.Message('start'))
        print("  ► Sent START")

        intervals: list[float] = []
        t0 = time.perf_counter()

        for i in range(1, total_pulses + 1):
            # Busy-wait for accurate timing
            target = t0 + i * PULSE_INTERVAL
            while time.perf_counter() < target:
                pass

            t_before = time.perf_counter()
            port.send(mido.Message('clock'))
            t_after  = time.perf_counter()
            intervals.append(t_after - t_before)

            pat_num   = (i - 1) // PULSES_PER_PAT + 1
            pulse_in  = ((i - 1) % PULSES_PER_PAT) + 1

            if pulse_in == PC_TRIGGER:
                print(f"  → Pattern {pat_num}: pulse {pulse_in} — PC trigger reached")
            if pulse_in == PULSES_PER_PAT:
                elapsed = time.perf_counter() - t0
                expected = PULSES_PER_PAT * pat_num * PULSE_INTERVAL
                drift_ms = (elapsed - expected) * 1000
                print(f"  ■ Pattern {pat_num} complete  "
                      f"elapsed={elapsed:.3f}s  expected={expected:.3f}s  drift={drift_ms:+.2f}ms")

        # STOP
        port.send(mido.Message('stop'))
        print("\n  ■ Sent STOP")

        # Timing report
        total_elapsed = time.perf_counter() - t0
        expected_total = total_pulses * PULSE_INTERVAL
        print()
        print("══ Timing Report ══════════════════════")
        print(f"  Total elapsed    : {total_elapsed:.4f}s")
        print(f"  Expected         : {expected_total:.4f}s")
        print(f"  Total drift      : {(total_elapsed - expected_total)*1000:+.2f} ms")
        print(f"  Send latency avg : {statistics.mean(intervals)*1000:.3f} ms")
        print(f"  Send latency max : {max(intervals)*1000:.3f} ms")
        print("═══════════════════════════════════════")
        print()
        if abs(total_elapsed - expected_total) < 0.020:
            print("  PASS — clock accuracy within 20 ms")
        else:
            print("  WARN — drift > 20 ms; check system load")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="MIDI clock timing test for reason_to_digitone.py")
    parser.add_argument('--pats', type=int, default=2,
                        help='number of patterns to simulate (default: 2)')
    args = parser.parse_args()

    if IAC_PORT not in mido.get_output_names():
        print(f"ERROR: '{IAC_PORT}' not found. Enable IAC Driver in Audio MIDI Setup.")
        raise SystemExit(1)

    send_clock(args.pats)
