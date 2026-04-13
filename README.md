# OpenCoach

OpenCoach is a Python-only golf swing demo.

The repo-level documentation lives under [/home/matt/Documents/dev/0golf/docs](/home/matt/Documents/dev/0golf/docs).

Start here:

- [Overview](/home/matt/Documents/dev/0golf/docs/overview.md)
- [OpenCoach V0 Execution Plan](/home/matt/Documents/dev/0golf/docs/tasks/opencoach-v0-execution-plan-2026-04-12.md)

Quick commands:

```bash
uv sync --python 3.11
./dev/bootstrap-models.sh
uv run python -m opencoach serve
uv run pre-commit run --all-files
uv run pytest
```

The local app URL is `http://127.0.0.1:8001`.
