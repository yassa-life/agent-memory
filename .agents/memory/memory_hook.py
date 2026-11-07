"""Best-effort Antigravity hook for keeping project memory fresh."""

import json
import sys
from pathlib import Path

MEMORY_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MEMORY_DIR.parents[1]
sys.path.insert(0, str(MEMORY_DIR))


def main() -> None:
    mode = sys.argv[1] if len(sys.argv) > 1 else "post_tool"
    if mode == "pre_invocation":
        synced = (MEMORY_DIR / "context.md").exists()
        message = (
            "Project memory is ready. Read .agents/memory/context.md before broad filesystem exploration. Refresh it after meaningful repository changes."
            if synced else
            "Project memory could not be refreshed; continue normally and run the memory scan when practical."
        )
        print(json.dumps({"injectSteps": [{"ephemeralMessage": message}]}))
    else:
        try:
            from memory_manager import scan
            scan(PROJECT_ROOT)
        except Exception:
            pass
        print(json.dumps({}))


if __name__ == "__main__":
    main()
