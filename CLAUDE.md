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

The model, in one breath: six specialist agents each read the same data and
compute their own finding, an Orchestrator routes ideas to the right lever by
trust type, and nothing counts until a human signs it — green = sign-off,
every tier, against a $36.5M/yr target.

## The 6 agents (in `.claude/agents/`)

Each agent reads real synthetic data in the `data/` folder and produces its
own output — nothing is hard-coded:

- `orchestrator` — routes a free-text idea to one of the 10 levers
- `commodity-watch` — checks live steel/rubber/alloy prices and erosion
- `should-cost-analytics` — reads part_master.csv + spend_cube.csv, flags gaps
- `vave-ideation` — reads teardown_ideas.csv + warranty_claims.csv, ranks ideas
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
- This demo is the AGENTS ONLY. Run exactly the commands in the RUN SEQUENCE
  below and nothing else.
- If a live agent call is slow, say "this is calling a real Claude agent now"
  and wait — do not cancel it.
- The decision is the HUMAN's. Always stop and ask; never decide on their
  behalf, never guess their answer, never skip the question to save time.
- Act on the answer you get. If they say yes, go ahead and book it — do not
  re-ask or seek confirmation of a decision they already made.
- Never claim a number the tool did not print. If the screen and your script
  disagree, trust the screen.

## RUN SEQUENCE

### Step 0 — Show the data the agents read
Say: "Everything runs on real data — a part master, a spend cube, warranty
claims, teardown ideas. The agents read these files and compute their own
answers. Nothing is hardcoded."
Run (the reset empties the ledger and clears any decisions from a previous
take, so the demo starts from a clean slate):
```
python cli.py --reset-demo
python cli.py --data
```
Then read out: 40 parts, ~$630M, six data files.

### Step 1 — Show the agents thinking for real, one at a time
Say: "These aren't hard-coded. Here are the real agents running live on Claude
Code — no API key, this is my Claude subscription. Each one reads the data in
data/ and produces its own finding, and each one needs a human signature
before it counts."

Go through these SIX agents, ONE AT A TIME, in this order:

```
commodity-watch
should-cost-analytics
vave-ideation
parts-commonization
orchestrator
savings-ledger
```

For EACH agent, do these three things in order, then move to the next agent:

**1. Run it.** Each takes 15-90s; allow up to 10 minutes and never cancel one
that is still running. While it thinks, say "this is a real Claude agent
running right now."
```
python cli.py --agent <name>
```

**2. Read out ONE concrete thing it found** — a should-cost gap, a VAVE idea,
a commonization pair, a dollar figure. Never read a number the screen did not
print. The output ends with "Awaiting human sign-off", because the finding
counts for nothing until a person signs it.

**3. ASK THE USER "do you want to go ahead with this?" and WAIT.** Use
AskUserQuestion with two options — "Yes, book it" and "No, skip it" — naming
the agent and the dollar figure, e.g. "Go ahead with commodity-watch's
$2.6M/yr finding?". The human decides. Never decide for them, never assume a
yes, never skip the question to save time.

When they answer, record it. On a YES the finding goes into the cost ledger;
on a NO it goes nowhere:
```
python cli.py --sign <name> y --saving <$M/yr>     (yes -> booked)
python cli.py --sign <name> n                      (no  -> not booked)
```
The `--saving` figure MUST be one the agent actually printed on screen. If the
agent printed no dollar figure, pass `--sign <name> y` with no `--saving` —
it records the approval without booking a number you cannot justify.

Act on their answer immediately — a "yes" means go ahead and book it. Do NOT
ask them to confirm a decision they already gave.

Read out what the screen says after: the booking id, and the running ledger
total ("the ledger now stands at $8.8M of $36.5M"). On a rejection say "that
one does not enter the ledger."

**4. ASK whether to move on to the next agent, and WAIT.** Use AskUserQuestion
with "Next agent" and "Hold here" — e.g. "Move on to should-cost-analytics?".
This lets them talk over a finding before the next agent starts. On the last
agent (savings-ledger) skip this and go to Step 2.

Every agent faces this. None is exempt, and nothing enters the ledger except
what the human approved.

Each agent reads data/part_master.csv (and its own file) — so if one ever says
the data is missing, the data/ folder wasn't shipped; check it's present.

### Step 2 — Close
Show what the human actually approved, and the ledger it built:
```
python cli.py --signoff-record
```
Read off the screen: "N/6 agent findings carry a human signature", then the
ledger total and what percent of the $36.5M target it is.

Say: "Six agents, each reading the same data, each computing its own finding —
and the only things in that ledger are the ones a human said yes to. That's
Intent-Driven Savings, and it all runs on Claude Code with no API key."

### Step 3 — OPTIONAL: the answer to the Grand Finale twist
Only run this if the user asks for it, or if a judge asks "so what's your
actual recommendation?". It is analysis, not an agent, and it is instant.
```
python cli.py --plan
```
It recomputes the case against all three pressures — commodity shock, trust
shock, deadline shock — and lands on a recommendation. Read out: the $17.7M of
commercial saving that evaporated, that 71% of direct-material spend is
load-bearing, and the recommended S2 number against the $36.5M target.

## If something breaks on camera
- A command errors: say "let me re-run that", run it once more, move on.
- One agent hangs or fails: the others already made the point. Sign off on
  what did return, say "that one's still thinking, let's move on", go to
  Step 2. Do not cancel a slow agent that is still printing.
- Agent output looks garbled: it shouldn't — cli.py forces UTF-8 output. If
  it ever happens, keep going; the text is readable and the numbers are fine.

Begin at Step 0 when the user says "begin".
