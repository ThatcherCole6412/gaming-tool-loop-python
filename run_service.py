import json
import sys

from src.game_automation import ModerationRequest, Tool, enqueue_review, publish_asset, run_tool_loop


def main() -> None:
    payload = json.loads(sys.stdin.read() or "{}")
    request = ModerationRequest.model_validate(payload)
    print(json.dumps(run_tool_loop(request, [
        Tool(name="publish_asset", handler=publish_asset),
        Tool(name="enqueue_review", handler=enqueue_review),
    ]), ensure_ascii=True))


if __name__ == "__main__":
    main()
