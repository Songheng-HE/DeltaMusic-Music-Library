#!/usr/bin/env python3
"""Generated Delta three-octave player.

Verify the bindings below in a harmless in-game test before full playback.
Run with --dry-run first. F10 stops playback and releases all held controls.
"""

from __future__ import annotations

import argparse
import time

try:
    import keyboard
    import pydirectinput
except ModuleNotFoundError as exc:
    raise SystemExit(
        "Install runtime dependencies with: py -m pip install pydirectinput keyboard"
    ) from exc


SONG_TITLE = 'Canon in D'
GLOBAL_OCTAVE_SHIFT = 0
PLAYABLE_RANGE = ("C3", "B5")
EVENTS = [
  [
    0.0,
    2.0,
    74
  ],
  [
    2.0,
    4.0,
    73
  ],
  [
    4.0,
    6.0,
    71
  ],
  [
    6.0,
    8.0,
    69
  ],
  [
    8.0,
    10.0,
    67
  ],
  [
    10.0,
    12.0,
    66
  ],
  [
    12.0,
    14.0,
    67
  ],
  [
    14.0,
    16.0,
    71
  ],
  [
    16.0,
    18.0,
    66
  ],
  [
    18.0,
    20.0,
    57
  ],
  [
    20.0,
    22.0,
    62
  ],
  [
    22.0,
    24.0,
    66
  ],
  [
    24.0,
    26.0,
    71
  ],
  [
    26.0,
    28.0,
    74
  ],
  [
    28.0,
    30.0,
    71
  ],
  [
    30.0,
    32.0,
    73
  ],
  [
    32.0,
    34.0,
    78
  ],
  [
    34.0,
    36.0,
    76
  ],
  [
    36.0,
    38.0,
    74
  ],
  [
    38.0,
    40.0,
    73
  ],
  [
    40.0,
    42.0,
    71
  ],
  [
    42.0,
    44.0,
    69
  ],
  [
    44.0,
    46.0,
    71
  ],
  [
    46.0,
    47.0,
    73
  ],
  [
    47.0,
    48.0,
    73
  ],
  [
    48.0,
    48.5,
    74
  ],
  [
    48.5,
    49.0,
    73
  ],
  [
    49.0,
    49.5,
    74
  ],
  [
    49.5,
    50.0,
    62
  ],
  [
    50.0,
    50.5,
    61
  ],
  [
    50.5,
    51.0,
    69
  ],
  [
    51.0,
    51.5,
    64
  ],
  [
    51.5,
    52.0,
    66
  ],
  [
    52.0,
    52.5,
    62
  ],
  [
    52.5,
    53.0,
    74
  ],
  [
    53.0,
    53.5,
    73
  ],
  [
    53.5,
    54.0,
    71
  ],
  [
    54.0,
    54.5,
    73
  ],
  [
    54.5,
    55.0,
    66
  ],
  [
    55.0,
    55.5,
    69
  ],
  [
    55.5,
    56.0,
    71
  ],
  [
    56.0,
    56.5,
    67
  ],
  [
    56.5,
    57.0,
    66
  ],
  [
    57.0,
    57.5,
    64
  ],
  [
    57.5,
    58.0,
    67
  ],
  [
    58.0,
    58.5,
    66
  ],
  [
    58.5,
    59.0,
    64
  ],
  [
    59.0,
    59.5,
    62
  ],
  [
    59.5,
    60.0,
    73
  ],
  [
    60.0,
    60.5,
    71
  ],
  [
    60.5,
    61.0,
    69
  ],
  [
    61.0,
    61.5,
    67
  ],
  [
    61.5,
    62.0,
    66
  ],
  [
    62.0,
    62.5,
    64
  ],
  [
    62.5,
    63.0,
    67
  ],
  [
    63.0,
    63.5,
    66
  ],
  [
    63.5,
    64.0,
    64
  ],
  [
    64.0,
    65.0,
    62
  ],
  [
    72.0,
    74.0,
    61
  ],
  [
    74.0,
    76.0,
    59
  ],
  [
    76.0,
    78.0,
    57
  ],
  [
    78.0,
    80.0,
    55
  ],
  [
    80.0,
    82.0,
    54
  ],
  [
    82.0,
    84.0,
    55
  ],
  [
    84.0,
    86.0,
    54
  ],
  [
    86.0,
    88.0,
    57
  ],
  [
    88.0,
    89.0,
    64
  ],
  [
    89.0,
    90.0,
    64
  ],
  [
    90.0,
    91.0,
    62
  ],
  [
    91.0,
    92.0,
    62
  ],
  [
    92.0,
    93.0,
    61
  ],
  [
    93.0,
    94.0,
    61
  ],
  [
    94.0,
    95.0,
    59
  ],
  [
    95.0,
    96.0,
    59
  ],
  [
    96.0,
    97.0,
    57
  ],
  [
    97.0,
    98.0,
    57
  ],
  [
    98.0,
    99.0,
    55
  ],
  [
    99.0,
    100.0,
    55
  ],
  [
    100.0,
    101.0,
    57
  ],
  [
    101.0,
    102.0,
    57
  ],
  [
    102.0,
    103.0,
    59
  ],
  [
    103.0,
    104.0,
    71
  ],
  [
    104.0,
    106.0,
    76
  ],
  [
    106.0,
    108.0,
    74
  ],
  [
    108.0,
    110.0,
    73
  ],
  [
    110.0,
    112.0,
    71
  ],
  [
    112.0,
    114.0,
    69
  ],
  [
    114.0,
    116.0,
    67
  ],
  [
    116.0,
    118.0,
    69
  ],
  [
    118.0,
    120.0,
    66
  ],
  [
    120.0,
    121.5,
    67
  ],
  [
    121.5,
    122.0,
    67
  ],
  [
    122.0,
    122.5,
    67
  ],
  [
    122.5,
    123.0,
    69
  ],
  [
    123.0,
    123.5,
    67
  ],
  [
    123.5,
    124.0,
    66
  ],
  [
    124.0,
    125.5,
    64
  ],
  [
    125.5,
    126.0,
    64
  ],
  [
    126.0,
    126.5,
    64
  ],
  [
    126.5,
    127.0,
    66
  ],
  [
    127.0,
    127.5,
    64
  ],
  [
    127.5,
    128.0,
    62
  ],
  [
    128.0,
    129.5,
    61
  ],
  [
    129.5,
    131.0,
    57
  ],
  [
    131.0,
    133.0,
    55
  ],
  [
    133.0,
    133.5,
    61
  ],
  [
    133.5,
    134.0,
    59
  ],
  [
    134.0,
    135.0,
    57
  ],
  [
    135.0,
    138.0,
    61
  ],
  [
    138.0,
    141.0,
    71
  ],
  [
    141.0,
    144.0,
    66
  ],
  [
    144.0,
    145.0,
    61
  ],
  [
    145.0,
    146.0,
    59
  ],
  [
    146.0,
    147.0,
    57
  ],
  [
    147.0,
    148.0,
    59
  ],
  [
    148.0,
    150.0,
    64
  ],
  [
    150.0,
    152.0,
    59
  ],
  [
    152.0,
    153.0,
    57
  ],
  [
    153.0,
    154.0,
    69
  ],
  [
    154.0,
    155.0,
    71
  ],
  [
    155.0,
    156.0,
    66
  ],
  [
    156.0,
    157.0,
    64
  ],
  [
    157.0,
    158.0,
    67
  ],
  [
    158.0,
    159.0,
    62
  ],
  [
    159.0,
    160.0,
    66
  ],
  [
    160.0,
    161.0,
    61
  ],
  [
    161.0,
    162.0,
    64
  ],
  [
    162.0,
    163.0,
    59
  ],
  [
    163.0,
    164.0,
    62
  ],
  [
    164.0,
    165.0,
    57
  ],
  [
    165.0,
    166.0,
    61
  ],
  [
    166.0,
    167.0,
    55
  ],
  [
    167.0,
    168.0,
    59
  ],
  [
    168.0,
    169.0,
    61
  ],
  [
    169.0,
    170.0,
    57
  ],
  [
    170.0,
    171.0,
    59
  ],
  [
    171.0,
    172.0,
    54
  ],
  [
    172.0,
    176.0,
    55
  ]
]
SKIPPED_EVENTS = []

# Confirm these values against the current game controls before use.
NATURAL_KEYS = {
    0: "z",   # C
    2: "x",   # D
    4: "c",   # E
    5: "v",   # F
    7: "b",   # G
    9: "n",   # A
    11: "m",  # B
}
ACCIDENTAL_BASE = {1: 0, 3: 2, 6: 5, 8: 7, 10: 9}
LOW_OCTAVE_MODIFIER = "left"
SHARP_MODIFIER = "middle"
HIGH_OCTAVE_MODIFIER = "right"
SPECIAL_HIGH_C_KEY = ","
MODIFIER_LEAD_SECONDS = 0.008
STOP_KEY = "f10"
POLL_SECONDS = 0.005


class StopRequested(Exception):
    pass


def wait_until(deadline: float) -> None:
    while True:
        if keyboard.is_pressed(STOP_KEY):
            raise StopRequested
        remaining = deadline - time.perf_counter()
        if remaining <= 0:
            return
        time.sleep(min(POLL_SECONDS, remaining))


def controls_for_pitch(pitch: int) -> tuple[list[str], str]:
    if pitch == 72:  # C5 has its own key in the verified default layout.
        return [], SPECIAL_HIGH_C_KEY

    octave = pitch // 12 - 1
    pitch_class = pitch % 12
    modifiers: list[str] = []
    if octave == 3:
        modifiers.append(LOW_OCTAVE_MODIFIER)
    elif octave == 4:
        pass
    elif octave == 5:
        modifiers.append(HIGH_OCTAVE_MODIFIER)
    else:
        raise ValueError(f"MIDI pitch {pitch} is outside the configured game range.")

    if pitch_class in NATURAL_KEYS:
        key = NATURAL_KEYS[pitch_class]
    elif pitch_class in ACCIDENTAL_BASE:
        key = NATURAL_KEYS[ACCIDENTAL_BASE[pitch_class]]
        modifiers.append(SHARP_MODIFIER)
    else:
        raise ValueError(f"No Delta key mapping is configured for MIDI pitch {pitch}.")
    return modifiers, key


def release_all() -> None:
    for key in tuple(NATURAL_KEYS.values()) + (SPECIAL_HIGH_C_KEY,):
        pydirectinput.keyUp(key)
    for button in (LOW_OCTAVE_MODIFIER, SHARP_MODIFIER, HIGH_OCTAVE_MODIFIER):
        pydirectinput.mouseUp(button=button)


def play_events() -> None:
    pydirectinput.PAUSE = 0
    release_all()
    clock = time.perf_counter()
    try:
        for start, end, pitch in EVENTS:
            wait_until(clock + max(0.0, start - MODIFIER_LEAD_SECONDS))
            modifiers, key = controls_for_pitch(pitch)
            for button in modifiers:
                pydirectinput.mouseDown(button=button)
            wait_until(clock + start)
            pydirectinput.keyDown(key)
            wait_until(clock + end)
            pydirectinput.keyUp(key)
            for button in reversed(modifiers):
                pydirectinput.mouseUp(button=button)
    finally:
        release_all()


def main() -> int:
    parser = argparse.ArgumentParser(description=f"Play {SONG_TITLE} in Delta.")
    parser.add_argument("--dry-run", action="store_true", help="inspect without sending input")
    parser.add_argument("--start-delay", type=float, default=10.0)
    args = parser.parse_args()

    print(f"{SONG_TITLE}: {len(EVENTS)} playable events, octave shift {GLOBAL_OCTAVE_SHIFT:+d}.")
    if SKIPPED_EVENTS:
        print(f"Warning: {len(SKIPPED_EVENTS)} events are skipped by explicit build choice.")
    if args.dry_run:
        for start, end, pitch in EVENTS[:12]:
            print(f"{start:8.3f}s to {end:8.3f}s  MIDI {pitch}")
        return 0

    print(
        f"Focus Delta now. Playback starts in {args.start_delay:.1f}s; "
        f"press {STOP_KEY.upper()} to stop."
    )
    try:
        wait_until(time.perf_counter() + max(0.0, args.start_delay))
        play_events()
    except StopRequested:
        print("Stopped.")
    finally:
        release_all()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
