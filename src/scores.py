import json
import os
from datetime import datetime


def _get_scores_path():
    """
    Find the right path for scores.json whether running from
    source or as a PyInstaller .exe bundle.
    """
    import sys
    if getattr(sys, 'frozen', False):
        # Running as PyInstaller bundle — save next to the .exe
        base = os.path.dirname(sys.executable)
    else:
        # Running from source
        base = os.path.join(os.path.dirname(__file__), "..")
    return os.path.join(base, "scores.json")

SCORES_FILE = _get_scores_path()


class ScoreEntry:
    def __init__(self, name, total_score, rounds_played, date=None):
        self.name          = name
        self.total_score   = total_score
        self.rounds_played = rounds_played
        # Matches Java: avg = totalScore / rounds (2 decimal places)
        self.avg_score     = round(total_score / rounds_played, 2) if rounds_played else 0.0
        self.date          = date or datetime.now().strftime("%d %b %Y")

    def to_dict(self):
        return {
            "name":          self.name,
            "total_score":   self.total_score,
            "rounds_played": self.rounds_played,
            "avg_score":     self.avg_score,
            "date":          self.date,
        }

    @staticmethod
    def from_dict(d):
        entry = ScoreEntry(
            name          = d["name"],
            total_score   = d["total_score"],
            rounds_played = d["rounds_played"],
            date          = d.get("date", ""),
        )
        entry.avg_score = d.get("avg_score", entry.avg_score)
        return entry


class ScoreManager:
    """
    Matches Java highScores() logic exactly:
    - Ranked by avg score (total / rounds)
    - Top 5 only (Java keeps top 5)
    - Computer players ARE included (Java includes them)
    """

    MAX_ENTRIES = 5  # Java keeps top 5

    def __init__(self):
        self._entries = []
        self._load()

    def _load(self):
        try:
            with open(SCORES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                self._entries = [ScoreEntry.from_dict(d) for d in data]
        except (FileNotFoundError, json.JSONDecodeError):
            self._entries = []

    def _save(self):
        with open(SCORES_FILE, "w", encoding="utf-8") as f:
            json.dump(
                [e.to_dict() for e in self._entries],
                f, indent=2, ensure_ascii=False
            )

    def add_score(self, name, total_score, rounds_played):
        """
        Add score for one player. Matches Java: adds entry per player
        (including Computer), sorts by avg desc, keeps top 5.
        """
        entry = ScoreEntry(name, total_score, rounds_played)
        self._entries.append(entry)
        self._entries.sort(key=lambda e: e.avg_score, reverse=True)
        self._entries = self._entries[:self.MAX_ENTRIES]
        self._save()
        return entry

    def get_entries(self):
        return list(self._entries)

    def get_rank(self, avg_score):
        for i, entry in enumerate(self._entries):
            if avg_score >= entry.avg_score:
                return i + 1
        return len(self._entries) + 1

    def is_high_score(self, avg_score):
        if len(self._entries) < self.MAX_ENTRIES:
            return True
        return avg_score >= self._entries[-1].avg_score