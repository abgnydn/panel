# Deploy Panel

Two paths, in order of effort:

1. [Streamlit Community Cloud](#streamlit-community-cloud) — free, 5 minutes, public URL
2. [Databricks Apps](#databricks-apps) — required for the hackathon submission

## Streamlit Community Cloud

The repo is already configured: `requirements.txt` at the root, main file at `app/app.py`.

### One-time setup

1. Open **https://share.streamlit.io**.
2. Sign in with the GitHub account that owns this repo.
3. **"New app"** → pick `abgnydn/panel` → branch `master` → **main file**: `app/app.py`.
4. (Optional) **Advanced settings → Python version**: pick **3.11** or **3.12**.
5. (Optional) **App URL**: customise the subdomain (e.g. `panel-app.streamlit.app`).
6. Click **Deploy**. First build takes 2–3 minutes.

### Add secrets

While the build runs, open **Settings → Secrets** in the app dashboard and paste:

```toml
GEMINI_API_KEY = "AI..."       # Free tier, no card — easiest path
# ANTHROPIC_API_KEY = "sk-ant-..."  # Optional; required for image OCR
# OPENAI_API_KEY = "sk-..."         # Optional
```

Save → app restarts automatically with the new secrets in `st.secrets`.

### Pick the provider in the UI

After deploy:

1. Open the app URL.
2. Sidebar → **🔌 Backend** → switch the **Provider** dropdown to whichever provider's key you set.
3. The key from `st.secrets` is auto-picked up; the sidebar key field can stay blank.
4. Click **🔍 Test connection** → green check.
5. Run a sample contract.

### What won't work on Streamlit Cloud

- **`claude_cli` provider** — there's no `claude` CLI on the sandbox runner. Use Anthropic / Gemini / OpenAI instead.
- **LM Studio** — local-only. Skip.
- **SQLite persistence** — Streamlit Cloud filesystems are ephemeral; sessions reset on app restart. Fine for demo; not production memory.

### Updating

Push to `master` → Streamlit Cloud auto-redeploys within ~1 minute.

## Databricks Apps

For the actual hackathon submission. Requires the Databricks workspace + $700 Express credits.

```bash
# Once your workspace is provisioned:
databricks bundle deploy --target dev
databricks bundle run panel-app
```

Open `databricks.yml` for the bundle config. The app will need Lakebase + Agent Bricks + a Genie Space + Mosaic AI model serving wired in — see `docs/spec.md` for the full integration map.
