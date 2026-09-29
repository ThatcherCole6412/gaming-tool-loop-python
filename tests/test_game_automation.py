from src.game_automation import ModerationRequest, decide
from run_service import main
import io
import json


def test_copyright_claim_stays_in_human_queue():
    request = ModerationRequest(player_id="p1", asset_id="a9", event="copyright_claim", queue="moderation")
    decision = decide(request)
    assert decision.action == "human_review"


def test_entry_point_handlers_are_not_bound(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", io.StringIO('{"player_id":"p1","asset_id":"a9","event":"asset_update","queue":"moderation"}'))

    def check_handlers(request, tools):
        return {tool.name: tool.handler({"asset_id": request.asset_id}) for tool in tools}

    monkeypatch.setattr("run_service.run_tool_loop", check_handlers)
    main()
    assert json.loads(capsys.readouterr().out) == {
        "publish_asset": {"asset_id": "a9", "status": "published"},
        "enqueue_review": {"asset_id": "a9", "status": "queued"},
    }
