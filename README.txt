COST TWIN — Terravik Intent-Driven Savings agent
Team Fourmula One | Accenture B-School Challenge S10

One shared brain (core.py). Two faces: a terminal app and a Streamlit app.
Both run the same roadmap pipeline, so they can never drift apart.

──────────────────────────────────────────────────────────────
EASIEST DEMO — let Claude Code drive it (record this)
──────────────────────────────────────────────────────────────
  cd into this folder, then:   claude

  Claude Code reads CLAUDE.md automatically. Give it one instruction:

      Read CLAUDE.md and begin.

  It narrates each step, runs the commands itself, and reads the numbers
  off the screen — the readiness gate, the routing, a live agent. Every
  command is visible on screen; that is what you record. No API key.

  Test the steps first if you want:
      python cli.py --run
      python cli.py --run --ready

──────────────────────────────────────────────────────────────
TWO WAYS TO RUN BY HAND. Pick one (they share the same core).
──────────────────────────────────────────────────────────────

A. TERMINAL  —  no API key, uses your Claude subscription via Claude Code
──────────────────────────────────────────────────────────────
  cd into this folder, then:

      python cli.py                 interactive menu
      python cli.py --run           run once, gate closed (all levers blocked)
      python cli.py --run --ready    stand up foundations first, then run
      python cli.py --run --ready --live    ...calling real Claude Code agents
      python cli.py --agent orchestrator    call one agent directly

  Live mode calls Claude Code headless (claude -p ...) on your Claude Pro
  plan. No API key. Test it first if you want:

      claude -p "say hi"

B. STREAMLIT  —  the visual version for the stage
──────────────────────────────────────────────────────────────
  pip install -r requirements.txt
  streamlit run app.py

  Sidebar has the Live Claude toggle and a connection test. Tabs:
  Phase 1 Foundations, Run Roadmap, Submit an Idea, Sign-off Queue,
  Booked Ledger, Call an Agent.

──────────────────────────────────────────────────────────────
THE MODEL (from the Intent-Driven Savings roadmap)
──────────────────────────────────────────────────────────────
  PHASE 1 — Foundations (the readiness gate).
    You cannot book a saving until you can COMPUTE (Should-Cost CoE + data
    foundation: part master, spend cube, warranty re-key, savings ledger)
    and SIGN (validation bench). Until then every lever is blocked.

  THE DECISION TREE (Phases 2-3):
    Tier 1 — Orchestrator: routes each idea to the right lever.
    Tier 2 — the 10 working levers, each with a trust type:
        Super Agent  — AI owns the screen  (Should-Cost, Tail-Spend,
                       Commonization, Sub-Tier teardown) — auto-book.
        Utility      — AI checks, human signs  (Specifications, Packaging,
                       Freight-Lane, Travel/office).
        Human-led    — AI assists only  (Alternate/dual sourcing,
                       Process/design-to-value).
    Tier 3 — Shared tools: Should-cost recompute, Warranty screen,
             Double-count check.

  The rule, every tier: green = human sign-off. Nothing books without it.

──────────────────────────────────────────────────────────────
THE 6 AGENTS  (in .claude/agents/)
──────────────────────────────────────────────────────────────
  orchestrator            routes a free-text idea to one of the 10 levers
  commodity-watch         checks live steel/rubber/alloy prices, erosion
  should-cost-analytics    flags the biggest should-cost gaps
  vave-ideation           generates risk-tagged VAVE ideas
  parts-commonization     scores part-merge candidates
  savings-ledger          reconciles the ledger, checks double-counting

──────────────────────────────────────────────────────────────
FILES
──────────────────────────────────────────────────────────────
  core.py                 shared brain: model, gate, tiers, bridge, pipeline
  cli.py                  terminal entry point
  app.py                  streamlit entry point
  CLAUDE.md               demo driver — Claude Code reads this and runs it
  .claude/agents/*.md     the 6 Claude Code subagents
  data/                   synthetic foundation data the agents read:
                            part_master.csv    27 parts, ~$630M
                            spend_cube.csv     spend by supplier x category
                            warranty_rekey.csv warranty claims by part
                            savings_ledger.csv booked savings (starts empty)
  requirements.txt        streamlit + pandas
  DEMO_SCRIPT.md          scene-by-scene script for the demo video

──────────────────────────────────────────────────────────────
HONESTY CHECK — read this before you record
──────────────────────────────────────────────────────────────
  Everything runs in SIMULATED mode by default: the numbers are modelled
  on the case's own figures, not a live data feed. Say so in the first ten
  seconds of the recording.

  Live Claude mode calls real Claude Code agents on your machine — that is
  genuine, no API key, and the tool calls are visible on screen. It only
  works when Streamlit/terminal and Claude Code run on the SAME machine.

  The readiness gate is real: with the foundations off, the pipeline books
  $0 and every lever shows as blocked. That is the point, not a bug — do
  not "fix" it on camera by skipping Phase 1.
