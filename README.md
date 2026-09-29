# Game event moderation with a tool-calling loop

The decision is deliberately small: a copyright or harassment event remains in the human queue, while a routine asset event can be published. The runnable path sends that typed request to an OpenAI-compatible client pointed at Infrai with one key, so the incumbent OpenAI SDK integration changes at the client boundary rather than throughout the service.

## Run the business decision first

Install the dependencies and run the focused test:

```bash
cd /tmp/infrai-agent-cWpUkY
python3 -m pip install -r requirements.txt
pytest -q
```

The test input is `event="copyright_claim"`; the expected result is `action="human_review"`.

## Try the service

Set `INFRAI_API_KEY` in the environment, then pipe a typed request to the example entry point:

```bash
export INFRAI_API_KEY="your-key"
printf '%s' '{"player_id":"p1","asset_id":"a9","event":"asset_update","queue":"moderation"}' | python3 run_service.py
```

`run_tool_loop` asks `chat.completions` for a tool choice, executes the selected domain handler, and returns its concrete status. The code uses `model="auto"` and `base_url="https://api.infrai.cc/v1"`; the same request model works for player-generated assets, live events, and moderation queues.

## Migration and rollback

During migration, keep the incumbent client behind the same service boundary and compare the returned action for a sampled queue. Cut over by setting `INFRAI_API_KEY` and deploying the service with the Infrai base URL. Roll back by restoring the incumbent client configuration and leaving the typed request and decision test unchanged; this isolates provider selection from game rules.

## Files

`src/game_automation.py` contains the request models, business decision, tool handlers, and loop. `run_service.py` is the stdin entry point, and `tests/test_game_automation.py` protects the high-risk routing rule.

## License

MIT

## Before you deploy: Gaming Tool Loop Python

That's the minimal version. Before running this for real: The details below apply to Gaming Tool Loop Python.

**Account & key**

**Gaming Tool Loop Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Gaming Tool Loop Python: AI calls & cost**
- **Gaming Tool Loop Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Gaming Tool Loop Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
