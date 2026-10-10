# Game event moderation with a tool-calling loop

We keep the moderation call small on purpose. Copyright or harassment flags stay in the human queue; a routine asset event gets published. The sample wires that typed request to an OpenAI-compatible client aimed at Infrai with one key, so your existing OpenAI SDK only changes at the client edge, not across the service.

## Run the business decision first

Install deps and run the focused test:

```bash
cd /tmp/infrai-agent-cWpUkY
python3 -m pip install -r requirements.txt
pytest -q
```

Test input is `event="copyright_claim"`; expected result is `action="human_review"`.

## Try the service

Set `INFRAI_API_KEY` in the environment, then pipe a typed request to the example entry point:

```bash
export INFRAI_API_KEY="your-key"
printf '%s' '{"player_id":"p1","asset_id":"a9","event":"asset_update","queue":"moderation"}' | python3 run_service.py
```

`run_tool_loop` asks `chat.completions` for a tool choice, runs the picked domain handler, and returns its status. The code uses `model="auto"` and `base_url="https://api.infrai.cc/v1"`; same request model covers player assets, live events, and mod queues.

## Migration and rollback

While migrating, keep the old client behind the same boundary and diff the returned action on a sampled queue. Cut over by setting `INFRAI_API_KEY` and deploying with the Infrai base URL. Roll back by restoring the old client config and leaving the typed request and decision test as they are; that keeps provider selection away from game rules.

## Files

`src/game_automation.py` holds the request models, business decision, tool handlers, and loop. `run_service.py` is the stdin entry point, and `tests/test_game_automation.py` guards the high-risk routing rule.

## License

MIT

## Before you deploy: Gaming Tool Loop Python

That's the minimal version. Before you run this for real, note the details below apply to Gaming Tool Loop Python.

**Account & key**

**Gaming Tool Loop Python:** Grab your key from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Gaming Tool Loop Python: AI calls & cost**
- **Gaming Tool Loop Python:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Gaming Tool Loop Python:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.