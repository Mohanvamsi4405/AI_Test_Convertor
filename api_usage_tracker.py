import json
import os
from datetime import datetime
from pathlib import Path

class APIUsageTracker:
    """Track API usage for each key and manage preferences."""

    def __init__(self):
        self.usage_file = Path(__file__).parent / ".usage_stats.json"
        self.prefs_file = Path(__file__).parent / ".api_preferences.json"
        self.load_usage()
        self.load_preferences()

    def load_usage(self):
        """Load usage stats from file."""
        if self.usage_file.exists():
            with open(self.usage_file, 'r') as f:
                self.usage = json.load(f)
        else:
            self.usage = {
                "key1": {"tokens_used": 0, "calls": 0, "last_reset": datetime.now().isoformat()},
                "key2": {"tokens_used": 0, "calls": 0, "last_reset": datetime.now().isoformat()}
            }
            self.save_usage()

    def load_preferences(self):
        """Load user preferences."""
        if self.prefs_file.exists():
            with open(self.prefs_file, 'r') as f:
                self.preferences = json.load(f)
        else:
            self.preferences = {
                "primary_key": "key1",
                "daily_limit_key1": 100000,
                "daily_limit_key2": 100000,
                "fallback_enabled": True
            }
            self.save_preferences()

    def save_usage(self):
        """Save usage stats to file."""
        with open(self.usage_file, 'w') as f:
            json.dump(self.usage, f, indent=2)

    def save_preferences(self):
        """Save preferences to file."""
        with open(self.prefs_file, 'w') as f:
            json.dump(self.preferences, f, indent=2)

    def log_usage(self, key_id: str, tokens_used: int, model: str = None):
        """Log API usage for a key."""
        if key_id not in self.usage:
            self.usage[key_id] = {"tokens_used": 0, "calls": 0, "last_reset": datetime.now().isoformat()}

        self.usage[key_id]["tokens_used"] += tokens_used
        self.usage[key_id]["calls"] += 1
        if model:
            if "models_used" not in self.usage[key_id]:
                self.usage[key_id]["models_used"] = {}
            if model not in self.usage[key_id]["models_used"]:
                self.usage[key_id]["models_used"][model] = {"count": 0, "tokens": 0}
            self.usage[key_id]["models_used"][model]["count"] += 1
            self.usage[key_id]["models_used"][model]["tokens"] += tokens_used

        self.save_usage()
        print(f"[USAGE] {key_id}: {self.usage[key_id]['tokens_used']} total tokens, {self.usage[key_id]['calls']} calls")
        print(f"[FILE] Saved to {self.usage_file}")

    def get_usage_stats(self):
        """Get usage stats for both keys."""
        stats = {}
        for key_id in ["key1", "key2"]:
            if key_id not in self.usage:
                self.usage[key_id] = {"tokens_used": 0, "calls": 0, "last_reset": datetime.now().isoformat()}

            limit = self.preferences.get(f"daily_limit_{key_id}", 100000)
            used = self.usage[key_id]["tokens_used"]
            remaining = max(0, limit - used)
            percentage = (used / limit * 100) if limit > 0 else 0

            stats[key_id] = {
                "tokens_used": used,
                "daily_limit": limit,
                "remaining": remaining,
                "percentage_used": round(percentage, 2),
                "calls_made": self.usage[key_id]["calls"],
                "last_reset": self.usage[key_id]["last_reset"],
                "status": self._get_status(used, limit)
            }

        return stats

    def _get_status(self, used: int, limit: int) -> str:
        """Determine status based on usage."""
        if limit == 0:
            return "unknown"
        percentage = (used / limit * 100)
        if percentage >= 95:
            return "critical"
        elif percentage >= 75:
            return "warning"
        elif percentage >= 50:
            return "moderate"
        else:
            return "good"

    def set_preferences(self, primary_key: str = None, limit_key1: int = None,
                       limit_key2: int = None, fallback_enabled: bool = None):
        """Update user preferences."""
        if primary_key and primary_key in ["key1", "key2"]:
            self.preferences["primary_key"] = primary_key
        if limit_key1 is not None:
            self.preferences["daily_limit_key1"] = limit_key1
        if limit_key2 is not None:
            self.preferences["daily_limit_key2"] = limit_key2
        if fallback_enabled is not None:
            self.preferences["fallback_enabled"] = fallback_enabled

        self.save_preferences()

    def get_preferences(self):
        """Get current preferences."""
        return self.preferences.copy()

    def reset_daily_stats(self):
        """Reset daily usage stats."""
        for key_id in ["key1", "key2"]:
            self.usage[key_id]["tokens_used"] = 0
            self.usage[key_id]["calls"] = 0
            self.usage[key_id]["last_reset"] = datetime.now().isoformat()
            if "models_used" in self.usage[key_id]:
                del self.usage[key_id]["models_used"]

        self.save_usage()

    def get_primary_key(self) -> str:
        """Get the primary key to use."""
        return self.preferences.get("primary_key", "key1")

    def set_primary_key(self, key_id: str):
        """Set primary key."""
        if key_id in ["key1", "key2"]:
            self.preferences["primary_key"] = key_id
            self.save_preferences()

# Global tracker instance
tracker = APIUsageTracker()
