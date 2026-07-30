# MidiDigi — Will's Studio Notebook

This project is Will's studio notebook. Three main uses:

1. **The MidiDigi bridge app** — Reason → Digitone 2 MIDI recording (see below)
2. **Sound design** — e.g. "I want to make a sub bass with the Tetra." Answer using
   the gear's actual manual in `manuals/` for parameter names and menus, with
   concrete settings to try. Aim for his minimal/deep techno sound.
3. **Gear acquisition** — research and buying advice, e.g. "a compressor for the
   ZED-10 that works on all channels with a warm analog feel." Ground advice in
   his existing rig, signal flow (below), vinyl-techno aesthetic, and laptop-free
   live goal.
Will is a techno musician and live performer — not a developer. Keep answers practical,
brief, and music-focused.

Vinyl releases on Cabaret Recordings, Sleepers, Florklang, and Flawed. His sound
sits with artists on those labels plus Perlon, Time Passages, Timeless, and
My Own Jupitor — minimal/deep techno. Frame gear advice and musical suggestions
in that aesthetic.

## HOUSE RULE — gear button/menu questions

When answering ANY question about buttons, key combos, or menus on the Digitone 2
(or any other gear), you MUST first look up the answer in the relevant PDF in
`manuals/` (read with pypdf). NEVER answer from training data — earlier AI tools
invented buttons that don't exist (e.g. a "SOUND" button on the Digitone 2).
If the manual for a piece of gear isn't in `manuals/`, say so instead of guessing.

## The rig

- Elektron Digitone 2 (new to Will — explain its concepts carefully)
- Reason DAW (Will knows it very well) sequencing 6–8 hardware synths via USB MIDI
- Hardware: TB-303, TR-8S, Korg Volca, Minilogue, Arturia Drumbrute, Tetr4, 1010music Blackbox 2
- Goal: fully laptop-free live sets — transfer humanized Reason sequences into the Digitone 2

## Studio signal flow

**MIDI (USB from Reason 12):** MIDI keyboard, TD-3, Digitone 2, Tetra, Minilogue,
TR-8S, Volca Bass, Blackbox 2 — all connected to the computer via USB.

**MIDI (dawless live):** Digitone 2 MIDI Out → TD-3 → Tetra → Blackbox 2 → Minilogue → TR-8S
(daisy-chained via MIDI Thru/Out, each unit on its own channel). BB2 needs TRS-to-DIN
adapter cables (Type A) for its 3.5mm MIDI jacks.

**Audio:**
- Tetra audio → Digitone 2 L audio input
- Blackbox 2 audio → Digitone 2 R audio input
- Digitone 2 stereo out → ZED-10 (Tetra + BB2 mixed inside the Digitone)
- Main mixer: Allen & Heath ZED-10
- Into the ZED-10 directly: computer output, TD-3, Minilogue, TR-8S
- Zoom V3 on the ZED-10 FX send/return for effects

## Safety rules

- NEVER risk disrupting the existing working Reason ↔ hardware MIDI connections.
- Before running anything that sends MIDI (tests, the bridge), confirm Reason is closed
  or that Will explicitly says it's safe.
- The bridge script only reads from IAC Driver Bus 1 and writes to the Digitone 2 USB
  port — it must stay that way.

## The bridge app

- `reason_to_digitone.py` — plays a track in Reason and records the MIDI to the
  Digitone 2 via IAC Driver Bus 1. Flags: `--dry`, `--ports`, `--start`, `--steps`, `--early N`
- `test_timing.py` — clock timing test
- `Reason_Digitone2_Project_Brief.docx` — the project brief (read with python-docx)
- Deps: mido, python-rtmidi, python-docx, pypdf (installed system-wide on the Mac)
- Status: Phases 1 & 2 done and code-reviewed; end-to-end dry run verified 2026-03-22
  (notes flowing on ch1 and ch10). NOT yet tested live with the Digitone connected.
- Phase 3 (not started): song definition file (YAML/JSON), batch recording mode,
  post-recording report
- Reason setup done: MIDI Clock out on IAC Driver Bus 1, Send Clock enabled.
  Channel 1 = TR-8S, Channel 10 = Minilogue (NOT ch2 as in default CHANNEL_MAP)

## Manuals

All gear manuals live in `manuals/`:

- `manuals/Digitone-2-User-Manual_ENG_OS1.10D_251022.pdf`
- `manuals/minilogue_OM_E5.pdf` — Korg Minilogue owner's manual
- `manuals/TD-3_Manual.pdf` — Behringer TD-3 quick start guide (the "TB-303")
- `manuals/Tetra_Manual_v1.3.pdf` — Dave Smith Instruments Tetra (Tetr4) operation manual
- `manuals/TR-8S_Manual.pdf` — Roland TR-8S quick start guide (24 pages)
- `manuals/TR-8S_Reference_Manual.pdf` — Roland TR-8S full reference manual (56 pages, has MIDI settings incl. Soft Thru)
- `manuals/volca_bass_OM.pdf` — Korg Volca Bass owner's manual (multi-language fold-out, 2 large pages)
- `manuals/DL241_operators_manual.pdf` — Drawmer DL241 dual auto compressor/limiter
- `manuals/DL251_operators_manual.pdf` — Drawmer DL251 spectral compressor (scanned PDF, text extraction unreliable — use pypdf with care)
- `manuals/Blackbox_User_Manual_3.0.pdf` — 1010music Blackbox original user manual v3.0 (123 pages)
- `manuals/Blackbox2_User_Manual.pdf` — 1010music Blackbox 2 user guide v1.0.1 (173 pages, July 2026)
- `manuals/mioXL_User_Manual.pdf` — iConnectivity mio X-Series user guide (26 pages, covers mioXL and mioXM)
- `manuals/MRCC_User_Manual.pdf` — Conductive Labs MRCC user manual v1.1.020 (54 pages)

### Sound design reference guides

These guides inform FM patch design on the Digitone 2. Read them when translating
a user's sound description into FM parameters.

- `manuals/FM_Synthesis_Basics_EtherDiver.md` — Core FM programming reference: operators, ratios, modulation depth, feedback, envelope shaping, and a "sound idea → FM parameter" translation table
- `manuals/FM_Synthesis_Patches_EDMProd.md` — Practical FM patch recipes (bass growl, frozen pad, lead) with design principles
- `manuals/Basic_FM_Synthesis_DX7_MarkPhillips.pdf` — 30-page hands-on FM programming tutorial for the DX7 (4/6-op concepts transfer directly to Digitone 2)
- `manuals/Drexciya_Electro_Sound_Design.md` — Detroit electro synthesis techniques, gear analysis, and Digitone 2 translation table (Drexciya, electro aesthetic)
- `manuals/Aphex_Twin_SAW_Production.md` — Selected Ambient Works 85-92 production breakdown: FM pad techniques (DX7/DX100), effects processing, lo-fi aesthetic, and Digitone 2 translation table

## Preset designer

`preset_designer.py` — natural language interface to the Digitone 2 over USB MIDI.
Port: `Elektron Digitone II`. Presets saved in `presets/` as JSON.
`send_acid_bounce.py` — standalone script for the first preset (can be retired).

Two modes:
1. **Describe → patch**: user describes a sound, Claude translates to Digitone params
   and sends via `send_preset()`.
2. **Audio → patch**: user provides a WAV, `analyze_audio()` extracts spectral features,
   Claude interprets them and designs an approximate patch.

Key functions:
- `send_preset(preset, track, machine, fltr)` — send a full preset dict
- `tweak(changes, track, machine, fltr)` — send just a few param changes ("make it warmer")
- `analyze_audio(filepath)` — returns pitch, harmonics, envelope, noise, modulation
- `mute(track)` / `unmute(track)` — track mute/unmute via CC 94
- `set_track_level(track, level)` — CC 95
- `change_pattern(pattern)` — Program Change (1-128 or 'A01'-'H16')

Machine/filter type must be set on the unit before sending (can't be changed via MIDI).
User must save presets manually via [PRESET/KIT] button (top row, labelled PERFORM in
turquoise — press WITHOUT [FUNC]).

Deps: mido, python-rtmidi, numpy, scipy (all in venv).

## Gear acquisition

- `gear_wishlist.html` — gear acquisition page (open in Chrome to view)
- Will is building a 6U rack (22"W × 14"D × 14"H) for studio + dawless live use
- All sound sources must respond to MIDI so the Digitone 2 can sequence them live
- Frame gear suggestions around his rig, signal flow, and laptop-free live goal
