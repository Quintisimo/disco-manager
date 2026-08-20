import re
import subprocess

import numpy as np

# Port of bpm-tools' `bpm` (C) Copyright 2013 Mark Hills, GPLv2.
SAMPLE_RATE = 44100  # bpm-tools assumes this regardless of input, https://www.xmodhub.com/info/xmod-blog/dead-as-disco-custom-music/
LOWER, UPPER = 84.0, 146.0
INTERVAL = 128
BEATS = np.array([-32, -16, -8, -4, -2, -1, 1, 2, 4, 8, 16, 32], dtype=np.float64)
NOBEATS = np.array([-0.5, -0.25, 0.25, 0.5], dtype=np.float64)


def compute_bpm(path):
    """Detect tempo (BPM), replacing the bpm-tools `bpm` binary. Reads mono
    32-bit float PCM from ffmpeg, builds a low-res energy envelope, then scans
    for the interval with the minimum autodifference."""
    raw = subprocess.run(
        f'ffmpeg -v quiet -vn -i "{path}" -ar {SAMPLE_RATE} -ac 1 -f f32le pipe:1',
        shell=True,
        check=True,
        capture_output=True,
    ).stdout
    samples = np.abs(np.frombuffer(raw, dtype="<f4").astype(np.float64)).tolist()

    # Asymmetric PPM energy meter, sampled every INTERVAL samples.
    # ponytail: per-sample recurrence can't vectorize; ~3min song = ~9M python
    # iterations (~1-3s). Move to numba/cython only if this shows up in a profile.
    nrg, v, n = [], 0.0, 0
    for z in samples:
        d = z - v
        v += d / 8 if d > 0 else d / 512
        n += 1
        if n == INTERVAL:
            n, _ = 0, nrg.append(v)
    nrg = np.array(nrg)

    return _scan_for_bpm(nrg, LOWER, UPPER)


def _to_interval(bpm):
    return (SAMPLE_RATE / (bpm / 60)) / INTERVAL


def _scan_for_bpm(nrg, slowest_bpm, fastest_bpm, steps=1024, samples=1024):
    L = len(nrg)
    rng = np.random.default_rng(0)  # bpm-tools uses unseeded drand48 (seed 0)
    slow, fast = _to_interval(slowest_bpm), _to_interval(fastest_bpm)
    intervals = np.linspace(fast, slow, steps + 1)

    best_interval, best = np.nan, np.inf
    for interval in intervals:
        mid = rng.random(samples) * L
        v = nrg[np.floor(mid).astype(int)]
        diff = np.zeros(samples)
        total = 0.0
        for offsets, sign in ((BEATS, 1.0), (NOBEATS, -1.0)):
            for b in offsets:
                idx = np.floor(mid + b * interval)
                ok = (idx >= 0) & (idx < L)
                y = np.where(ok, nrg[np.clip(idx, 0, L - 1).astype(int)], 0.0)
                w = 1.0 / abs(b) if sign > 0 else abs(b)
                diff += sign * w * np.abs(y - v)
                total += w
        t = np.sum(diff / total)
        if t < best:
            best, best_interval = t, interval

    return SAMPLE_RATE / (best_interval * INTERVAL) * 60  # interval_to_bpm


def analyze_audio(path):
    """Detect leading/trailing silence (seconds) and total duration (seconds)
    from an audio file using ffmpeg's silencedetect filter."""
    log = subprocess.run(
        f'ffmpeg -i "{path}" -af silencedetect=noise=-30dB:d=0.3 -f null -',
        shell=True,
        check=True,
        text=True,
        capture_output=True,
    ).stderr

    duration = 0.0
    match = re.search(r"Duration: (\d+):(\d+):(\d+\.\d+)", log)
    if match:
        hours, minutes, seconds = match.groups()
        duration = int(hours) * 3600 + int(minutes) * 60 + float(seconds)

    starts = [float(s) for s in re.findall(r"silence_start: ([\d.]+)", log)]
    ends = [float(s) for s in re.findall(r"silence_end: ([\d.]+)", log)]

    # Leading silence: a silence region that begins at (or near) the very start.
    leading = ends[0] if starts and ends and starts[0] < 0.5 else 0.0

    # Trailing silence: a silence region that begins but never ends (runs to EOF).
    trailing = duration - starts[-1] if len(starts) > len(ends) and duration else 0.0

    return leading, trailing, duration
