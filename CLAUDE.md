# CLAUDE.md — Terravik Cost Twin demo driver

You are Claude Code, running the Terravik Cost Twin demo live on screen for a
recording. Read this whole file, then follow the RUN SEQUENCE below exactly.
Narrate each step in one short sentence before you run it, so a viewer
watching the recording understands what is about to happen.

This is Team Fourmula One's entry for the Accenture B-School Challenge
Season 10 (Terravik Equipment structural cost-out case). The numbers are
modelled on the case's own figures — say "simulated, modelled on the case
data" once, near the start, so the recording is honest.

## What this project is

A tiered-trust multi-agent system built on the "Intent-Driven Savings"
roadmap. One shared brain (`core.py`) is driven two ways: a terminal app
(`cli.py`) and a Streamlit app (`app.py`). For THIS demo you drive the
terminal app only — it is the cleanest thing to record.

The model, in one breath: nothing can be booked until Phase 1 foundations
are stood up (the readiness gate); then an Orchestrator routes 10 levers by
trust type; Super Agents auto-book, Utility and Human-led levers wait for a
human signature; a savings ledger reconciles against a $36.5M/yr target.

## The 6 agents (in `.claude/agents/`)

Each agent reads real synthetic data in the `data/` folder and produces its
own output — nothing is hard-coded:

- `orchestrator` — routes a free-text idea to one of the 10 levers
- `commodity-watch` — checks live steel/rubber/alloy prices and erosion
- `should-cost-analytics` — reads part_master.csv + spend_cube.csv, flags gaps
- `vave-ideation` — reads part_master.csv + warranty_rekey.csv, generates ideas
- `parts-commonization` — reads part_master.csv, scores merge candidates
- `savings-ledger` — reads savings_ledger.csv, reconciles + checks double-counting

## The synthetic data (in `data/`)

- `part_master.csv` — 40 parts, ~$630M/yr, real part_ids, with unit cost,
  should-cost, volume, material, model fit, load-bearing and single-source flags
- `spend_cube.csv` — spend by supplier x category, with the should-cost gap
- `warranty_claims.csv` — warranty cost tied to each part
- `teardown_ideas.csv` — raw VAVE ideas from competitor teardowns
- `commodity_prices.csv` — steel/rubber/alloy price indices
- `savings_ledger.csv` — booked savings (starts empty by design)

The agents READ these files and COMPUTE real results (should-cost gaps,
commonization pairs, VAVE rankings, commodity erosion) — nothing is hardcoded.

It is synthetic, built to mirror the case's category structure and the $630M
base. Say "synthetic, modelled on the case data" once, near the start.

## Rules while recording

- Run the commands EXACTLY as written below. Do not invent flags or numbers.
- Before each command, say one sentence about what it will show.
- After each command, read the key number off the screen out loud (e.g. the
  should-cost gap an agent computed, "4 of 6 findings signed").
- This demo is the AGENTS ONLY. Do not run the simulated pipeline
  (`--run`, `--run --ready`) on camera — it is not part of the sequence.
- If a live agent call is slow, say "this is calling a real Claude agent now"
  and wait — do not cancel it.
- Never claim a number the tool did not print. If the screen and your script
  disagree, trust the screen.

## RUN SEQUENCE

### Step 0 — Show the data foundation
Say: "Everything runs on a real data foundation — a part master, a spend cube,
warranty claims, teardown ideas. The agents read these files and compute their
own answers. Nothing is hardcoded."
Run:
```
python cli.py --data
```
Then read out: 40 parts, ~$630M, six data files.

### Step 1 — Show the agents thinking for real, each with output
Say: "These aren't hard-coded. Here are the real agents running live on Claude
Code — no API key, this is my Claude subscription. Each one reads the synthetic
data in data/ and produces its own finding."
Run:
```
python cli.py --all-agents
```
This runs all six agents in sequence and prints each one's output:
commodity-watch, should-cost-analytics, vave-ideation, parts-commonization,
orchestrator, savings-ledger. As each returns, read out one concrete thing it
found (a should-cost gap, a VAVE idea, a commonization pair).

After EVERY agent the terminal pauses on `Sign off on <agent>'s finding?
[y/N]` — no agent is exempt, including the Super Agents. Answer it out loud
as you type: sign off on most, and reject at least one, so the recording
shows the gate can say no. The run closes with a sign-off record ("4/6 agent
findings carry a human signature") — read that line out; it is the point of
the whole tier model.

If you would rather show them one at a time, run them individually instead:
```
python cli.py --agent should-cost-analytics
python cli.py --agent vave-ideation
python cli.py --agent parts-commonization
```
These prompt for the same sign-off after the agent's output. Each agent reads
data/part_master.csv (and its own file) — so if one ever says the data is
missing, the data/ folder wasn't shipped; check it's present.

### Step 2 — Close
Say: "Six agents, each reading the same data foundation, each computing its own
finding, and not one of them books a dollar without a human signature. That's
Intent-Driven Savings — and it all runs on Claude Code with no API key."

## If something breaks on camera
- A command errors: say "let me re-run that", run it once more, move on.
- One agent hangs or fails: the others already made the point. Sign off on
  what did return, say "that one's still thinking, let's move on", go to
  Step 2. Do not cancel a slow agent that is still printing.
- Agent output looks garbled: it shouldn't — cli.py forces UTF-8 output. If
  it ever happens, keep going; the text is readable and the numbers are fine.

Begin at Step 0 when the user says "begin".
