# FM Synthesis Basics — Programming Guide

Source: Ether Diver, "How to Synth: FM Basics I"
https://www.etherdiver.com/how-to-synth-a-guide-to-programming-synthesizers/fm-basics-i/

---

## Overview

FM (Frequency Modulation) synthesis creates sounds via audio-rate modulation of
frequency. Unlike subtractive synthesis (which filters harmonically rich waveforms),
FM uses audio-rate modulation to generate new frequencies called sidebands, enabling
complex timbres from simple waveforms.

## Core Components

### The Operator

An operator combines three elements:
- **Oscillator** — generates a waveform (sine wave in classic FM)
- **Amplifier** — controls level
- **Envelope** — shapes amplitude over time

In a 6-operator synth (DX7), each operator has a dedicated envelope. In a 4-operator
synth (Digitone 2, TX81Z), the same principle applies with fewer operators.

Operators are configured as pairs: one **modulator** and one **carrier**.
Only the carrier connects to audio output.

### Carrier vs. Modulator

- **Carrier**: The operator you hear. Determines the fundamental pitch of the sound.
  Connected to the audio output.
- **Modulator**: Shapes the carrier's timbre by modulating its frequency at audio rate.
  NOT connected to audio output — you never hear the modulator directly.
  The modulator's envelope controls how FM complexity develops over time.

## Frequency Ratios

Operators are tuned using **ratios** relative to the base pitch. The ratio between
carrier and modulator determines the harmonic content of the sound.

### Harmonic (Integer) Ratios

| Ratio | Interval | Character |
|-------|----------|-----------|
| 1:1   | Unison   | Sine → sawtooth spectral evolution as mod depth increases |
| 2:1   | Octave   | Triangle and square waveshapes |
| 3:1   | Octave + fifth | Hollow, clarinet-like |
| 4:1   | Two octaves | Bright, organ-like |
| 5:1   | Two octaves + major third | Bell-like onset |
| 7:1   | — | Glassy FM tones |
| 10:1  | — | Very glassy, metallic |
| 13:1  | — | Extremely glassy, almost noise |

**Rule of thumb**: Higher integer ratios = more harmonics = brighter/glassier sounds.

### Inharmonic (Non-Integer) Ratios

| Ratio | Character |
|-------|-----------|
| 1.7:1 | Slightly metallic, bell-like |
| 2.3:1 | More metallic, clangy |
| 3.14:1 | Chaotic, noisy |

Non-integer ratios produce **inharmonic** spectra — metallic, bell-like, or noisy
timbres. Essential for percussion, metallic textures, and experimental sounds.

### Sub-Ratios

| Ratio | Effect |
|-------|--------|
| 0.5:1 | One octave below — creates subharmonics |
| 0.25:1 | Two octaves below |

Fractional ratios below 1:1 generate subharmonics useful for bass sounds.

### Fixed Frequencies

Setting an operator to a fixed frequency (in Hz) rather than a ratio means it
doesn't track the keyboard. Useful for:
- Sound effects
- Percussion (where the modulator should stay at a fixed frequency)
- Noise-like textures

## Modulation Depth (Modulator Level)

The modulator's level determines FM intensity — how much the carrier's frequency
is being modulated.

**Analogy with subtractive synthesis**: Higher modulator level = more open filter,
because more overtones are present.

| Modulator Level | Result |
|-----------------|--------|
| 0%              | Pure sine wave (no modulation) |
| ~20-30%         | Subtle warmth, slight harmonic content |
| ~40-60%         | Rich, musical complexity |
| ~70-80%         | Aggressive, buzzy, lots of harmonics |
| ~90-100%        | Harsh, approaching noise |

**Key principle**: Small changes in modulator level have dramatic timbral effects.
This is the most sensitive parameter in FM synthesis.

## Feedback

Self-modulation through feedback adds edge and definition. An operator modulates
its own frequency, creating additional harmonics.

| Feedback Amount | Result |
|-----------------|--------|
| 0%              | Pure sine wave |
| ~30-40%         | Slight edge, warmth |
| ~50-60%         | Sawtooth-like character |
| ~70-75%         | Clean sawtooth wave |
| ~80-90%         | Harsh, distorted |
| 100%            | Chaos / noise |

**Critical insight**: "Feedback is required to achieve certain fundamental waveshapes,
including saw and square waves." A self-modulating operator at ~70-75% feedback
produces a sawtooth wave.

Combined with ratios:
- Feedback + 1:1 ratio + moderate mod → sawtooth-like
- Feedback + 2:1 ratio + moderate mod → square-like

## Envelope Shaping Strategy

This is where FM becomes expressive. The key insight:

**To create FM sweeps (equivalent to filter sweeps in subtractive):**
1. Carrier envelope: opens quickly (fast attack)
2. Modulator envelope: rises slowly to a moderate level, then fades
3. Result: sound evolves from simple → complex → simple (like a filter opening and closing)

**For percussive/plucky sounds:**
1. Carrier envelope: sharp attack, quick decay
2. Modulator envelope: even sharper attack, very quick decay
3. Result: bright transient that quickly becomes simple

**For evolving pads:**
1. Carrier envelope: slow attack, long sustain
2. Modulator envelope: very slow attack, gradual rise
3. Result: timbre slowly becomes more complex over time

## Practical Patch Foundations (2-Operator)

### FM Bass
- Carrier: ratio 1:1
- Modulator: ratio 0.5:1 (subharmonic) or 1:1
- Modulator level: ~40-50%
- Modulator envelope: fast attack, medium decay, low sustain
- Add feedback on carrier for saw-like edge

### FM Lead
- Carrier: ratio 1:1
- Modulator: ratio 2:1 or 3:1
- Modulator level: ~50-70%
- Feedback: ~20-40% for edge
- Modulator envelope: follows carrier closely

### FM Sweep
- Carrier: ratio 1:1
- Modulator: ratio 1:1 or 2:1
- Modulator level: ~60-80%
- Modulator envelope: slow attack (creates timbral sweep)
- This is the FM equivalent of a filter sweep

### FM Percussion
- Carrier: ratio 1:1, very short envelope
- Modulator: non-integer ratio (e.g., 1.7:1, 3.14:1)
- Modulator level: high (~80%)
- Both envelopes: very fast decay
- Use fixed frequencies for non-pitched percussion

### FM Bell
- Carrier: ratio 1:1
- Modulator: non-integer ratio (e.g., 1.4:1, 3.5:1)
- Modulator level: ~50-60%
- Long decay on both envelopes
- No feedback (keep it clean and resonant)

## Translating Sound Ideas to FM Parameters

| "I want it to sound..." | Adjust... |
|--------------------------|-----------|
| Brighter / more harmonics | Increase modulator level |
| Darker / fewer harmonics | Decrease modulator level |
| More metallic / bell-like | Use non-integer ratio |
| More musical / tonal | Use integer ratio |
| Warmer / saw-like edge | Add feedback |
| More sub bass | Use ratio below 1:1 (e.g., 0.5) |
| Glassy / crystalline | High integer ratio (7:1, 10:1+) |
| Filter sweep effect | Modulate modulator level with envelope or LFO |
| Plucky / percussive | Fast modulator envelope decay |
| Evolving / pad-like | Slow modulator envelope |
| Noisy / chaotic | Very high modulator level + non-integer ratio |

## Key Takeaway

"By carefully controlling how much modulation each wave gets with envelopes, LFOs
and hands-on controls, it becomes possible to create incredibly nuanced and complex
sounds via FM."

The most important parameters to experiment with:
1. **Ratio** — determines harmonic content type
2. **Modulator level** — determines harmonic content amount
3. **Modulator envelope** — determines how harmonics evolve over time
4. **Feedback** — adds edge and fundamental waveshape character
