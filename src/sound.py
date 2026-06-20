import os
import threading

# Graceful fallback if pygame not installed
try:
    import pygame
    _PYGAME_AVAILABLE = True
except ImportError:
    _PYGAME_AVAILABLE = False


class SoundManager:
    """
    Manages background music and sound effects using pygame.
    All methods are safe to call even if pygame is unavailable.
    """

    # Free-to-use sound URLs we'll generate programmatically instead
    # We create simple tones using pygame synthesizer

    def __init__(self):
        self._music_on = True
        self._sfx_on   = True
        self._init_ok  = False

        if not _PYGAME_AVAILABLE:
            return

        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
            self._init_ok = True
            self._sounds  = self._generate_sounds()
        except Exception:
            self._init_ok = False

    def _generate_sounds(self):
        """Generate simple tones programmatically — no audio files needed."""
        import numpy as np
        import struct

        def make_tone(freq, duration, volume=0.3, wave="sine"):
            sample_rate = 44100
            n_samples   = int(sample_rate * duration)
            buf         = []
            for i in range(n_samples):
                t = i / sample_rate
                if wave == "sine":
                    val = volume * __import__("math").sin(2 * __import__("math").pi * freq * t)
                else:
                    val = volume * (1 if (i // (sample_rate // (freq * 2))) % 2 == 0 else -1)
                # Fade out last 10%
                fade = min(1.0, (n_samples - i) / (n_samples * 0.1))
                val *= fade
                sample = int(val * 32767)
                buf.append(struct.pack("<h", max(-32768, min(32767, sample))))
                buf.append(struct.pack("<h", max(-32768, min(32767, sample))))  # stereo

            raw = b"".join(buf)
            sound = pygame.sndarray.make_sound(
                __import__("numpy").frombuffer(raw, dtype="<i2").reshape(-1, 2)
            )
            return sound

        try:
            import numpy
            return {
                "click":   make_tone(440,  0.08, 0.2),
                "card":    make_tone(330,  0.12, 0.25),
                "replace": make_tone(523,  0.15, 0.25),
                "score":   make_tone(659,  0.3,  0.3),
                "win":     make_tone(784,  0.6,  0.35),
                "deal":    make_tone(294,  0.1,  0.2),
            }
        except Exception:
            return {}

    def play(self, name):
        """Play a named sound effect."""
        if not self._init_ok or not self._sfx_on:
            return
        sound = self._sounds.get(name)
        if sound:
            try:
                sound.play()
            except Exception:
                pass

    def start_music(self):
        """
        Start looping background music (gentle ambient tone loop).
        Runs in a background thread.
        """
        if not self._init_ok or not self._music_on:
            return
        threading.Thread(target=self._music_loop, daemon=True).start()

    def _music_loop(self):
        """Simple ambient background — cycles quiet tones."""
        if not self._init_ok:
            return
        import math, struct, numpy
        try:
            sample_rate = 44100
            duration    = 4.0
            n           = int(sample_rate * duration)
            buf = []
            freqs = [130, 164, 196, 220]   # C2, E2, G2, A2 — calm chord
            for i in range(n):
                t   = i / sample_rate
                val = sum(
                    0.04 * math.sin(2 * math.pi * f * t)
                    for f in freqs
                )
                # Slow volume swell
                swell = 0.5 + 0.5 * math.sin(2 * math.pi * t / duration)
                val  *= swell
                s = int(val * 32767)
                s = max(-32768, min(32767, s))
                buf.append(struct.pack("<h", s))
                buf.append(struct.pack("<h", s))

            raw   = b"".join(buf)
            music = pygame.sndarray.make_sound(
                numpy.frombuffer(raw, dtype="<i2").reshape(-1, 2)
            )
            music.set_volume(0.18)
            music.play(loops=-1)   # Loop forever
        except Exception:
            pass

    def stop_music(self):
        if self._init_ok:
            try:
                pygame.mixer.stop()
            except Exception:
                pass

    def toggle_music(self):
        self._music_on = not self._music_on
        if self._music_on:
            self.start_music()
        else:
            self.stop_music()
        return self._music_on

    def toggle_sfx(self):
        self._sfx_on = not self._sfx_on
        return self._sfx_on