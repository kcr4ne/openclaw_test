import os
import hashlib
import json
from datetime import datetime
from typing import List, Dict, Tuple

class SmartLogReader:
    """
    Reads log files efficiently by only fetching new lines (Diff-Only).
    Keeps track of file offsets to minimize I/O.
    """
    def __init__(self, state_file: str = "log_offsets.json"):
        self.state_file = state_file
        self.offsets = self._load_offsets()

    def _load_offsets(self) -> Dict[str, int]:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _save_offsets(self):
        with open(self.state_file, 'w') as f:
            json.dump(self.offsets, f)

    def read_new_lines(self, filepath: str) -> List[str]:
        if not os.path.exists(filepath):
            return []

        last_offset = self.offsets.get(filepath, 0)
        current_size = os.path.getsize(filepath)

        # If file was rotated (smaller than last specific offset), reset
        if current_size < last_offset:
            last_offset = 0

        new_lines = []
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                f.seek(last_offset)
                new_lines = f.readlines()
                self.offsets[filepath] = f.tell()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return []
        
        self._save_offsets()
        return [line.strip() for line in new_lines if line.strip()]

class LogDeduplicator:
    """
    Compresses repeated log lines into a single line with a count.
    Example: "Error: Failed to connect" (x50)
    """
    @staticmethod
    def compress(lines: List[str]) -> List[str]:
        if not lines:
            return []

        compressed = []
        if not lines:
            return compressed

        current_line = lines[0]
        count = 1

        for line in lines[1:]:
            # Simple fuzzy matching or exact match
            # For strict system logs, exact match + timestamp removal is usually best
            # Here we do exact match for simplicity of the PoC
            if line == current_line:
                count += 1
            else:
                if count > 1:
                    compressed.append(f"{current_line} (x{count})")
                else:
                    compressed.append(current_line)
                current_line = line
                count = 1
        
        # Append last entry
        if count > 1:
            compressed.append(f"{current_line} (x{count})")
        else:
            compressed.append(current_line)
            
        return compressed

class ContextPruner:
    """
    Manages the sliding window of conversation or log history.
    Keeps 'Critical' events longer, discards 'Info' events faster.
    """
    def __init__(self, max_tokens: int = 1000):
        self.max_tokens = max_tokens
        self.history: List[str] = []

    def get_context(self) -> str:
        # Simple join for now, can be upgraded to token counting
        return "\n".join(self.history)

    def add_event(self, event: str, level: str = "INFO"):
        # Heuristic: If critical, prepend 'CRITICAL' tag
        if level == "CRITICAL":
            event = f"[CRITICAL] {event}"
        
        self.history.append(event)
        
        # Pruning logic: Keep removing from start if too long
        # (Very rough character count approximation for tokens: 1 token ~= 4 chars)
        while len("\n".join(self.history)) > self.max_tokens * 4:
            self.history.pop(0)

class TokenOptimizer:
    """
    Facade for all optimization strategies.
    """
    def __init__(self):
        self.reader = SmartLogReader()
        self.deduplicator = LogDeduplicator()
        self.pruner = ContextPruner()

    def process_log_file(self, filepath: str) -> str:
        raw_lines = self.reader.read_new_lines(filepath)
        if not raw_lines:
            return ""
            
        compressed_lines = self.deduplicator.compress(raw_lines)
        
        # Add to context (could filter further here)
        for line in compressed_lines:
             self.pruner.add_event(line)
             
        # Return mostly for debug or immediate reaction
        return "\n".join(compressed_lines)
