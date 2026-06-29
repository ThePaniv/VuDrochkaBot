# VuDrochkaBot

A small Discord bot for a Ukrainian-speaking community server. It does two things,
both driven by voice-channel join/leave/move events:

1. **Otter status** — rewrites a voice channel's *status* line to one 🦦 per member
   plus the grammatically-correct Ukrainian word form
   (`ВиДрочка` / `ВиДрочки` / `ВиДрочок`). Empty channel → `Немає ВиДрочок`.
2. **Voice greetings** *(optional)* — joins the channel and plays a neural
   text-to-speech greeting for each member who joins
   (`Нова видрочка {name} приєдналась!`).

## What's modern here

This is a from-scratch rewrite of the original bot. Notable changes:

| Area | Before | Now |
| --- | --- | --- |
| Voice-channel status | Hand-rolled HTTP call with a **user-account token** (selfbot, violates Discord ToS) | Official `VoiceChannel.edit(status=...)` with the **bot token** (discord.py 2.7) |
| Member-count word | JSON table for 0–10 only (`KeyError` on the 11th member) | Programmatic East-Slavic plural rule — works for any count |
| TTS | `gTTS`, **synchronous** (blocked the event loop) | `edge-tts`, **async-native** neural voices |
| Config | `os.environ` + a leaked absolute Windows path | `pydantic-settings`, typed, validated, `SecretStr` token |
| Packaging | `requirements.txt` | `pyproject.toml` + **uv** lockfile, `src/` layout |
| Container | root, single-stage | **multi-stage uv build, non-root**, ffmpeg |
| CI/CD | broken `$IMAGE_URI`, deprecated actions, static keys | fixed image passing, SHA tags, **OIDC**, current actions |
| Audio queue | `is_playing` never reset (wedged after one disconnect) | self-restarting worker, event-based completion, temp-file cleanup, auto-leave |

## Requirements

- A Discord **bot** application/token: <https://discord.com/developers/applications>
- For status renaming: the bot needs the **Set Voice Channel Status** permission.
- For greetings: **Connect** + **Speak** permissions, and `ffmpeg` (bundled in the image).
- The `voice_states` gateway intent (part of `Intents.default()`, no privileged toggle needed).

## Local development (uv)

```bash
# install uv once: https://docs.astral.sh/uv/getting-started/installation/
uv sync                 # create .venv from uv.lock (downloads Python 3.13 if needed)
cp .env.example .env    # then put your BOT_TOKEN in .env
uv run ruff check .     # lint
uv run pytest           # tests
uv run python -m vudrochka_bot   # run the bot
```

## Run with Docker

```bash
cp .env.example .env    # set BOT_TOKEN (and ENABLE_GREETINGS=true if desired)
docker compose up --build
```

## Configuration

All config comes from environment variables (or a local `.env`). See
[`.env.example`](.env.example).

| Variable | Default | Description |
| --- | --- | --- |
| `BOT_TOKEN` | *(required)* | Discord bot token |
| `ENABLE_GREETINGS` | `false` | Join voice channels and play TTS greetings |
| `JOIN_CHIME` | `true` | Play the bundled hello chime on first connect |
| `TTS_VOICE` | `uk-UA-PolinaNeural` | edge-tts voice (`uk-UA-OstapNeural` is the male voice) |
| `TTS_GREETING_TEMPLATE` | `Нова видрочка {name} приєдналась!` | `{name}` → member display name |
| `COMMAND_PREFIX` | `!` | Legacy text-command prefix |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` / `CRITICAL` |

## Project layout

```
src/vudrochka_bot/
  __main__.py        # entry point (python -m vudrochka_bot)
  bot.py             # commands.Bot subclass + cog wiring
  config.py          # pydantic-settings
  logging_config.py  # logging setup
  pluralization.py   # Ukrainian count-word logic (+ 500-char status cap)
  cogs/
    voice_status.py  # channel status renaming (bot token)
    greetings.py     # TTS greetings + voice connection lifecycle
  services/
    audio.py         # serialized playback queue
    tts.py           # edge-tts wrapper
  assets/hello.mp3   # join chime
tests/               # pytest (pluralization, config, import smoke)
```

## Deployment (AWS ECS Fargate)

`.github/workflows/deploy.yml` builds the image, pushes it to ECR tagged with the
commit SHA, renders [`task-definition.json`](task-definition.json), and deploys to
ECS on push to `main`. Prerequisites:

- A GitHub **OIDC** IAM role; put its ARN in the `AWS_DEPLOY_ROLE_ARN` secret
  (scoped to ECR push + ECS deploy). No long-lived access keys.
- `BOT_TOKEN` stored in **AWS Secrets Manager** at
  `vudrochka-bot/BOT_TOKEN`; the **execution role** needs
  `secretsmanager:GetSecretValue` (+ `kms:Decrypt`) and `logs:CreateLogGroup`.

## Caveat

Discord's voice-channel *status* endpoint is not in the official API docs, though
discord.py supports it natively with a bot token. Discord could change it.

## License

MIT © Andrii Pankiv
