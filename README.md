# MidiDigi — Reason → Digitone 2 MIDI Bridge

Python script that listens to Reason's MIDI clock on IAC Driver Bus 1, forwards all note/CC data to the Elektron Digitone 2, and fires Program Change messages at pattern boundaries so the Digitone auto-advances through patterns — one pattern per Reason loop.

## Requirements

```
pip install mido python-rtmidi
```

## Usage

```bash
python3 reason_to_digitone.py            # normal recording session
python3 reason_to_digitone.py --ports    # list MIDI ports and exit
python3 reason_to_digitone.py --dry      # dry run (no Digitone required)
python3 reason_to_digitone.py --start 16 # start from pattern B01
python3 reason_to_digitone.py --steps 32 # use 32-step patterns
python3 reason_to_digitone.py --early 8  # adjust PC lead time (default: 12 pulses)
```

## One-Time Setup

### Reason
1. Preferences → Sync → MIDI Clock Output: **IAC Driver Bus 1**
2. Tick **"Send MIDI clock while sequencer is stopped"**
3. Transport panel → enable **"Send MIDI Clock"**
4. Each MIDI Out Device → set channel to match Digitone track (see CHANNEL_MAP in script)

### Digitone 2
1. Each track → SYN page → CHAN = matching channel number
2. SETTINGS → MIDI CONFIG → SYNC → Clock Receive: **OFF**
3. SETTINGS → MIDI CONFIG → SYNC → Transport Receive: **OFF**
4. SETTINGS → MIDI CONFIG → SYNC → PRG CH RECEIVE: **ON**
5. Connect via USB

### Mac
IAC Driver Bus 1 must be active: Audio MIDI Setup → MIDI Studio → IAC Driver → enable

## Config (top of script)

| Variable | Default | Description |
|---|---|---|
| `IAC_INPUT_PORT` | `"IAC Driver Bus 1"` | Reason's MIDI output |
| `DIGITONE_OUTPUT` | `"Digitone 2"` | Digitone USB port name |
| `BPM` | `120` | Must match Reason's tempo |
| `STEPS_PER_PAT` | `64` | Steps per pattern (32/64/128) |
| `START_PATTERN` | `0` | 0=A01, 16=B01, 127=H16 |
| `PC_EARLY_PULSES` | `12` | Lead time for pattern change (½ 16th note) |

## Channel Map (default)

| Ch | Instrument |
|---|---|
| 1 | TR-8S |
| 2 | Minilogue |
| 3 | TB-303 |
| 4 | Drumbrute |
| 5 | Tetr4 |
| 6 | Volca |

## How It Works

1. Waits for MIDI `start` from Reason
2. Counts clock pulses (24 PPQN × steps per pattern)
3. Sends Program Change `PC_EARLY_PULSES` before pattern end so Digitone queues next pattern
4. Resets pulse counter at pattern boundary, advances pattern index
5. On `stop`: sends CC 123 (all notes off) on all 16 channels to prevent stuck notes
6. On `continue`: resets pulse counter and warns to disable Reason loop mode

## Manuals

- [Digitone 2 User Manual](Digitone-2-User-Manual_ENG_OS1.10D_251022.pdf)
- [Reason / Digitone 2 Project Brief](Reason_Digitone2_Project_Brief.docx)

## Phase Status

- **Phase 1** ✓ — Clock timing, bridge logic, port flags
- **Phase 2** ✓ — Loop handling, all-notes-off on stop, send error handling, `--early` flag
- **Phase 3** — Song definition file (YAML/JSON), batch recording mode, post-recording report
