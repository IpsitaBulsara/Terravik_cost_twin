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

The model, in one breath: specialist agents each read the same data and compute
their own findings, an Orchestrator routes ideas to the right lever by trust
type, and nothing counts until a human signs it — green = sign-off, every tier,
against a $36.5M/yr target on a ~$730M addressable base.

## The agents (in `.claude/agents/`)

Each agent reads real data in the `data/` folder and produces its own output —
nothing is hard-coded. FOUR run in the demo, one per trust tier, and each asks
a DIFFERENT question:

- `should-cost-analytics` — SUPER AGENT. part_master + spend_cube, gap per
  part. Puts a straight yes/no in front of a human.
- `parts-commonization` — SUPER AGENT. part_master, scores merge candidates.
  Straight yes/no.
- `freight-lane` — UTILITY. freight_lanes.csv, prices four buying options per
  lane and refuses to pick. The human chooses one.
- `vave-ideation` — HUMAN-LED. teardown_ideas + warranty_claims. Names the
  physical test, who owns it, and what breaks if it is wrong. A yes here books
  nothing until the test passes.

Not run in the demo:

- `commodity-watch` — commodity erosion; covered instantly by `cli.py --plan`
- `orchestrator` — routes free-text ideas to a lever
- `savings-ledger` — reconciles the ledger, checks double-counting

## The synthetic data (in `data/`)

- `part_master.csv` — 40 parts, ~$630M/yr, real part_ids, with unit cost,
  should-cost, volume, material, model fit, load-bearing and single-source flags
- `spend_cube.csv` — spend by supplier x category, with the should-cost gap
- `warranty_claims.csv` — warranty cost tied to each part
- `teardown_ideas.csv` — raw VAVE ideas from competitor teardowns
- `commodity_prices.csv` — steel/rubber/alloy price indices
- `freight_lanes.csv` — 6 ocean lanes, ~$18M/yr, with option rates per lane
- `category_rates.csv` — the CASE's own commercial and VAVE % per category
- `indirect_opportunities.csv` — the ~$100M of indirect spend and its levers
- `savings_ledger.csv` — booked savings (starts empty by design)

The agents READ these files and COMPUTE real results (should-cost gaps,
commonization pairs, VAVE rankings, commodity erosion) — nothing is hardcoded.

The category spends and the commercial/VAVE rates are the case's own figures;
the part-level rows under them are synthetic. Say "synthetic, modelled on the
case data" once, near the start.

## Rules while recording

- Run the commands EXACTLY as written below. Do not invent flags or numbers.
- Before each command, say one sentence about what it will show.
- After each command, read the key number off the screen out loud (e.g. the
  should-cost gap an agent computed, "6 of 8 opportunities signed").
- ONLY these four agents run, in this order, and no others:
  `should-cost-analytics`, `parts-commonization`, `freight-lane`,
  `vave-ideation`. Never run `commodity-watch`, `orchestrator`,
  `savings-ledger`, `--all-agents`, `--run`, or anything not in the RUN
  SEQUENCE below.
- EVERY item gets a human decision. Two items per agent, asked one at a time,
  eight in total. You never approve, choose, or skip on the human's behalf.
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
Say: "Terravik's addressable base is about $730M a year — $630M of direct
materials plus roughly $100M of indirect — and the board wants 5 to 7% of it,
about $36.5M a year. Everything here runs on that real data: a part master, a
spend cube, warranty claims, teardown ideas. The agents read these files and
compute their own answers. Nothing is hardcoded."
Run (the reset empties the ledger and clears any decisions from a previous
take, so the demo starts from a clean slate):
```
python cli.py --reset-demo
python cli.py --data
```
Then read out: 40 parts covering the $630M of direct materials, and the files.

Always frame the base as **$730M**, and $630M as the direct-materials slice of
it. The $36.5M target is 5% of $730M. If you call $630M "the base" and a judge
divides, they get 5.8% and think your maths is off.

### Step 1 — Show the agents thinking for real, one at a time
Say: "These aren't hard-coded. Here are the real agents running live on Claude
Code — no API key, this is my Claude subscription. Each one reads the data in
data/ and produces its own finding, and each one needs a human signature
before it counts."

Go through these FOUR agents, ONE AT A TIME, in this order. They are one per
trust tier, and THE POINT OF THE DEMO IS THAT EACH TIER ASKS A DIFFERENT
QUESTION. Say the tier out loud before each agent.

```
should-cost-analytics    SUPER AGENT   -> straight yes/no
parts-commonization      SUPER AGENT   -> straight yes/no
freight-lane             UTILITY       -> options, the human picks one
vave-ideation            HUMAN-LED     -> needs a test and an owner
```

Do NOT run `commodity-watch`, `orchestrator` or `savings-ledger` in the demo.
Commodity erosion is covered instantly by `cli.py --plan` in Step 3.

For EACH agent, do these three things in order, then move to the next agent:

**1. Run it.** Each takes 15-90s; allow up to 10 minutes and never cancel one
that is still running. While it thinks, say "this is a real Claude agent
running right now."
```
python cli.py --agent <name>
```

**2. Talk through what it found — the WHOLE list, not one line.** Each agent
prints its complete opportunity table: every part with a should-cost gap,
every feasible VAVE idea, every commonization pair. Cover:
  - the TOTAL the agent computed, and what share of spend or target that is
  - the top 2-3 named items with their part ids and dollar figures
  - how many items there are in total, and how many are load-bearing
Never read a number the screen did not print. The output ends with "Awaiting
human sign-off", because the finding counts for nothing until a person signs
it.

**3. Take the TWO items in the agent's closing section, ONE AT A TIME.** Every
agent ends with exactly two. Always state the id, where the numbers came from,
the arithmetic, and the dollar figure before you ask. Never bundle the two into
one question. HOW you ask depends on the tier:

**SUPER AGENT — `should-cost-analytics`, `parts-commonization`.** Section is
`FOR DECISION`. Say it, then ask a straight yes/no:
> "The first one is part F-3001, a forging. From part_master.csv — unit cost
> 1,240 against a should-cost of 1,216 across 49,470 units a year. That's
> $1.87M a year, and it IS load-bearing."

AskUserQuestion, "Yes, book it" / "No, skip it" — "Should we proceed with
F-3001, $1.87M/yr?". Then:
```
python cli.py --sign <agent> y --saving <$M/yr> --part <ID> --label "<short name>"
python cli.py --sign <agent> n --part <ID> --label "<short name>"
```

**UTILITY — `freight-lane`.** Section is `FOR CHOICE`. The agent does NOT pick;
it prices four options per lane. Read all four out with their trade-offs, then
let the human choose:
> "Lane L-01, Chennai to Rotterdam, $5.2M a year, bought on spot. Four options:
> a fixed contract saves $0.47M but locks the rate; index-linked saves $0.31M
> and shares the risk; consolidating and slow-steaming saves $0.21M but adds
> transit days; staying on spot saves nothing and keeps flexibility. On-time is
> only 82% on this lane."

AskUserQuestion with the FOUR options as the choices. Then record which one:
```
python cli.py --sign freight-lane y --saving <$M/yr> --part <LANE_ID> \
  --label "<origin-destination>" --option "<the option they chose>"
```
If they pick "stay on spot", that is a real answer: record it with
`--sign freight-lane n --part <LANE_ID> --label "..."`.

**HUMAN-LED — `vave-ideation`.** Section is `FOR ENGINEERING JUDGEMENT`. This
is the tier the field failure created, so lead with the risk and the test, not
the saving:
> "Idea V-014 on casting C-2004 — remove two ribs, $1.1M a year. But it is
> load-bearing, and this is exactly the class of change that failed in the
> field. Before it moves it needs a fatigue test to the part's rated load
> cycles, about six weeks, owned by a structural engineer. If it's wrong, the
> part fails under load in the field."

AskUserQuestion, "Yes — send it for testing" / "No — don't pursue it". A yes
here does NOT book a saving; it enters the ledger as Pending validation and
earns nothing until the test passes. Record it WITH the test and the owner:
```
python cli.py --sign vave-ideation y --saving <$M/yr> --part <ID> \
  --label "<short name>" --test "<the named test and how long>" --owner "<who signs>"
```
Never omit `--test` on this tier — the tool will call it out, and rightly.

After each decision read out what the screen says: the booking id, and the
booked run-rate. Point out explicitly when a human-led item does NOT move the
run-rate: "that's approved, but it earns nothing until the test comes back."
On a rejection say "that one does not enter the ledger."

**4. ASK whether to move on to the next agent, and WAIT.** Use AskUserQuestion
with "Next agent" and "Hold here" — e.g. "Move on to parts-commonization?".
This lets them talk over a finding before the next agent starts. After the
LAST agent (`vave-ideation`) skip this and go to Step 2.

Every item faces a human. None is exempt, and nothing enters the ledger except
what the human approved. That is 4 agents x 2 items = 8 decisions, plus 3
"move on?" questions. Do not shorten it, do not batch it, and do not answer
any of it yourself.

Each agent reads data/part_master.csv (and its own file) — so if one ever says
the data is missing, the data/ folder wasn't shipped; check it's present.

### Step 2 — Close
Show what the human actually approved, and the ledger it built:
```
python cli.py --signoff-record
```
Read off the screen: "N/8 opportunities carry a human signature", then the
ledger total and what percent of the $36.5M target it is.

Say: "Four agents, one per trust tier. The Super Agents asked me yes or no.
The Utility agent refused to choose and made me pick. The Human-led one would
not book a dollar until an engineer tests it. Same data, three different levels
of trust — and nothing in that ledger that a human didn't sign. That's
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
