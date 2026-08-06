# Digitone 2 — Making Analog-Sounding Patches

Source: compiled from Elektronauts forums, Sound on Sound review, Digitone FM
Synthesis Google Doc guide, Elektron knowledge base, and various YouTube tutorial
summaries (Cuckoo, loopop, etc.)

---

## Why FM Patches Sound "Digital" (and How to Fix It)

FM's default is thin, glassy sine waves. Classic analog synths sound warm because
of sawtooth/square waves, filter sweeps, slight detuning, and saturation. The
Digitone 2 was *designed* to bridge this gap — its signal path is closer to a
subtractive synth than a classic DX7. Use that architecture.

**The three pillars of analog-sounding FM:**
1. **Feedback** — turns sines into saws/squares (the raw waveform)
2. **Filter** — shape harmonics subtractively, just like an analog synth
3. **Detune + chorus** — add warmth and width that FM lacks naturally

---

## Waveform Recipes via Ratios + Feedback

### Sawtooth Wave (the analog bread-and-butter)
- Ratio A = 1:1 (modulator and carrier at same frequency)
- **A Level (mod depth) ≈ 50** — adds all harmonics progressively
- OR: use **feedback ≈ 35** on an operator — self-modulation creates saw shape
- Higher feedback = brighter saw; above ~60 starts becoming noise

### Square Wave
- Ratio A = **2:1** (modulator at double carrier frequency)
- A Level ≈ 30-40 — produces odd harmonics only (hollow, clarinet-like)
- Alternatively: ratio 1:2 (carrier:modulator) gives square character

### Triangle Wave (soft, mellow)
- Low feedback (10-15) on a 1:1 ratio
- Keep modulation depth very low
- Or use ratio 2:1 with A Level ≈ 15-20

### Pulse Wave (PWM-like)
- Ratio 3:1 or higher with moderate modulation depth
- LFO on modulation depth = pseudo-PWM movement

---

## Algorithm Choice for Analog Sounds

**Algorithm 1** (A→C, B1→B2, both to output): Two independent carrier+modulator
pairs. Good for layered sounds (e.g., sub bass + harmonic content).

**Algorithm 2** (A→C, B1→B2 in series): Cascade creates more complex harmonics.
Good for pads with evolving harmonic content.

**Algorithm 4** (all four ops in parallel): Each op is a carrier — closest to
additive synthesis. Use with feedback on each op for organ-like or warm layered
tones.

**Algorithm 5** (A→C, B1+B2→C): Two modulators into one carrier. Rich harmonic
content, good for thick basses.

**Algorithm 7** (feedback loop): Self-modulating feedback path. Can produce very
analog-like raw tones but harder to control.

**General rule**: For analog-like sounds, simpler algorithms (1, 2) with fewer
modulation stages work best. Complex algorithms create harmonics that don't exist
in analog synths.

---

## The Filter Is Your Best Friend

This is the **single biggest thing** that makes Digitone sound analog. Classic FM
synths (DX7) had no filter — the Digitone's filter is specifically there to tame
FM harmonics into subtractive-style sounds.

### Lowpass 4-pole (LP4) — the analog emulator
- Set filter freq **low** (30-60) and use **filter envelope** to sweep up
- This is exactly how a Moog/Juno/303 works — start dark, sweep bright
- Resonance 40-80 for character (higher = more squelchy/acid)
- Filter envelope: fast attack, medium-long decay, moderate sustain

### Lowpass 2-pole (LP2) — gentler roll-off
- More like a Korg or SEM filter — less aggressive, more open
- Good for pads where you want warmth without thickness

### Legacy filter
- The original Digitone filter — still useful but less analog-feeling
- Better for sound effects and experimental textures

### Filter Envelope Tips
- **Punchy bass**: fast attack (0-5), short decay (40-60), low sustain (20-30)
- **Acid bass**: fast attack, medium decay (60-90), zero sustain, high resonance
- **Warm pad**: slow attack (60-100), long decay (110-127), high sustain (90-110)
- **Pluck**: zero attack, very short decay (20-40), zero sustain

---

## Feedback: The Secret Weapon

Feedback = an operator modulating itself. This is the easiest way to get
non-sine waveforms without needing a modulator.

| Feedback Value | Character |
|----------------|-----------|
| 0              | Pure sine wave |
| 10-20          | Slightly warm, triangle-like |
| 25-35          | **Sawtooth territory** — this is the sweet spot for analog |
| 40-50          | Bright, aggressive saw |
| 55-70          | Harsh, distorted |
| 70+            | Approaching noise |

**Tip**: Feedback ~30 + LP4 filter sweep = instant Juno/Moog-style patch.

---

## Detune and Chorus for Warmth

FM sounds are mathematically perfect — analog synths are warm partly because
oscillators drift slightly. Recreate this:

- **DTUN parameter**: Small values (2-8) add subtle beating between operators,
  mimicking analog oscillator drift
- **Chorus effect (fx_chr)**: Even small amounts (15-30) add the stereo width
  and slight pitch wobble that screams "analog"
- **LFO on pitch**: Very slow (speed 3-8), very shallow (depth 2-5) sine LFO
  on pitch = oscillator drift. This is what makes vintage synths sound alive.

### Digitone 2 Unison (new feature)
- Unison stacks multiple voices per note with detune/spread
- Even 2 voices with slight detune transforms a thin FM tone into something
  much fatter and more analog-feeling
- More voices + more detune = supersaw territory

---

## Specific Analog-Style Patch Frameworks

### Deep Techno Sub Bass
- Algorithm 1 or 2
- Ratio A: 1:1, A Level: 40-50 (saw-ish harmonics)
- Feedback: 25-30
- Filter: LP4, freq 40, reso 30, env depth 45
- Filter env: atk 0, dec 50, sus 25, rel 20
- Amp env: atk 0, dec 127, sus 127, rel 15
- Detune: 3-5 for subtle thickness
- No chorus, no reverb (keep it dry and tight)

### Warm Juno-Style Pad
- Algorithm 1 or 4
- Ratio A: 1:1, A Level: 30 (gentle saw harmonics)
- Feedback: 20-28
- Filter: LP4, freq 55, reso 50, env depth 40
- Filter env: atk 80, dec 110, sus 80, rel 60
- Amp env: atk 80-100, dec 127, sus 120, rel 50
- Chorus: 30-50 (essential for Juno character)
- Detune: 5-10
- LFO: slow triangle on filter freq, depth 15-25

### 303 Acid Line
- Algorithm 1
- Ratio A: 1:1, A Level: 55-65 (bright saw)
- Feedback: 35-40
- Filter: LP4, freq 25, reso 90-110 (squelchy!), env depth 80-100
- Filter env: atk 0, dec 40-60, sus 0, rel 10
- Amp env: atk 0, dec 80, sus 80, rel 10
- Accent/velocity mapped to filter env depth
- Overdrive (fx_over): 15-25 for grit
- Slide/glide between notes

### Detuned Lead (Minilogue-style)
- Algorithm 1 or 5
- Ratio A: 1:1, A Level: 45
- Feedback: 30
- Filter: LP4, freq 60, reso 55, env depth 50
- Filter env: atk 5, dec 70, sus 50, rel 20
- Detune: 8-15 (more than bass — leads can be wider)
- Chorus: 20-35
- LFO: medium triangle on pitch, depth 3-5 (vibrato)

### Analog Kick Drum
- Algorithm 1
- Ratio A: 1:1 or 2:1
- A Level: 80-100 (lots of harmonics for the click)
- Feedback: 15
- Filter: LP4, freq 60, reso 20
- Filter env: atk 0, dec 15-25, sus 0, rel 5 (very fast)
- Amp env: atk 0, dec 30-50, sus 0, rel 10
- Pitch envelope: start high, drop fast to fundamental

---

## Common Mistakes (Why Patches Sound Bad)

1. **Too much modulation depth** — FM gets harsh fast. "Small modulation amounts
   often suffice." Start low, increase gradually.

2. **Not using the filter** — This is the #1 mistake. Raw FM sounds digital.
   Running it through LP4 with an envelope sweep immediately sounds more analog.

3. **Integer ratios too high** — Ratios above 4:1 create glassy/metallic sounds.
   For analog character, stay at 1:1, 2:1, or 3:1.

4. **No detuning** — Perfect mathematical tuning = sterile. Add small detune
   values and/or chorus.

5. **Ignoring feedback** — Using only operator-on-operator modulation when
   feedback alone can give you a saw wave as a starting point.

6. **Too much reverb/delay** — Covering up a thin patch with effects. Fix the
   source sound first.

7. **Not using the amp envelope** — Leaving sustain at max when the sound needs
   shape. Analog sounds have character partly from their envelopes.

---

## The "Subtractive FM" Method (Most Analog-Like Approach)

This is the approach that consistently produces the most analog results:

1. **Start with feedback ~30** on the carrier — gives you a raw sawtooth
2. **Set filter to LP4**, cutoff low (30-40)
3. **Add filter envelope** — sweep the cutoff up (env depth 50-70)
4. **Shape the amp envelope** for your sound type (pad/bass/lead)
5. **Add slight detune** (3-8) and **chorus** (15-30)
6. **Only then** add operator modulation if you want more harmonic complexity
7. Use the modulator's envelope to control how harmonics evolve over time

This reverses the typical FM approach: instead of building up from sine waves,
you start with a harmonically rich tone (feedback saw) and sculpt it down with
the filter — exactly like subtractive synthesis.

---

## Digitone 2-Specific Features for Analog Sound

### Wavetone Machine
- The Digitone 2's wavetone engine can produce waveforms closer to analog
  oscillators than pure FM
- Combined with the multimode filter, this is arguably the easiest path to
  analog-like sounds on the Digi 2

### Multimode Filter
- The Digi 2 adds bandpass and notch filter modes beyond LP/HP
- Bandpass with resonance = vocal, formant-like character
- These expand the analog palette significantly

### Scene System
- Use scenes to morph between bright/dark filter settings
- A→B crossfade mimics the hands-on filter sweeps of analog performance

### Overdrive + SRR
- Overdrive (fx_over 10-25) adds analog-style saturation/warmth
- SRR (sample rate reduction) at low values (5-15) adds subtle grit
  without sounding obviously digital
