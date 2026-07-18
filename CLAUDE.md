# MidiDigi — Will's Studio Notebook

This project is Will's studio notebook AND the Reason → Digitone 2 MIDI bridge app.
Will is a techno musician and live performer — not a developer. Keep answers practical,
brief, and music-focused.

## HOUSE RULE — gear button/menu questions

When answering ANY question about buttons, key combos, or menus on the Digitone 2
(or any other gear), you MUST first look up the answer in the relevant PDF in
`manuals/` (read with pypdf). NEVER answer from training data — earlier AI tools
invented buttons that don't exist (e.g. a "SOUND" button on the Digitone 2).
If the manual for a piece of gear isn't in `manuals/`, say so instead of guessing.

## The rig

- Elektron Digitone 2 (new to Will — explain its concepts carefully)
- Reason DAW (Will knows it very well) sequencing 6–8 hardware synths via USB MIDI
- Hardware: TB-303, TR-8S, Korg Volca, Minilogue, Arturia Drumbrute, Tetr4
- Goal: fully laptop-free live sets — transfer humanized Reason sequences into the Digitone 2

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

Will also asks for advice on new gear purchases — frame suggestions around his rig
and laptop-free live performance goal.
