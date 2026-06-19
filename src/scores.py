import json
import os
from datetime import datetime


SCORES_FILE = os.path.join(os.path.dirname(__file__), "..", "scores.json")


class ScoreEntry:
    """A single high score record."""

    def __init__(self, name, total_score, round_scores, rounds_played, date=None):
        self.name          = name
        self.total_score   = total_score
        self.round_scores  = round_scores
        self.rounds_played = rounds_played
        self.avg_score     = round(total_score / rounds_played) if rounds_played else 0
        self.date          = date or datetime.now().strftime("%d %b %Y")

    def to_dict(self):
        return {
            "name":          self.name,
            "total_score":   self.total_score,
            "round_scores":  self.round_scores,
            "rounds_played": self.rounds_played,
            "avg_score":     self.avg_score,
            "date":          self.date,
        }

    @staticmethod
    def from_dict(d):
        entry = ScoreEntry(
            name          = d["name"],
            total_score   = d["total_score"],
            round_scores  = d["round_scores"],
            rounds_played = d["rounds_played"],
            date          = d.get("date", ""),
        )
        # Use stored avg if present, otherwise recalculate
        entry.avg_score = d.get("avg_score", entry.avg_score)
        return entry


class ScoreManager:
    """
    Loads, saves, and ranks high scores from a local JSON file.
    Ranked by AVERAGE score per round (total / rounds_played).
    Keeps the top 10 scores only.
    """

    MAX_ENTRIES = 10

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

    def add_score(self, name, total_score, round_scores, rounds_played):
        """Add entry ranked by avg score, keep top 10, save."""
        entry = ScoreEntry(name, total_score, round_scores, rounds_played)
        self._entries.append(entry)
        # Sort by avg score descending
        self._entries.sort(key=lambda e: e.avg_score, reverse=True)
        self._entries = self._entries[:self.MAX_ENTRIES]
        self._save()
        return entry

    def get_entries(self):
        return list(self._entries)

    def get_rank(self, avg_score):
        """Return what rank this avg score would achieve."""
        for i, entry in enumerate(self._entries):
            if avg_score >= entry.avg_score:
                return i + 1
        return len(self._entries) + 1

    def is_high_score(self, avg_score):
        """Returns True if this avg score makes the top 10."""
        if len(self._entries) < self.MAX_ENTRIES:
            return True
        return avg_score >= self._entries[-1].avg_score