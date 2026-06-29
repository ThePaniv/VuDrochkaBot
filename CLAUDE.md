# CLAUDE.md

Guidance for working in this repository.

## What this is

**VuDrochkaBot** — a small Discord bot (Python, `discord.py` 2.7) for a Ukrainian-speaking
server. Two behaviours, both driven by voice-channel join/leave/move events:

1. **Voice-channel status** (always on): renames a channel's status to `N × :otter:` plus the
   grammatically-correct Ukrainian word form (`ВиДрочка` / `ВиДрочки` / `ВиДрочок`); empty → `Немає ВиДрочок`.
2. **TTS greetings** (opt-in, `ENABLE_GREETINGS=true`): joins the channel and plays a neural
   `edge-tts` greeting per joiner.

## Tech stack

Python **3.13**, managed with **uv** (`pyproject.toml` + `uv.lock`, `src/` layout).
Key deps: `discord-py[voice]` 2.7, `edge-tts`, `pydantic-settings`. Tooling: `ruff`, `pytest`, Docker.

## Commands

```bash
uv sync                              # create .venv from the lockfile
uv run python -m vudrochka_bot       # run (needs BOT_TOKEN in .env)
uv run ruff check . && uv run ruff format --check .   # lint + format check
uv run pytest                        # tests
docker compose up -d --build         # run containerized (reads .env)
```

### Local dev caveat (Windows)

On the maintainer's machine, Windows Application Control blocks `.venv\Scripts\python.exe`
(`os error 4551`), so `uv run` / `pytest` fail locally. Lint still works (`ruff` is a native
binary: `uvx ruff check .`). To run/verify **Python**, use Docker:

```bash
# tests on Linux (doesn't touch the host .venv)
docker run --rm -e UV_PROJECT_ENVIRONMENT=/opt/venv -v "$PWD:/app" -w /app \
  ghcr.io/astral-sh/uv:python3.13-trixie-slim uv run --dev --locked pytest
# import smoke test in the real image
docker build -t vudrochka-bot . && docker run --rm vudrochka-bot python -c "import vudrochka_bot.bot; print('ok')"
```

## Architecture (`src/vudrochka_bot/`)

| File | Role |
|---|---|
| `__main__.py` | Entrypoint: load config, set up logging, `bot.run()` |
| `bot.py` | `commands.Bot` subclass; loads cogs (greetings only if enabled) |
| `config.py` | `pydantic-settings`; `BOT_TOKEN` is a `SecretStr` |
| `pluralization.py` | Ukrainian count-word + 500-char status cap — **handles any count** |
| `cogs/voice_status.py` | Renames status via `channel.edit(status=...)` (bot token) |
| `cogs/greetings.py` | Voice connect/greet; per-guild connect lock; auto-leave when alone |
| `services/audio.py` | Serialized playback queue (self-restarting worker, temp-file cleanup) |
| `services/tts.py` | `edge-tts` wrapper (async, non-blocking) |

`tests/` covers the pluralization logic, config validation, and an import smoke test (pure, no network).

## Conventions

- `ruff` formatted, line length 100, target `py313`; keep `from __future__ import annotations` + type hints.
- Config is **env-driven only** — no hardcoded paths or secrets; token via `SecretStr`.
- Event handlers gate on `before.channel != after.channel` so mute/deafen toggles don't trigger work.

## Gotchas / do-not-break

- **Voice-channel status uses the BOT token** via `channel.edit(status=...)` (discord.py ≥ 2.4) and
  needs the **"Set Voice Channel Status"** permission in the guild. **Do NOT reintroduce the old
  user-account / "selfbot" token approach** — it violates Discord ToS and risks an account ban.
- That status endpoint is **undocumented by Discord** and could change.
- Member-count word: always use `vudrochka_word()` / `format_status()`; never a fixed `0..10` table.
- Greetings need `ffmpeg` (in the image) + `PyNaCl` (via `discord-py[voice]`); `edge-tts` must stay
  awaited (never block the event loop).
- **Never bake `.env`/secrets into the image** — `.dockerignore` excludes them; inject at runtime.

## Config (env vars)

`BOT_TOKEN` (required), `ENABLE_GREETINGS`, `JOIN_CHIME`, `TTS_VOICE`, `TTS_GREETING_TEMPLATE`,
`COMMAND_PREFIX`, `LOG_LEVEL`. See [.env.example](.env.example).

## Deployment

Runs as a Docker container (`docker compose`, `restart: unless-stopped`) on an **AWS Lightsail**
instance in eu-central-1. The bot is **no longer on ECS/Fargate** — do not reintroduce an ECS
deploy. `task-definition.json` is a leftover from that era and is unused.

**CD pipeline** ([.github/workflows/deploy.yml](.github/workflows/deploy.yml)): runs on **every
push/merge to `develop`** (or manual dispatch). It first lints + tests (the deploy is gated on that
passing), then builds the image, pushes it to ECR (`vudrochka-bot`, commit-SHA + `latest` tags),
SSHes into the box, renders [compose.prod.yaml](compose.prod.yaml) with the pinned image URI, and
`docker compose pull && up -d`. **The box never builds** — it pulls the pre-built image; ECR auth is
a short-lived token minted on the runner (OIDC), so the box holds no AWS credentials. ([ci.yml](.github/workflows/ci.yml)
runs the same lint+test on pull requests; `develop` pushes are covered by the deploy gate.)

**No GitHub secrets.** AWS is reached by assuming the IAM role
`github-actions-vudrochka-deploy` via GitHub OIDC (the role ARN is hardcoded in the workflow — an
ARN isn't sensitive; the role's trust policy only allows this repo's `deploy`/`develop` refs). The
deploy target (host, `ubuntu` user, default-key-pair private key) is a JSON secret
`vudrochka-bot/deploy` in **AWS Secrets Manager**, fetched at run time. To rotate the IP or key,
update that secret — no workflow change. The box must have `~/vudrochka/.env` (holds `BOT_TOKEN`) —
it's preserved across deploys, never shipped from CI (there is no `BOT_TOKEN` in Secrets Manager).

Manual fallback (e.g. CI down): sync source to `~/vudrochka` and `docker compose up -d --build`
(the dev [compose.yaml](compose.yaml), which builds from source).
