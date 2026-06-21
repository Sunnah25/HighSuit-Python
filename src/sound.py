import os
import math
import struct
import threading

try:
    import pygame
    import numpy as np
    _AVAILABLE = True
except ImportError:
    _AVAILABLE = False


ASSETS = os.path.join(os.path.dirname(__file__), "..", "assets")
MUSIC_FILE = os.path.join(ASSETS, "music.mp3")


def _get_assets_path():
    import sys
    if getattr(sys, 'frozen', False):
        base = sys._MEIPASS
    else:
        base = os.path.join(os.path.dirname(__file__), "..")
    return os.path.join(base, "assets")


ASSETS     = _get_assets_path()
MUSIC_FILE = os.path.join(ASSETS, "music.mp3")


def _make_sound(frequency, duration_ms, volume=0.4, shape="sine"):
    if not _AVAILABLE:
        return None
    try:
        sample_rate = 44100
        n = int(sample_rate * duration_ms / 1000)
        buf = np.zeros(n, dtype=np.float32)

        for i in range(n):
            t = i / sample_rate
            if shape == "sine":
                buf[i] = math.sin(2 * math.pi * frequency * t)
            elif shape == "square":
                buf[i] = 1.0 if math.sin(2 * math.pi * frequency * t) > 0 else -1.0
            elif shape == "triangle":
                buf[i] = 2 * abs(2 * (t * frequency - math.floor(t * frequency + 0.5))) - 1

        attack  = int(n * 0.01)
        decay_s = int(n * 0.1)
        sustain = 0.7
        release = int(n * 0.3)

        env = np.ones(n, dtype=np.float32)
        for i in range(attack):
            env[i] = i / attack
        for i in range(decay_s):
            env[attack + i] = 1.0 - (1.0 - sustain) * i / decay_s
        for i in range(release):
            env[n - release + i] = sustain * (1 - i / release)

        buf = buf * env * volume
        buf_int = (buf * 32767).astype(np.int16)
        stereo  = np.column_stack([buf_int, buf_int])
        return pygame.sndarray.make_sound(stereo)
    except Exception:
        return None


def _make_chord(freqs, duration_ms, volume=0.25):
    if not _AVAILABLE:
        return None
    try:
        sample_rate = 44100
        n   = int(sample_rate * duration_ms / 1000)
        buf = np.zeros(n, dtype=np.float32)
        for f in freqs:
            for i in range(n):
                buf[i] += math.sin(2 * math.pi * f * i / sample_rate)
        buf /= len(freqs)

        fade = int(n * 0.25)
        for i in range(fade):
            buf[n - fade + i] *= (1 - i / fade)

        buf_int = (buf * volume * 32767).astype(np.int16)
        stereo  = np.column_stack([buf_int, buf_int])
        return pygame.sndarray.make_sound(stereo)
    except Exception:
        return None


class SoundManager:
    def __init__(self):
        self._music_on        = True
        self._sfx_on          = True
        self._init_ok         = False
        self._music_started   = False   # KEY FLAG — only start once
        self._sounds          = {}

        if not _AVAILABLE:
            return

        try:
            pygame.mixer.pre_init(44100, -16, 2, 1024)
            pygame.mixer.init()
            self._init_ok = True
            self._build_sounds()
        except Exception:
            pass

    def _build_sounds(self):
        self._sounds = {
            "card":    _make_sound(900,  45,  0.35, "square"),
            "click":   _make_sound(660,  60,  0.3,  "sine"),
            "replace": _make_chord([523, 415, 330], 220, 0.3),
            "suit":    _make_sound(880,  120, 0.35, "sine"),
            "score":   _make_chord([523, 659], 300, 0.35),
            "win":     _make_chord([523, 659, 784, 1047], 700, 0.4),
            "deal":    _make_sound(180,  80,  0.4,  "triangle"),
            "error":   _make_sound(220,  150, 0.3,  "square"),
        }

    def play(self, name):
        if not self._init_ok or not self._sfx_on:
            return
        s = self._sounds.get(name)
        if s:
            try:
                s.play()
            except Exception:
                pass

    def start_music(self):
        """
        Start music ONCE per app session.
        Subsequent calls are ignored — music keeps playing uninterrupted.
        """
        if not self._init_ok or not self._music_on:
            return

        # Already started — do nothing, let it keep playing
        if self._music_started:
            return

        self._music_started = True

        if os.path.exists(MUSIC_FILE):
            try:
                pygame.mixer.music.load(MUSIC_FILE)
                pygame.mixer.music.set_volume(0.35)
                pygame.mixer.music.play(loops=-1)
                return
            except Exception:
                pass

        # Fallback ambient
        threading.Thread(target=self._ambient_loop, daemon=True).start()

    def _ambient_loop(self):
        if not self._init_ok:
            return
        try:
            sample_rate = 44100
            bpm         = 60
            beat        = sample_rate * 60 // bpm
            notes = [261, 329, 392, 329]

            buffers = []
            for freq in notes:
                n   = beat
                buf = np.zeros(n, dtype=np.float32)
                for i in range(n):
                    t = i / sample_rate
                    buf[i] = (
                        0.5 * math.sin(2 * math.pi * freq * t) +
                        0.25 * math.sin(2 * math.pi * freq * 2 * t) +
                        0.1  * math.sin(2 * math.pi * freq * 3 * t)
                    )
                attack  = int(n * 0.05)
                release = int(n * 0.4)
                for i in range(attack):
                    buf[i] *= i / attack
                for i in range(release):
                    buf[n - release + i] *= (1 - i / release)

                buf_int = (buf * 0.12 * 32767).astype(np.int16)
                stereo  = np.column_stack([buf_int, buf_int])
                buffers.append(pygame.sndarray.make_sound(stereo))

            # Loop forever — stops only when app closes
            while self._music_on and self._init_ok:
                for snd in buffers:
                    if not self._music_on:
                        return
                    snd.play()
                    pygame.time.wait(int(60000 / bpm))
        except Exception:
            pass

    def stop_music(self):
        if not self._init_ok:
            return
        self._music_on = False
        try:
            pygame.mixer.music.stop()
            pygame.mixer.stop()
        except Exception:
            pass

    def toggle_music(self):
        if self._music_on:
            self.stop_music()
        else:
            self._music_on      = True
            self._music_started = False   # Allow restart after unmute
            self.start_music()
        return self._music_on

    def toggle_sfx(self):
        self._sfx_on = not self._sfx_on
        return self._sfx_on