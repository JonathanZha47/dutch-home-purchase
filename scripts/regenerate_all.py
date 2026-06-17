#!/usr/bin/env python3
"""Regenerate all dashboard pages after search or analysis."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from sync_inbox import main as sync_inbox
from generate_search_board import main as gen_search
from generate_dashboard import main as gen_dashboard


def main() -> None:
    sync_inbox()
    gen_search()
    sys.argv = ["generate_dashboard.py"]
    gen_dashboard()


if __name__ == "__main__":
    main()
