import unicodedata
import re
import pandas as pd
from typing import List
import yaml

def normalize_string(s: str) -> str:
    """Normalize string: uppercase, remove accents, symbols."""
    s = s.upper()
    s = ''.join(c for c in unicodedata.normalize('NFD', s)
                if unicodedata.category(c) != 'Mn')
    s = re.sub(r'[^A-Z0-9\s]', '', s)
    return s.strip()

def split_assignees(assignee_str: str) -> List[str]:
    """Split assignees by line breaks and normalize."""
    return list({normalize_string(a) for a in re.split(r'\n|\r|;', assignee_str) if a.strip()})

def extract_first_date(date_str: str) -> str:
    """Extract first date in YYYY-MM-DD format from cell."""
    match = re.search(r'(\d{4}-\d{2}-\d{2})', date_str)
    return match.group(1) if match else ''


def extract_last_percentage(score_str: str) -> float:
    """Extract last percentage from string and convert to float."""
    matches = re.findall(r'(\d+(?:\.\d+)?)%', score_str)
    return float(matches[-1]) if matches else None

def load_config(config_path):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)
