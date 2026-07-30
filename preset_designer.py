#!/usr/bin/env python3
"""
Digitone 2 Preset Designer — natural language → patch → MIDI CC

Send presets to the Digitone 2 over USB MIDI by specifying parameters
with human-readable names. Analyze audio files to reverse-engineer
approximate synth settings.

Usage (CLI):
  python3 preset_designer.py ports                     # list MIDI ports
  python3 preset_designer.py send patch.json --track 7  # send a preset file
  python3 preset_designer.py analyze audio.wav          # analyze audio
  python3 preset_designer.py machines                   # list machines & params
  python3 preset_designer.py read --track 3             # read current CC values (via request)

Primary usage is conversational — called by Claude to send patches.
"""

import mido
import time
import sys
import json
import argparse
from pathlib import Path

# ═══════════════════════════════════════════════════════════════════
# MIDI CC MAP — from Digitone 2 manual Appendix C (pages 112-117)
# These CC numbers are constant regardless of which machine is loaded.
# SYN page knobs are "machine dependent" — same CC, different param.
# ═══════════════════════════════════════════════════════════════════

CC = {
    # ── SYN Page 1 (knobs A-H) ──
    'syn1a': 40, 'syn1b': 41, 'syn1c': 42, 'syn1d': 43,
    'syn1e': 44, 'syn1f': 45, 'syn1g': 46, 'syn1h': 47,
    # ── SYN Page 2 ──
    'syn2a': 48, 'syn2b': 49, 'syn2c': 50, 'syn2d': 51,
    'syn2e': 52, 'syn2f': 53, 'syn2g': 54, 'syn2h': 55,
    # ── SYN Page 3 ──
    'syn3a': 56, 'syn3b': 57, 'syn3c': 58, 'syn3d': 59,
    'syn3e': 60, 'syn3f': 61, 'syn3g': 62, 'syn3h': 63,
    # ── SYN Page 4 ──
    'syn4a': 70, 'syn4b': 71, 'syn4c': 72, 'syn4d': 73,
    'syn4e': 74, 'syn4f': 75, 'syn4g': 76, 'syn4h': 77,

    # ── FLTR ──
    'fltr_atk':  20, 'fltr_dec':  21, 'fltr_sus':  22, 'fltr_rel': 23,
    'fltr_freq': 16, 'fltr_f':   17, 'fltr_g':    18, 'fltr_env': 24,
    'fltr_del':  19, 'fltr_key':  26,
    'fltr_base': 27, 'fltr_wdth': 28, 'fltr_rst':  25,

    # ── AMP ──
    'amp_atk':  84, 'amp_hold': 85, 'amp_dec':  86,
    'amp_sus':  87, 'amp_rel':  88,  # CC 87 for sus (manual may have typo showing 86)
    'amp_rst':  92, 'amp_mode': 91,
    'amp_pan':  89, 'amp_vol':  90,

    # ── FX ──
    'fx_br':     78, 'fx_over':   81, 'fx_srr':    79,
    'fx_srr_rt': 80, 'fx_od_rt':  82,
    'fx_del':    30, 'fx_rev':    31, 'fx_chr':    29,

    # ── LFO 1 ──
    'lfo1_spd': 102, 'lfo1_mult': 103, 'lfo1_fade': 104,
    'lfo1_dest': 105, 'lfo1_wave': 106, 'lfo1_sph': 107,
    'lfo1_mode': 108, 'lfo1_depth': 109,

    # ── LFO 2 ──
    'lfo2_spd': 111, 'lfo2_mult': 112, 'lfo2_fade': 113,
    'lfo2_dest': 114, 'lfo2_wave': 115, 'lfo2_sph': 116,
    'lfo2_mode': 117, 'lfo2_depth': 118,

    # ── Track ──
    'track_mute':  94, 'track_level': 95,
}

# LFO 3 — no CC, NRPN only (MSB = 1)
LFO3_NRPN = {
    'lfo3_spd':   58, 'lfo3_mult': 59, 'lfo3_fade': 60,
    'lfo3_dest':  61, 'lfo3_wave': 62, 'lfo3_sph':  70,
    'lfo3_mode':  71, 'lfo3_depth': 72,
}


# ═══════════════════════════════════════════════════════════════════
# LFO WAVEFORMS AND DESTINATIONS
# ═══════════════════════════════════════════════════════════════════

LFO_WAVE = {
    'tri': 0, 'sine': 1, 'sqr': 2, 'saw': 3,
    'expo': 4, 'ramp': 5, 'rand': 6,
}

LFO_MODE = {
    'free': 0, 'trig': 1, 'hold': 2, 'one': 3, 'half': 4,
}

# Destination indices (Appendix D) — sequential list from the manual.
# SYN destinations cover pages 1-4 per knob (8 knobs × 4 pages = 32 entries).
LFO_DEST = {
    'none': 0,
    # LFO1 params (targets for LFO2/3 only)
    'lfo1_spd': 1, 'lfo1_mult': 2, 'lfo1_fade': 3, 'lfo1_wave': 4,
    'lfo1_sph': 5, 'lfo1_mode': 6, 'lfo1_depth': 7,
    # LFO2 params (targets for LFO3 only)
    'lfo2_spd': 8, 'lfo2_mult': 9, 'lfo2_fade': 10, 'lfo2_wave': 11,
    'lfo2_sph': 12, 'lfo2_mode': 13, 'lfo2_depth': 14,
    # SYN page 1 knobs A-H
    'syn1a': 15, 'syn1b': 16, 'syn1c': 17, 'syn1d': 18,
    'syn1e': 19, 'syn1f': 20, 'syn1g': 21, 'syn1h': 22,
    # SYN page 2
    'syn2a': 23, 'syn2b': 24, 'syn2c': 25, 'syn2d': 26,
    'syn2e': 27, 'syn2f': 28, 'syn2g': 29, 'syn2h': 30,
    # SYN page 3
    'syn3a': 31, 'syn3b': 32, 'syn3c': 33, 'syn3d': 34,
    'syn3e': 35, 'syn3f': 36, 'syn3g': 37, 'syn3h': 38,
    # SYN page 4
    'syn4a': 39, 'syn4b': 40, 'syn4c': 41, 'syn4d': 42,
    'syn4e': 43, 'syn4f': 44, 'syn4g': 45, 'syn4h': 46,
    # FLTR
    'fltr_atk': 47, 'fltr_dec': 48, 'fltr_sus': 49, 'fltr_rel': 50,
    'fltr_freq': 51, 'fltr_f': 52, 'fltr_g': 53, 'fltr_env': 54,
    'fltr_del': 55, 'fltr_key': 56, 'fltr_base': 57, 'fltr_wdth': 58,
    'fltr_rst': 59,
    # AMP
    'amp_atk': 60, 'amp_hold': 61, 'amp_dec': 62, 'amp_sus': 63,
    'amp_rel': 64, 'amp_pan': 65, 'amp_vol': 66,
    # FX
    'fx_del': 67, 'fx_rev': 68, 'fx_chr': 69,
    'fx_br': 70, 'fx_srr': 71, 'fx_srr_rt': 72, 'fx_over': 73,
}


# ═══════════════════════════════════════════════════════════════════
# MACHINE DEFINITIONS — map human-readable names to knob keys
# ═══════════════════════════════════════════════════════════════════

MACHINES = {
    'fm_tone': {
        'name': 'FM Tone',
        'params': {
            # Page 1
            'algo': 'syn1a', 'ratio_a': 'syn1b', 'ratio_b': 'syn1c',
            'harm': 'syn1d', 'dtun': 'syn1e', 'fdbk': 'syn1f', 'mix': 'syn1g',
            # Page 2
            'atk_a': 'syn2a', 'dec_a': 'syn2b', 'end_a': 'syn2c', 'lev_a': 'syn2d',
            'atk_b': 'syn2e', 'dec_b': 'syn2f', 'end_b': 'syn2g', 'lev_b': 'syn2h',
            # Page 3
            'adel': 'syn3a', 'atrg': 'syn3b', 'arst': 'syn3c', 'phrt': 'syn3d',
            'bdel': 'syn3e', 'btrg': 'syn3f', 'brst': 'syn3g',
            # Page 4
            'ratio_ofs_c': 'syn4a', 'ratio_ofs_a': 'syn4b',
            'ratio_ofs_b1': 'syn4c', 'ratio_ofs_b2': 'syn4d',
            'key_trk_a': 'syn4e', 'key_trk_b1': 'syn4f', 'key_trk_b2': 'syn4g',
        },
    },
    'fm_drum': {
        'name': 'FM Drum',
        'params': {
            # Page 1
            'tune': 'syn1a', 'stim': 'syn1b', 'sdep': 'syn1c', 'algo': 'syn1d',
            'op_c': 'syn1e', 'op_ab': 'syn1f', 'fdbk': 'syn1g', 'fold': 'syn1h',
            # Page 2
            'ratio_a': 'syn2a', 'dec_a': 'syn2b', 'end_a': 'syn2c', 'mod_a': 'syn2d',
            'ratio_b': 'syn2e', 'dec_b': 'syn2f', 'end_b': 'syn2g', 'mod_b': 'syn2h',
            # Page 3
            'hold': 'syn3a', 'dec': 'syn3b', 'ph_c': 'syn3c', 'lev': 'syn3d',
            'nrst': 'syn3e', 'nrm': 'syn3f',
            # Page 4
            'nhld': 'syn4a', 'ndec': 'syn4b', 'tran': 'syn4c', 'tlev': 'syn4d',
            'n_base': 'syn4e', 'n_wdth': 'syn4f', 'gran': 'syn4g', 'nlev': 'syn4h',
        },
    },
    'wavetone': {
        'name': 'Wavetone',
        'params': {
            # Page 1
            'tun1': 'syn1a', 'wav1': 'syn1b', 'pd1': 'syn1c', 'lev1': 'syn1d',
            'tun2': 'syn1e', 'wav2': 'syn1f', 'pd2': 'syn1g', 'lev2': 'syn1h',
            # Page 2
            'ofs1': 'syn2a', 'tbl1': 'syn2b', 'mod': 'syn2c', 'rset': 'syn2d',
            'ofs2': 'syn2e', 'tbl2': 'syn2f',
            # Page 3 (noise)
            'n_atk': 'syn3a', 'n_hold': 'syn3b', 'n_dec': 'syn3c', 'nlev': 'syn3d',
            'n_base': 'syn3e', 'n_wdth': 'syn3f', 'n_type': 'syn3g', 'n_char': 'syn3h',
        },
    },
    'swarmer': {
        'name': 'Swarmer',
        'params': {
            # Page 1
            'tune': 'syn1a', 'swrm': 'syn1b', 'det': 'syn1c', 'mix': 'syn1d',
            'm_oct': 'syn1e', 'main': 'syn1f', 'anim': 'syn1g', 'n_mod': 'syn1h',
        },
    },
}

FILTERS = {
    'multi_mode': {
        'name': 'Multi-Mode',
        'params': {
            'freq': 'fltr_freq', 'reso': 'fltr_f', 'type': 'fltr_g', 'env': 'fltr_env',
            'atk': 'fltr_atk', 'dec': 'fltr_dec', 'sus': 'fltr_sus', 'rel': 'fltr_rel',
        },
    },
    'lowpass4': {
        'name': 'Lowpass 4',
        'params': {
            'freq': 'fltr_freq', 'reso': 'fltr_f', 'env': 'fltr_env',
            'atk': 'fltr_atk', 'dec': 'fltr_dec', 'sus': 'fltr_sus', 'rel': 'fltr_rel',
        },
    },
    'legacy': {
        'name': 'Legacy LP/HP',
        'params': {
            'freq': 'fltr_freq', 'reso': 'fltr_f', 'type': 'fltr_g', 'env': 'fltr_env',
            'atk': 'fltr_atk', 'dec': 'fltr_dec', 'sus': 'fltr_sus', 'rel': 'fltr_rel',
        },
    },
    'comb_minus': {
        'name': 'Comb-',
        'params': {
            'freq': 'fltr_freq', 'fdbk': 'fltr_f', 'lpf': 'fltr_g', 'env': 'fltr_env',
            'atk': 'fltr_atk', 'dec': 'fltr_dec', 'sus': 'fltr_sus', 'rel': 'fltr_rel',
        },
    },
    'comb_plus': {
        'name': 'Comb+',
        'params': {
            'freq': 'fltr_freq', 'fdbk': 'fltr_f', 'lpf': 'fltr_g', 'env': 'fltr_env',
            'atk': 'fltr_atk', 'dec': 'fltr_dec', 'sus': 'fltr_sus', 'rel': 'fltr_rel',
        },
    },
}


# ═══════════════════════════════════════════════════════════════════
# DEFAULT PORT
# ═══════════════════════════════════════════════════════════════════

DEFAULT_PORT = "Elektron Digitone II"
CC_DELAY = 0.015  # 15ms between messages


# ═══════════════════════════════════════════════════════════════════
# MIDI SENDING
# ═══════════════════════════════════════════════════════════════════

def _clamp(value):
    return max(0, min(127, int(round(value))))


def _send_cc(port, cc, value, channel):
    port.send(mido.Message('control_change', channel=channel, control=cc, value=_clamp(value)))
    time.sleep(CC_DELAY)


def _send_nrpn(port, msb, lsb, value, channel):
    _send_cc(port, 99, msb, channel)
    _send_cc(port, 98, lsb, channel)
    _send_cc(port, 6, value, channel)


def _resolve_key(key, machine=None, fltr=None):
    """Resolve a parameter name to a CC knob key.

    Accepts either:
      - A knob key directly: 'syn1a', 'fltr_freq', 'amp_atk', etc.
      - A machine-specific name: 'algo', 'ratio_a' (requires machine)
      - A filter-specific name: 'freq', 'reso' (requires fltr, prefixed 'f_')
    """
    # Already a known CC key
    if key in CC:
        return key

    # Try machine params
    if machine and machine in MACHINES:
        params = MACHINES[machine]['params']
        if key in params:
            return params[key]

    # Try filter params (prefix 'f_' to disambiguate from machine params)
    bare_key = key[2:] if key.startswith('f_') else key
    if fltr and fltr in FILTERS:
        params = FILTERS[fltr]['params']
        if bare_key in params:
            return params[bare_key]

    return key  # return as-is, will fail at CC lookup if invalid


def send_preset(preset, track=1, machine=None, fltr=None, port_name=DEFAULT_PORT):
    """Send a preset to the Digitone 2.

    Args:
        preset: dict of parameter names → values (0-127).
                Keys can be knob keys ('syn1a'), machine names ('algo'),
                or filter names with 'f_' prefix ('f_freq').
                Special keys: 'lfo1', 'lfo2', 'lfo3' → dicts with LFO params.
        track: track number 1-16
        machine: machine name for resolving SYN param names (e.g. 'fm_tone')
        fltr: filter name for resolving FLTR param names (e.g. 'comb_minus')
        port_name: MIDI output port name
    """
    channel = track - 1  # zero-indexed

    try:
        port = mido.open_output(port_name)
    except (IOError, OSError) as e:
        print(f"ERROR: Could not open '{port_name}': {e}")
        return False

    print(f"Sending preset to track {track} (ch {track})...")
    sent = 0

    # Send regular CC params
    for key, value in preset.items():
        if key.startswith('lfo') and isinstance(value, dict):
            continue  # handle LFOs separately

        resolved = _resolve_key(key, machine, fltr)
        if resolved in CC:
            _send_cc(port, CC[resolved], value, channel)
            sent += 1
        else:
            print(f"  WARNING: unknown param '{key}' (resolved: '{resolved}')")

    # Send LFOs
    for lfo_key in ('lfo1', 'lfo2', 'lfo3'):
        if lfo_key not in preset:
            continue
        lfo = preset[lfo_key]
        _send_lfo(port, lfo_key, lfo, channel)
        sent += len(lfo)

    port.close()
    print(f"Done — {sent} parameters sent.")
    return True


def _send_lfo(port, lfo_key, params, channel):
    """Send LFO parameters, resolving wave/dest names."""
    prefix = lfo_key  # 'lfo1', 'lfo2', 'lfo3'

    # Resolve destination name to index
    dest = params.get('dest', 0)
    if isinstance(dest, str):
        dest = LFO_DEST.get(dest, 0)

    # Resolve waveform name to index
    wave = params.get('wave', 0)
    if isinstance(wave, str):
        wave = LFO_WAVE.get(wave, 0)

    # Resolve mode name to index
    mode = params.get('mode', 0)
    if isinstance(mode, str):
        mode = LFO_MODE.get(mode, 0)

    resolved = {
        f'{prefix}_spd':   params.get('spd', 64),
        f'{prefix}_mult':  params.get('mult', 0),
        f'{prefix}_fade':  params.get('fade', 64),
        f'{prefix}_dest':  dest,
        f'{prefix}_wave':  wave,
        f'{prefix}_sph':   params.get('sph', 0),
        f'{prefix}_mode':  mode,
        f'{prefix}_depth': params.get('depth', 0),
    }

    if prefix in ('lfo1', 'lfo2'):
        for param_key, value in resolved.items():
            if param_key in CC:
                _send_cc(port, CC[param_key], value, channel)
    elif prefix == 'lfo3':
        for param_key, value in resolved.items():
            nrpn_key = param_key  # same key name
            if nrpn_key in LFO3_NRPN:
                _send_nrpn(port, 1, LFO3_NRPN[nrpn_key], _clamp(value), channel)


def tweak(changes, track=1, machine=None, fltr=None, port_name=DEFAULT_PORT):
    """Send only specific parameter changes (for 'make it warmer' etc.)."""
    channel = track - 1
    try:
        port = mido.open_output(port_name)
    except (IOError, OSError) as e:
        print(f"ERROR: Could not open '{port_name}': {e}")
        return False

    for key, value in changes.items():
        resolved = _resolve_key(key, machine, fltr)
        if resolved in CC:
            _send_cc(port, CC[resolved], value, channel)
        elif resolved in LFO3_NRPN:
            _send_nrpn(port, 1, LFO3_NRPN[resolved], _clamp(value), channel)
        else:
            print(f"  WARNING: unknown param '{key}'")

    port.close()
    print(f"Tweaked {len(changes)} params on track {track}.")
    return True


# ═══════════════════════════════════════════════════════════════════
# LIVE CONTROL — mute, pattern change, track level
# ═══════════════════════════════════════════════════════════════════

def _open_port(port_name=DEFAULT_PORT):
    try:
        return mido.open_output(port_name)
    except (IOError, OSError) as e:
        print(f"ERROR: Could not open '{port_name}': {e}")
        return None


def mute(track, port_name=DEFAULT_PORT):
    """Mute a track (1-16)."""
    port = _open_port(port_name)
    if not port:
        return False
    _send_cc(port, 94, 1, track - 1)
    port.close()
    print(f"Track {track} muted.")
    return True


def unmute(track, port_name=DEFAULT_PORT):
    """Unmute a track (1-16)."""
    port = _open_port(port_name)
    if not port:
        return False
    _send_cc(port, 94, 0, track - 1)
    port.close()
    print(f"Track {track} unmuted.")
    return True


def mute_tracks(tracks, port_name=DEFAULT_PORT):
    """Mute multiple tracks at once. tracks = list of track numbers."""
    port = _open_port(port_name)
    if not port:
        return False
    for t in tracks:
        _send_cc(port, 94, 1, t - 1)
    port.close()
    print(f"Muted tracks: {tracks}")
    return True


def unmute_tracks(tracks, port_name=DEFAULT_PORT):
    """Unmute multiple tracks at once."""
    port = _open_port(port_name)
    if not port:
        return False
    for t in tracks:
        _send_cc(port, 94, 0, t - 1)
    port.close()
    print(f"Unmuted tracks: {tracks}")
    return True


def set_track_level(track, level, port_name=DEFAULT_PORT):
    """Set a track's level (0-127)."""
    port = _open_port(port_name)
    if not port:
        return False
    _send_cc(port, 95, level, track - 1)
    port.close()
    print(f"Track {track} level → {level}")
    return True


def change_pattern(pattern, port_name=DEFAULT_PORT):
    """Change pattern via Program Change.

    Args:
        pattern: pattern number 1-128, or string like 'A01'-'H16'
    """
    if isinstance(pattern, str):
        pattern = _pattern_to_pc(pattern)
    else:
        pattern = pattern - 1  # 0-indexed for MIDI

    port = _open_port(port_name)
    if not port:
        return False
    # Program Change on channel 0 (auto channel behavior)
    port.send(mido.Message('program_change', channel=0, program=_clamp(pattern)))
    time.sleep(CC_DELAY)
    port.close()
    print(f"Pattern change → {pattern + 1}")
    return True


def _pattern_to_pc(pattern_str):
    """Convert 'A01'-'H16' to program change number 0-127."""
    pattern_str = pattern_str.upper().strip()
    bank = ord(pattern_str[0]) - ord('A')  # 0-7
    num = int(pattern_str[1:]) - 1          # 0-15
    return bank * 16 + num


# ═══════════════════════════════════════════════════════════════════
# AUDIO ANALYSIS — extract features from audio files to guide
#                   patch design
# ═══════════════════════════════════════════════════════════════════

def analyze_audio(filepath):
    """Analyze an audio file and return spectral characteristics.

    Returns a dict with features useful for designing Digitone patches:
      - fundamental_hz, note_name
      - harmonics (relative strengths)
      - spectral_centroid (brightness)
      - attack_ms, decay_ms
      - noise_ratio
      - modulation (detected LFO-like movement)
    """
    try:
        import numpy as np
        from scipy.io import wavfile
        from scipy import signal as sig
        from scipy.fft import rfft, rfftfreq
    except ImportError:
        print("ERROR: numpy and scipy required. Install: pip install numpy scipy")
        return None

    filepath = Path(filepath)
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        return None

    # Read audio
    if filepath.suffix.lower() in ('.wav', '.wave'):
        sr, data = wavfile.read(str(filepath))
    else:
        print(f"ERROR: Unsupported format '{filepath.suffix}'. Use WAV.")
        return None

    # Convert to mono float
    if data.ndim > 1:
        data = data.mean(axis=1)
    if data.dtype != np.float64:
        data = data.astype(np.float64) / np.iinfo(data.dtype).max

    duration = len(data) / sr
    results = {'file': str(filepath), 'duration_s': round(duration, 2), 'sample_rate': sr}

    # ── Fundamental frequency (autocorrelation method) ──
    # Use a chunk from the sustain portion
    chunk_start = min(int(0.05 * sr), len(data) // 4)  # skip attack
    chunk_len = min(int(0.1 * sr), len(data) - chunk_start)
    chunk = data[chunk_start:chunk_start + chunk_len]

    if len(chunk) > 0:
        corr = np.correlate(chunk, chunk, mode='full')
        corr = corr[len(corr) // 2:]
        # Find first peak after the initial drop
        min_lag = int(sr / 2000)  # max 2kHz
        max_lag = int(sr / 20)    # min 20Hz
        if max_lag < len(corr) and min_lag < max_lag:
            search = corr[min_lag:max_lag]
            if len(search) > 0:
                peak_idx = np.argmax(search) + min_lag
                fund_hz = sr / peak_idx
                results['fundamental_hz'] = round(fund_hz, 1)
                results['note_name'] = _hz_to_note(fund_hz)

    # ── Spectrum analysis ──
    N = min(8192, len(data))
    spectrum_chunk = data[chunk_start:chunk_start + N]
    if len(spectrum_chunk) < N:
        spectrum_chunk = np.pad(spectrum_chunk, (0, N - len(spectrum_chunk)))

    window = np.hanning(N)
    spectrum = np.abs(rfft(spectrum_chunk * window))
    freqs = rfftfreq(N, 1 / sr)

    # Spectral centroid (brightness indicator)
    if spectrum.sum() > 0:
        centroid = np.sum(freqs * spectrum) / np.sum(spectrum)
        results['spectral_centroid_hz'] = round(centroid, 0)
        if centroid < 500:
            results['brightness'] = 'dark'
        elif centroid < 1500:
            results['brightness'] = 'warm'
        elif centroid < 3000:
            results['brightness'] = 'medium'
        elif centroid < 6000:
            results['brightness'] = 'bright'
        else:
            results['brightness'] = 'very bright'

    # ── Harmonic analysis ──
    fund = results.get('fundamental_hz', 0)
    if fund > 20:
        harmonics = []
        fund_mag = 0
        for h in range(1, 17):
            target_hz = fund * h
            if target_hz > sr / 2:
                break
            idx = int(target_hz * N / sr)
            if idx < len(spectrum):
                # Search small window around expected frequency
                lo = max(0, idx - 3)
                hi = min(len(spectrum), idx + 4)
                mag = np.max(spectrum[lo:hi])
                if h == 1:
                    fund_mag = mag
                if fund_mag > 0:
                    harmonics.append({
                        'harmonic': h,
                        'hz': round(target_hz, 0),
                        'relative_db': round(20 * np.log10(max(mag / fund_mag, 1e-10)), 1),
                    })
        results['harmonics'] = harmonics

        # Classify harmonic content
        if len(harmonics) >= 3:
            odd_avg = np.mean([h['relative_db'] for h in harmonics if h['harmonic'] % 2 == 1])
            even_avg = np.mean([h['relative_db'] for h in harmonics if h['harmonic'] % 2 == 0 and h['harmonic'] > 1] or [0])
            if even_avg < -20:
                results['harmonic_character'] = 'odd harmonics dominant (square/pulse-like)'
            elif abs(odd_avg - even_avg) < 6:
                results['harmonic_character'] = 'full harmonic series (saw-like)'
            else:
                results['harmonic_character'] = 'mixed harmonics'

    # ── Amplitude envelope ──
    envelope = np.abs(data)
    # Smooth with a window
    win_size = int(sr * 0.005)  # 5ms window
    if win_size > 0 and len(envelope) > win_size:
        kernel = np.ones(win_size) / win_size
        envelope = np.convolve(envelope, kernel, mode='same')

        peak_idx = np.argmax(envelope)
        peak_val = envelope[peak_idx]

        if peak_val > 0:
            # Attack time: 10% to 90% of peak
            threshold_lo = 0.1 * peak_val
            threshold_hi = 0.9 * peak_val
            atk_start = np.argmax(envelope > threshold_lo)
            atk_end = np.argmax(envelope > threshold_hi)
            attack_ms = (atk_end - atk_start) / sr * 1000
            results['attack_ms'] = round(max(0, attack_ms), 1)

            if attack_ms < 5:
                results['attack_character'] = 'percussive'
            elif attack_ms < 30:
                results['attack_character'] = 'snappy'
            elif attack_ms < 100:
                results['attack_character'] = 'moderate'
            else:
                results['attack_character'] = 'slow/pad-like'

            # Decay: time from peak to 37% of peak (1/e)
            decay_threshold = peak_val * 0.37
            after_peak = envelope[peak_idx:]
            decay_indices = np.where(after_peak < decay_threshold)[0]
            if len(decay_indices) > 0:
                decay_ms = decay_indices[0] / sr * 1000
                results['decay_ms'] = round(decay_ms, 1)
            else:
                results['decay_ms'] = round(len(after_peak) / sr * 1000, 1)
                results['sustain'] = True

    # ── Noise content ──
    if fund > 20 and len(spectrum) > 0:
        # Estimate noise by looking at energy between harmonics
        harmonic_bins = set()
        for h in range(1, 17):
            idx = int(fund * h * N / sr)
            for offset in range(-3, 4):
                harmonic_bins.add(idx + offset)

        all_energy = np.sum(spectrum ** 2)
        harmonic_energy = sum(spectrum[i] ** 2 for i in harmonic_bins if 0 <= i < len(spectrum))
        if all_energy > 0:
            noise_ratio = 1 - (harmonic_energy / all_energy)
            results['noise_ratio'] = round(noise_ratio, 2)
            if noise_ratio < 0.1:
                results['noise_character'] = 'clean/tonal'
            elif noise_ratio < 0.3:
                results['noise_character'] = 'slightly noisy'
            elif noise_ratio < 0.6:
                results['noise_character'] = 'noisy'
            else:
                results['noise_character'] = 'very noisy/textural'

    # ── Modulation detection ──
    # Look for amplitude modulation (tremolo/LFO) by analyzing envelope spectrum
    if len(envelope) > sr // 2:
        env_chunk = envelope[:min(len(envelope), sr * 2)]  # up to 2 seconds
        env_spectrum = np.abs(rfft(env_chunk - np.mean(env_chunk)))
        env_freqs = rfftfreq(len(env_chunk), 1 / sr)
        # Look for peaks in 0.5-30 Hz range (typical LFO range)
        lfo_mask = (env_freqs >= 0.5) & (env_freqs <= 30)
        if np.any(lfo_mask):
            lfo_spectrum = env_spectrum[lfo_mask]
            lfo_freqs_masked = env_freqs[lfo_mask]
            if lfo_spectrum.max() > np.median(env_spectrum) * 3:
                mod_freq = lfo_freqs_masked[np.argmax(lfo_spectrum)]
                results['modulation_hz'] = round(mod_freq, 2)
                results['modulation_character'] = (
                    'slow drift' if mod_freq < 2 else
                    'moderate wobble' if mod_freq < 8 else
                    'fast vibrato'
                )

    return results


def _hz_to_note(hz):
    """Convert frequency to nearest note name."""
    if hz <= 0:
        return '?'
    import math
    notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    midi = 69 + 12 * math.log2(hz / 440)
    midi_round = int(round(midi))
    note = notes[midi_round % 12]
    octave = (midi_round // 12) - 1
    cents_off = round((midi - midi_round) * 100)
    cents_str = f" ({cents_off:+d}¢)" if abs(cents_off) > 5 else ""
    return f"{note}{octave}{cents_str}"


def print_analysis(results):
    """Pretty-print audio analysis results."""
    if not results:
        return

    print(f"\n{'═' * 50}")
    print(f"  AUDIO ANALYSIS: {results.get('file', '?')}")
    print(f"{'═' * 50}")
    print(f"  Duration:    {results.get('duration_s', '?')}s")
    print(f"  Sample rate: {results.get('sample_rate', '?')} Hz")

    if 'fundamental_hz' in results:
        print(f"\n  Pitch:       {results['fundamental_hz']} Hz ({results.get('note_name', '?')})")

    if 'brightness' in results:
        print(f"  Brightness:  {results['brightness']} (centroid: {results.get('spectral_centroid_hz', '?')} Hz)")

    if 'harmonic_character' in results:
        print(f"  Harmonics:   {results['harmonic_character']}")
        if 'harmonics' in results:
            for h in results['harmonics'][:8]:
                bar = '█' * max(0, int((h['relative_db'] + 40) / 3))
                print(f"    H{h['harmonic']:2d} ({h['hz']:>6.0f} Hz): {h['relative_db']:+6.1f} dB {bar}")

    if 'attack_character' in results:
        print(f"\n  Attack:      {results['attack_character']} ({results.get('attack_ms', '?')} ms)")
    if 'decay_ms' in results:
        sus = " (sustains)" if results.get('sustain') else ""
        print(f"  Decay:       {results['decay_ms']} ms{sus}")

    if 'noise_character' in results:
        print(f"  Noise:       {results['noise_character']} (ratio: {results.get('noise_ratio', '?')})")

    if 'modulation_hz' in results:
        print(f"  Modulation:  {results['modulation_character']} ({results['modulation_hz']} Hz)")

    print(f"{'═' * 50}\n")


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════

def cmd_ports():
    print("Available MIDI output ports:")
    for name in mido.get_output_names():
        marker = " ◄ Digitone" if "Digitone" in name else ""
        print(f"  {name}{marker}")


def cmd_machines():
    print("\n── SYN Machines ──")
    for key, m in MACHINES.items():
        params = ', '.join(m['params'].keys())
        print(f"  {key:15s} ({m['name']}): {params}")
    print("\n── FLTR Machines ──")
    for key, f in FILTERS.items():
        params = ', '.join(f['params'].keys())
        print(f"  {key:15s} ({f['name']}): {params}")
    print()


def cmd_send(args):
    filepath = Path(args.file)
    if not filepath.exists():
        print(f"ERROR: File not found: {filepath}")
        sys.exit(1)

    with open(filepath) as f:
        data = json.load(f)

    preset = data.get('preset', data)
    machine = data.get('machine', args.machine)
    fltr = data.get('filter', args.filter)
    track = data.get('track', args.track)

    send_preset(preset, track=track, machine=machine, fltr=fltr)


def cmd_analyze(args):
    results = analyze_audio(args.file)
    if results:
        print_analysis(results)
        if args.json:
            print(json.dumps(results, indent=2))


def main():
    parser = argparse.ArgumentParser(description='Digitone 2 Preset Designer')
    sub = parser.add_subparsers(dest='command')

    sub.add_parser('ports', help='List MIDI ports')
    sub.add_parser('machines', help='List machines and parameters')

    p_send = sub.add_parser('send', help='Send preset from JSON file')
    p_send.add_argument('file', help='JSON preset file')
    p_send.add_argument('--track', type=int, default=1, help='Track number (1-16)')
    p_send.add_argument('--machine', default=None, help='SYN machine name')
    p_send.add_argument('--filter', default=None, help='FLTR machine name')

    p_analyze = sub.add_parser('analyze', help='Analyze audio file')
    p_analyze.add_argument('file', help='WAV audio file')
    p_analyze.add_argument('--json', action='store_true', help='Output raw JSON')

    args = parser.parse_args()

    if args.command == 'ports':
        cmd_ports()
    elif args.command == 'machines':
        cmd_machines()
    elif args.command == 'send':
        cmd_send(args)
    elif args.command == 'analyze':
        cmd_analyze(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
