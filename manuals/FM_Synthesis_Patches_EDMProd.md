# FM Synthesis — Practical Patch Guide

Source: EDMProd, "FM Synthesis: The Beginner's Guide"
https://www.edmprod.com/fm-synthesis/

---

## FM Synthesis vs. Other Synthesis Types

| Type | Method | Character |
|------|--------|-----------|
| **FM** | Audio-rate frequency modulation between operators | Complex, metallic, evolving, aggressive |
| **Subtractive** | Filter harmonically-rich waveforms | Warm, smooth, classic analog |
| **Wavetable** | Morph between waveform frames | Digital, evolving, modern |
| **Granular** | Slice audio into grains, rearrange | Glitchy, textured, atmospheric |

## Core Terminology

- **Operator**: An oscillator used for generating or modulating sound
- **Carrier**: The operator generating actual sound output (you hear this)
- **Modulator**: The operator modulating other parameters (you don't hear this directly)
- **Algorithm**: The specific arrangement and routing of carriers and modulators
- **Harmonic Ratio**: The frequency relationship between operators. Integer ratios
  (2:1, 3:1) produce harmonic/musical tones. Non-integer ratios produce inharmonic/
  metallic tones.

## Historical Context

Yamaha developed FM digital synthesizer prototypes starting in 1974. The GS-1
was released commercially in 1980. The DX7 followed as the first fully digital
synthesizer and became one of the best-selling synths of all time.

The TX81Z (1986) expanded FM by allowing 8 different waveforms per operator
(not just sine waves), which enabled sounds like the famous "Lately Bass" that
defined 90s house, techno, and hip-hop.

## Basic FM Patch Setup

The fundamental FM patch:
1. Carrier oscillator (sine wave) → audio output
2. Modulator oscillator (sine wave) → modulates carrier's frequency
3. Modulator level at 0 = pure sine; increase for more harmonics
4. Apply envelope to FM amount for dynamic timbre

**Key principle**: "Small modulation amounts often suffice" — FM synthesis produces
aggressive characteristics quickly.

## Phase Modulation vs. FM

Phase Modulation (PM) and Frequency Modulation (FM) are scientifically different
but achieve identical practical results. The Digitone 2 and most modern "FM" synths
actually use PM internally. For patch design purposes, the distinction doesn't matter.

## Patch Recipe: Bass Growl

**Goal**: Aggressive, evolving bass with movement

- **OSC 1** (Carrier): Primary oscillator, various waveforms
- **OSC 2** (Modulator): Sine wave, level at 0 (audio), FM routed to OSC 1
- **OSC 3**: Sub bass layer (square wave, low octave)
- **Filter 1**: High-pass with LFO modulation for movement
- **LFO 1**: Modulates filter cutoff, resonance, and OSC levels

Post-processing: chorus, compression, distortion for aggression.

**FM design principles for bass**:
- Keep carrier at base pitch (ratio 1:1)
- Modulator at 1:1 or 2:1 for harmonic bass
- Use envelope on FM amount: fast attack, medium decay = plucky/punchy
- LFO on FM amount at low rate = wobble/growl

## Patch Recipe: Frozen Pad

**Goal**: Evolving ambient texture with depth

- **OSC 1** (Carrier): Sine wave
- **OSC 2** (Modulator 1): Complex waveform, dropped 12 semitones (0.5:1 ratio)
- **OSC 3** (Modulator 2): Sine wave, modulating OSC 2 (cascaded modulation)
- **Routing**: OSC 3 → modulates OSC 2 → modulates OSC 1
- **LFO**: Very slow rate, assigned to multiple parameters for organic drift
- **Filter 1**: Low-pass (tame highs)
- **Filter 2**: High-pass (remove mud)
- **Noise**: Pink noise layer for texture
- **Effects**: Heavy reverb and delay for spatial character

**FM design principles for pads**:
- Cascaded modulation (mod → mod → carrier) creates extremely complex evolving spectra
- Slow LFOs on FM amount = organic timbral drift
- Low modulator ratios (0.5:1) keep things warm and deep
- Multiple modulators at different ratios = rich harmonic content

## Patch Recipe: Jump Up Lead

**Goal**: Aggressive, rhythmic lead sound

- **OSC 1** (Carrier): Sine wave, dropped 3 octaves
- **OSC 2** (Modulator): Variable waveform
- **LFO 1**: Modulates OSC 1 level AND FM amount (creates rhythmic pumping)
- **Filter 1**: High-pass with LFO on cutoff
- **Noise**: White noise through separate filter
- Post-processing: multiband compression, distortion with LFO

**Key insight**: "Wavetable selection for OSC 2 significantly impacts final character."
Changing the modulator waveform from sine to other shapes dramatically alters the
harmonic spectrum — this is how the TX81Z's 8 waveforms unlocked sounds the
sine-only DX7 couldn't achieve.

## FM Across Different Synth Architectures

### 4-Operator FM (Digitone 2, TX81Z)
- 4 operators, typically 8 algorithms
- More immediate, hands-on — fewer operators means each one matters more
- Non-sine waveforms available (Digitone 2 has many waveform choices)
- Sweet spot for electronic music: complex enough for rich timbres, simple enough
  to program intuitively

### 6-Operator FM (DX7, DX21)
- 6 operators, 32 algorithms
- More complex routing possibilities
- Sine-wave only (DX7) — requires more operators to achieve complex timbres
- Classic "DX" sound: electric piano, bells, brass

## General Design Principles

1. **Envelope shaping creates dynamic character** — static FM sounds flat;
   enveloped FM sounds alive
2. **LFO assignments to multiple parameters** (filter cutoff, FM amount, noise
   levels) generate evolving textures
3. **FM produces aggressive characteristics** — start with low modulation and
   increase gradually
4. **Experimenting with modulator waveform** drastically changes the final tone
5. **Non-integer ratios** → metallic, bell-like, percussive
6. **Integer ratios** → musical, harmonic, tonal
