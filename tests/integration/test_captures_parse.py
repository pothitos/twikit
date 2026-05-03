"""
Offline checks using saved X API JSON (see captures/).

Requires ``captures/trends_response.json`` and ``captures/search_response.json``
(recorded from Firefox). These assert parsing matches current timeline shapes.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

CAPTURES_DIR = Path(__file__).resolve().parents[2] / 'captures'


pytestmark = pytest.mark.skipif(
    not (CAPTURES_DIR / 'trends_response.json').exists()
    or not (CAPTURES_DIR / 'search_response.json').exists(),
    reason='captures/*.json not present',
)


def test_parse_trends_from_capture():
    from twikit.client.client import Client

    client = Client('en-US')
    data = json.loads((CAPTURES_DIR / 'trends_response.json').read_text())
    results = client._trends_from_generic_timeline_response(data)
    assert len(results) >= 5
    assert any(t.name for t in results)


def test_parse_search_tweets_from_capture():
    from twikit.client.client import Client
    from twikit.tweet import tweet_from_data
    from twikit.utils import find_dict

    client = Client('en-US')
    data = json.loads((CAPTURES_DIR / 'search_response.json').read_text())
    instructions = find_dict(data, 'instructions', find_one=True)[0]
    items_ = find_dict(instructions, 'entries', find_one=True)
    items = items_[0] if items_ else []

    tweets = []
    for item in items:
        if not item['entryId'].startswith(('tweet', 'search-grid')):
            continue
        tw = tweet_from_data(client, item)
        if tw is not None:
            tweets.append(tw)

    assert len(tweets) >= 5
