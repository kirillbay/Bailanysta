"""Hashtag extraction and normalization."""

import re

MAX_HASHTAGS_PER_POST = 20
MAX_HASHTAG_LEN = 50

# Allow letters, numbers, underscore; case-insensitive, normalized lower
HASHTAG_RE = re.compile(r"#([A-Za-z0-9_]{1,50})")

def extract_hashtags(content: str) -> list[str]:
    if not content:
        return []
    raw = HASHTAG_RE.findall(content)
    seen = set()
    result = []
    for tag in raw:
        name = tag.strip().lower()
        if not name:
            continue
        if len(name) > MAX_HASHTAG_LEN:
            continue
        # exclude pure numbers? allow but keep
        if name in seen:
            continue
        seen.add(name)
        result.append(name)
        if len(result) >= MAX_HASHTAGS_PER_POST:
            break
    return result
