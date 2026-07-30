#!/usr/bin/env python3
"""
"Thor Blips" — analog blippy patch + 16-step arp pattern for Digitone 2.

Sends a Wavetone patch to track 8 that sounds like a Thor step-sequenced
analog blip: short percussive notes, resonant filter, per-step note and
filter variation via the arpeggiator + LFOs.

BEFORE RUNNING:
  1. Reason must be CLOSED (or confirm it's safe)
  2. On the Digitone 2, select track 8
  3. Set SYN machine to WAVETONE:  [FUNC] + [SYN/PRESET] → WAVETONE
  4. Set FLTR to LOWPASS 4:        [FUNC] + [FLTR/AMP] → LOWPASS4
  5. Run this script
  6. Set up the arpeggiator (instructions printed after send)
  7. Save:  [PRESET/KIT] (top row, turquoise label) → SAVE

Hold any key and the arp steps through 16 notes with filter movement.
"""

import sys
sys.path.insert(0, '/Applications/MidiDigi')
from preset_designer import send_preset, CC, LFO_DEST, LFO_WAVE, LFO_MODE

TRACK = 8

# ═══════════════════════════════════════════════════════════════════
# SOUND DESIGN — analog blippy, Thor-like
# ═══════════════════════════════════════════════════════════════════
#
# Wavetone: two oscillators with saw-ish wavetables, slight detune
# for analog thickness. Short amp envelope for blips. Lowpass4 filter
# with resonance and a snappy envelope for plucky attack. LFO1 on
# filter freq (random per trig = different freq each arp step),
# LFO2 on filter reso (same idea, different pattern).
#
# The result: hold one key, arp steps through 16 notes, each step
# gets a different random filter freq and resonance value.

preset = {
    # ── Wavetone Osc 1 ──
    # TUN1=centered, WAV1=saw-ish position, PD1=phase dist, LEV1=level
    'syn1a': 64,   # TUN1 = 0 (centered, bipolar)
    'syn1b': 20,   # WAV1 = early in wavetable (saw-like)
    'syn1c': 15,   # PD1  = light phase distortion (adds edge)
    'syn1d': 110,  # LEV1 = loud

    # ── Wavetone Osc 2 ──
    # TUN2=slightly detuned, WAV2=different position, PD2, LEV2
    'syn1e': 67,   # TUN2 = +3 (slight detune up for thickness)
    'syn1f': 35,   # WAV2 = different wavetable position (pulse-ish)
    'syn1g': 8,    # PD2  = minimal phase dist
    'syn1h': 95,   # LEV2 = slightly below osc 1

    # ── Wavetone Page 2 (wavetable offsets/modulation) ──
    'syn2a': 0,    # OFS1 = 0
    'syn2b': 0,    # TBL1 = 0
    'syn2c': 0,    # MOD  = 0 (no cross-mod)
    'syn2d': 0,    # RSET = 0

    # ── Wavetone Page 3 (noise) ──
    'syn3a': 0,    # N.ATK  = 0
    'syn3b': 0,    # N.HOLD = 0
    'syn3c': 20,   # N.DEC  = short burst
    'syn3d': 15,   # NLEV   = touch of noise for analog feel
    'syn3e': 40,   # N.BASE = mid
    'syn3f': 80,   # N.WDTH = wide

    # ── FLTR (Lowpass 4) ──
    'fltr_freq': 55,  # Cutoff = medium-low (LFO will move this)
    'fltr_f':    75,   # Reso = medium-high (squelchy)
    'fltr_env':  90,   # Env depth = strong positive (plucky attack)
    'fltr_atk':  0,    # Attack = instant
    'fltr_dec':  55,   # Decay = medium (filter closes after pluck)
    'fltr_sus':  15,   # Sustain = low (filter stays mostly closed)
    'fltr_rel':  40,   # Release = medium
    'fltr_key':  40,   # Key tracking = moderate (higher notes brighter)

    # ── AMP ──
    'amp_atk':  0,    # Attack = instant (blippy!)
    'amp_hold': 0,    # Hold = 0
    'amp_dec':  50,   # Decay = medium-short (blip tail)
    'amp_sus':  0,    # Sustain = 0 (pure blip, no sustain)
    'amp_rel':  35,   # Release = short
    'amp_pan':  64,   # Center
    'amp_vol':  100,  # Volume

    # ── FX ──
    'fx_br':   127,   # Bit reduction = off (full quality)
    'fx_over': 20,    # Overdrive = light warmth
    'fx_srr':  0,     # Sample rate reduction = off
    'fx_del':  45,    # Delay send = medium
    'fx_rev':  20,    # Reverb send = touch
    'fx_chr':  35,    # Chorus send = medium (stereo width)

    # ── LFO 1 → Filter Frequency (random per trig) ──
    # Each arp step triggers a new random filter cutoff value.
    # This is what creates "a sequence of changes to freq."
    'lfo1': {
        'dest':  'fltr_freq',  # → filter cutoff
        'wave':  'rand',       # random = new value each trig
        'mode':  'trig',       # retrigger on each note
        'spd':   64,           # speed (doesn't matter much for rand+trig)
        'mult':  0,            # multiplier
        'fade':  64,           # no fade (center = instant)
        'sph':   0,            # start phase
        'depth': 75,           # depth = wide sweep range
    },

    # ── LFO 2 → Filter Resonance (random per trig) ──
    # Each arp step also gets a different resonance value.
    'lfo2': {
        'dest':  'fltr_f',     # → filter resonance
        'wave':  'rand',       # random per trig
        'mode':  'trig',       # retrigger on each note
        'spd':   64,
        'mult':  0,
        'fade':  64,
        'sph':   0,
        'depth': 55,           # moderate depth (don't go full screech)
    },

    # ── LFO 3 → Osc 1 wavetable position (subtle timbral shift) ──
    # Slowly drifts the wavetable position so the tone evolves.
    'lfo3': {
        'dest':  'syn1b',      # → WAV1 (osc 1 waveform position)
        'wave':  'tri',        # smooth triangle
        'mode':  'free',       # free-running
        'spd':   70,           # slow drift
        'mult':  0,
        'fade':  64,
        'sph':   0,
        'depth': 30,           # subtle
    },
}


# ═══════════════════════════════════════════════════════════════════
# ARP PATTERN — 16-step note offsets (semitones from held key)
# ═══════════════════════════════════════════════════════════════════
# If you hold F3, this pattern plays:
#   F3  F3  Ab3 F3  C3  F3  Eb3 C3  F3  Ab3 Bb3 Ab3 F3  C3  Eb3 F3
#
# Classic minimal techno blip sequence — stays in F minor,
# bounces between root, fifth, minor third.

ARP_OFFSETS = [
    0,    # step 1:  root (F)
    0,    # step 2:  root
    +3,   # step 3:  minor 3rd (Ab)
    0,    # step 4:  root
    -5,   # step 5:  fifth below (C)
    0,    # step 6:  root
    -2,   # step 7:  minor 7th below (Eb)
    -5,   # step 8:  fifth below (C)
    0,    # step 9:  root
    +3,   # step 10: minor 3rd (Ab)
    +5,   # step 11: fourth (Bb)
    +3,   # step 12: minor 3rd (Ab)
    0,    # step 13: root
    -5,   # step 14: fifth below (C)
    -2,   # step 15: minor 7th below (Eb)
    0,    # step 16: root (resolves)
]


def main():
    print("=" * 55)
    print("  THOR BLIPS — analog blip patch for Digitone 2")
    print("=" * 55)
    print()
    print(f"  Target: Track {TRACK} (MIDI ch {TRACK})")
    print(f"  Machine: WAVETONE  |  Filter: LOWPASS 4")
    print()

    # Send the preset
    ok = send_preset(preset, track=TRACK, machine='wavetone', fltr='lowpass4')
    if not ok:
        sys.exit(1)

    # Print arp setup instructions
    print()
    print("=" * 55)
    print("  NOW SET UP THE ARPEGGIATOR ON THE DIGITONE 2")
    print("=" * 55)
    print()
    print("  Press [ARPEGGIATOR] (button 13, turquoise ARP label)")
    print()
    print("  1. MODE  → TRUE  (knob A)")
    print("  2. SPEED → 1/16  (knob B)")
    print("  3. RANGE → 1     (knob C — one octave only)")
    print("  4. N.LEN → 3/128 or short  (knob D — short blips)")
    print("  5. LEN   → 16    (knob F — all 16 steps)")
    print()
    print("  6. Set the 16 step offsets:")
    print("     Use [LEFT]/[RIGHT] to select step,")
    print("     knob E to set the offset (semitones).")
    print()
    print("     Step  Note (if C3)  Offset")
    print("     ─────────────────────────────")
    for i, ofs in enumerate(ARP_OFFSETS):
        note_names = {0: 'C', 1: 'C#', 2: 'D', 3: 'Eb', -1: 'B', -2: 'Bb',
                      -3: 'A', -4: 'Ab', -5: 'G', 5: 'F', 4: 'E', 7: 'G',
                      8: 'Ab', 10: 'Bb', 12: 'C'}
        base = 'C3' if ofs == 0 else f'{note_names.get(ofs % 12, "?")}{"3" if ofs >= 0 else "2"}'
        sign = f'+{ofs}' if ofs > 0 else str(ofs)
        print(f"      {i+1:2d}    {base:4s}         {sign:>3s}")
    print()
    print("  7. Press [FUNC] + [ARPEGGIATOR] to turn arp ON")
    print()
    print("  PLAY IT: hold any key on the Digi's keyboard.")
    print("  Each 1/16 step plays a different note + filter value.")
    print()
    print("  SAVE: [PRESET/KIT] (top row, turquoise label)")
    print("        → SAVE → pick a slot")
    print()
    print("  TWEAK IDEAS:")
    print("  • LFO1 depth (filter freq range): [MOD] → knob H")
    print("  • LFO2 depth (reso range): [MOD] → page 2 → knob H")
    print("  • Filter cutoff base: [FLTR/AMP] → knob E")
    print("  • More acid: raise fltr_f (reso) and fltr_env (env depth)")
    print("  • Longer blips: raise amp_dec on [FLTR/AMP] page 2")


if __name__ == "__main__":
    main()
