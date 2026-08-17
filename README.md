# App Research Agent -- Phase 1 setup

This is the scaffold for the Composio take-home: an agent that researches
100 apps and reports auth patterns, self-serve status, API surface, and
buildability. This README covers Phase 1 only -- getting your environment
ready. Later phases (the agent itself, verification, the HTML report)
build on top of this.

## What's already here

```
project/
  data/apps.json      the 100 apps from the assignment, structured and ready
  schema.py            the exact "form" every researched app must match
  requirements.txt      python packages this project needs
  .env.example          template for your API keys (copy to .env)
  test_setup.py          run this to confirm Composio is wired up correctly
  output/                 where research results will be saved (Phase 2+)
```

## Step 1: Python environment

You need Python 3.10 or newer. Check with:

```bash
python3 --version
```

Create an isolated environment so this project's packages don't clash
with anything else on your machine, then install dependencies:

```bash
cd project
python3 -m venv .venv
source .venv/bin/activate      # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

You'll know it worked if `pip list` shows `composio`, `pydantic`,
`anthropic`, and `python-dotenv`.

## Step 2: Git repo

This will become the repo you submit, so set it up now:

```bash
git init
git add .
git commit -m "Phase 1: schema, repo scaffold, data/apps.json"
```

Then create an empty repo on GitHub and push:

```bash
git remote add origin <your-repo-url>
git branch -M main
git push -u origin main
```

## Step 3: Composio account

1. Go to composio.dev and sign up (GitHub or email works).
2. Once logged in, open the dashboard and find **Settings > API Keys**.
3. Create a new API key and copy it -- you won't be able to see it again,
   so paste it somewhere safe immediately.
4. In this project folder, copy the env template and fill it in:

   ```bash
   cp .env.example .env
   ```

   Open `.env` and paste your key after `COMPOSIO_API_KEY=`.

5. You'll also need an Anthropic API key (console.anthropic.com) for the
   agent's reasoning step in Phase 2 -- paste that in `ANTHROPIC_API_KEY=`
   too, even though we're not using it yet.

**Never commit `.env`.** It's already excluded via `.gitignore`, but
double check before you push.

## Step 4: Verify the connection

```bash
python test_setup.py
```

Expected output looks like:

```
Connected to Composio.
Session ID: ...
Session has N meta tool(s) available:
 - COMPOSIO_SEARCH_...
 - ...
Setup looks good. You're ready for Phase 2 (the research agent).
```

If this fails, the error message will tell you which piece is missing --
usually a blank or mistyped API key. Fix `.env` and rerun.

## Step 5: Sanity-check the schema

```bash
python schema.py
```

This should print a validated example entry for Stripe as JSON. If you
edit `schema.py` and break something (e.g. set `api_surface="restt"`),
rerunning this will show you a validation error -- that's the schema
doing its job.

## Phase 2: the research agent

New files:

```
explore_composio.py    run this FIRST -- prints Composio's raw toolkit
                         data so you can confirm field names match what
                         composio_lookup.py expects
composio_lookup.py       tier 1: checks if Composio already has a
                         toolkit for the app (ground-truth auth data)
web_researcher.py         tier 2: Claude + web search fills in everything
                         else, for apps not in Composio's catalog
agent.py                   orchestrator -- loops over all 100 apps,
                         merges both tiers, validates, saves results
```

### Run order

```bash
# 1. Confirm Composio's API shape matches what the code expects
python explore_composio.py

# 2. Smoke-test the web researcher on one app
python web_researcher.py

# 3. Test the full pipeline on 5 apps before spending real API calls on 100
python agent.py --limit 5

# 4. Check output/pass_1.json and output/pass_1_failures.json, then
#    run the full batch once you're happy with the results
python agent.py
```

### What to expect

- Each app costs one Claude API call with web search (billed per search +
  tokens) plus one fast, free-ish Composio lookup. Budget accordingly --
  run `--limit 5` and `--limit 20` before committing to all 100.
- Failures are expected and saved separately, not silently dropped --
  check `output/pass_1_failures.json` after each run.
- This is deliberately the *fast, minimally-verified* first pass. Phase 4
  (verification) is where accuracy gets measured and improved -- don't
  try to make this pass perfect, that's not the point of a first pass.

## What's next (Phase 3)

Once `output/pass_1.json` has all 100 apps (or as many as succeeded),
Phase 3 is the verification loop: sample ~15-20 apps, hand-check them
against the real docs, measure this pass's accuracy, then run a
stricter second pass and measure the improvement.
