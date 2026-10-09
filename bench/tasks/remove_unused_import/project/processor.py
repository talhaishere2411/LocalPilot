import os
import sys
from typing import List


def process_items(items: List[str]) -> List[str]:
    """Process a list of items."""
    return [item.upper() for item in items]
