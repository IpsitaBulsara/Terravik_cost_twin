#!/usr/bin/env python3
"""
cli.py  -  terminal face of the Terravik Cost Twin (Intent-Driven Savings roadmap).

Same core.py as the Streamlit app. No API key; live mode uses Claude Code.

Usage:
    python cli.py                 # interactive menu
    python cli.py --run           # run once (simulated) and exit
    python cli.py --run --live    # ...calling real Claude Code agents
    python cli.py --run --ready   # pre-mark all Phase-1 foundations ready
    python cli.py --agent commodity-watch
"""
import argparse
import sys
import core

# Live agent output contains arrows, box-drawing and currency glyphs. On a
# console whose default encoding is cp1252 (Windows) printing those raises
# UnicodeEncodeError mid-table, so force UTF-8 and degrade unmappable
# characters instead of crashing the demo.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass


class C:
    P = "\033[95m"; B = "\033[94m"; G = "\033[92m"; Y = "\033[93m"
    R = "\033[91m"; BOLD = "\033[1m"; DIM = "\033[2m"; END = "\033[0m"


def banner():
    print(f"{C.P}{C.BOLD}")
    print("  ================================================")
    print("   TERRAVIK COST TWIN  -  Intent-Driven Savings")
    print("  ================================================")
    print(f"{C.END}{C.DIM}  Accenture B-School Challenge  |  Team Fourmula One{C.END}")
    ok = core.claude_available()
    print(f"  Claude Code (live agents): {(C.G if ok else C.Y)}{'available' if ok else 'NOT found on PATH'}{C.END}\n")


def show_readiness(state):
    print(f"{C.BOLD}Phase 1  -  Foundations (readiness gate){C.END}")
    for k, (label, feeds, fname) in core.DATA_FOUNDATION.items():
        mark = f"{C.G}[x]{C.END}" if state.foundation[k] else f"{C.R}[ ]{C.END}"
        n = len(core.load_foundation_rows(k))
        data = f"{C.DIM}({fname}, {n} rows){C.END}" if core.foundation_data_exists(k) else f"{C.R}(no data file){C.END}"
        print(f"  {mark} {label}  {C.DIM}{feeds}{C.END}  {data}")
    coe = f"{C.G}[x]{C.END}" if state.coe_ready else f"{C.R}[ ]{C.END}"
    bench = f"{C.G}[x]{C.END}" if state.bench_ready else f"{C.R}[ ]{C.END}"
    print(f"  {coe} Should-Cost CoE stood up (can COMPUTE)")
    print(f"  {bench} Validation bench stood up (can SIGN)")
    gate = C.G + "OPEN - levers may run" if state.can_compute and state.can_sign else C.R + "CLOSED - cannot save yet"
    print(f"  Gate: {gate}{C.END}\n")


def setup_foundations(state):
    """Interactively stand up Phase 1 pieces."""
    keys = list(core.DATA_FOUNDATION) + ["coe", "bench"]
    while True:
        show_readiness(state)
        print("  Toggle: 1-4 data pieces, 5 CoE, 6 bench, a=all, b=back")
        raw = input("  > ").strip().lower()
        if raw == "b":
            return
        if raw == "a":
            for k in state.foundation:
                state.foundation[k] = True
            state.coe_ready = True
            state.bench_ready = True
            continue
        m = {"1": 0, "2": 1, "3": 2, "4": 3}
        if raw in m:
            k = list(core.DATA_FOUNDATION)[m[raw]]
            state.foundation[k] = not state.foundation[k]
        elif raw == "5":
            state.coe_ready = not state.coe_ready
        elif raw == "6":
            state.bench_ready = not state.bench_ready


def trust_colour(trust):
    return {core.Trust.SUPER_AGENT: C.P, core.Trust.UTILITY: C.B, core.Trust.HUMAN_LED: C.Y}[trust]


def print_steps(steps):
    for s in steps:
        print(f"{C.P}{C.BOLD}{s.name}{C.END}")
        print(f"  {s.detail}")
        if s.live_output:
            print(f"{C.DIM}  --- live Claude Code response ---{C.END}")
            for line in s.live_output.splitlines():
                print(f"{C.DIM}  {line}{C.END}")
        print()


def show_state(state):
    print(f"{C.BOLD}Booked (signed){C.END}")
    for b in state.booked:
        tag = f"{C.B}[submitted]{C.END} " if b.source == "Submitted" else ""
        print(f"  {tag}{trust_colour(b.trust)}{b.trust.value:<12}{C.END} {b.lever_name:<26} {C.BOLD}${b.saving}M/yr{C.END}")
    if not state.booked:
        print("  (none)")
    print(f"\n{C.BOLD}Awaiting human sign-off{C.END}")
    for b in state.pending:
        tag = f"{C.B}[submitted]{C.END} " if b.source == "Submitted" else ""
        print(f"  {tag}{trust_colour(b.trust)}{b.trust.value:<12}{C.END} {b.lever_name:<26} {C.BOLD}${b.saving}M/yr{C.END}  {C.DIM}{b.note}{C.END}")
    if not state.pending:
        print("  (none)")
    print(f"\n{C.BOLD}Blocked by the readiness gate{C.END}")
    for b in state.blocked:
        print(f"  {C.R}{b.lever_name:<26}{C.END} {C.DIM}{b.note}{C.END}")
    if not state.blocked:
        print("  (none)")
    print(f"\n  {C.G}{C.BOLD}Booked: ${state.booked_total}M/yr ({state.pct_of_target}% of ${core.TARGET_ANNUAL_SAVING}M){C.END}")
    print(f"  {C.Y}Awaiting sign-off: ${state.pending_total}M/yr{C.END}\n")


def submit_idea_flow(state):
    """Classify a free-text idea (Tier 1 Orchestrator) and route it into the ledger/queue."""
    print(f"{C.BOLD}Submit an idea  -  the Orchestrator will route it to a lever{C.END}")
    desc = input("  Describe the idea: ").strip()
    if not desc:
        print(f"{C.Y}Nothing entered.{C.END}\n"); return
    saving_raw = input("  Estimated saving, $M/yr [0.5]: ").strip()
    try:
        saving = float(saving_raw) if saving_raw else 0.5
    except ValueError:
        saving = 0.5

    live = st_live = core.claude_available()
    if live:
        use_live = input("  Use the live orchestrator agent to classify? [y/N] ").strip().lower() == "y"
    else:
        use_live = False
        print(f"{C.DIM}  (Claude Code not found  -  using the offline keyword classifier){C.END}")

    print(f"{C.DIM}  Classifying...{C.END}")
    lever_id, load_bearing, why, raw = core.classify_idea(desc, live=use_live)
    lever = core.lever_by_id(lever_id)
    print(f"\n  Routed to: {C.BOLD}{lever.name}{C.END} ({lever.trust.value})")
    print(f"  Load-bearing: {C.R + 'yes' if load_bearing else C.G + 'no'}{C.END}")
    print(f"  {C.DIM}{why}{C.END}")
    if raw:
        print(f"{C.DIM}  --- live orchestrator response ---\n  {raw}{C.END}")

    ans = input(f"\n  Submit under {lever.name}? [Y/n] ").strip().lower()
    if ans == "n":
        print(f"{C.Y}Cancelled.{C.END}\n"); return
    override = input(f"  Override load-bearing flag? [y/n/enter to keep '{load_bearing}']: ").strip().lower()
    if override == "y":
        load_bearing = True
    elif override == "n":
        load_bearing = False

    bid, outcome = core.submit_idea(state, lever_id, desc, saving, load_bearing=load_bearing)
    colour = {"booked": C.G, "pending": C.Y, "blocked": C.R, "skipped": C.DIM}[outcome]
    print(f"\n  {colour}{C.BOLD}{outcome.upper()}{C.END}  ({bid})\n")


def sign_loop(state):
    if not state.pending:
        print(f"{C.Y}Nothing waiting for sign-off.{C.END}\n")
        return
    print(f"{C.BOLD}Human sign-off  -  green = sign-off, every tier.{C.END}\n")
    for b in list(state.pending):
        print(f"  {C.BOLD}{b.lever_name}{C.END} ({b.trust.value})  ${b.saving}M/yr")
        ans = input("  Sign off? [y/N] ").strip().lower()
        state.sign_off(b.id, ans == "y")
        print(f"  -> {(C.G+'booked' if ans=='y' else C.R+'rejected')}{C.END}\n")
    show_state(state)


AGENT_PROMPTS = core.AGENT_PROMPTS


SIGNOFF_LOG = core._os.path.join(core._os.path.dirname(core._os.path.abspath(__file__)),
                                 "signoff_log.csv")


LEDGER = core.foundation_file("savings_ledger")
LEDGER_HEADER = ["booking_id", "lever", "trust_type", "part_id",
                 "saving_usd_yr", "status", "approved_by", "booked_date"]

# Which of the 10 levers a signed finding from each agent books under.
AGENT_LEVER = {
    "commodity-watch": "should_cost",
    "should-cost-analytics": "should_cost",
    "vave-ideation": "subtier_teardown",
    "parts-commonization": "commonization",
    "orchestrator": "should_cost",
    "savings-ledger": "should_cost",
}


def book_to_ledger(agent_name, saving_musd, part_id="-"):
    """Append a human-approved finding to the cost ledger."""
    import csv, datetime
    lever = core.lever_by_id(AGENT_LEVER.get(agent_name, "should_cost"))
    rows = ledger_rows()
    booking_id = f"BK-{len(rows) + 1:03d}"
    if not core._os.path.exists(LEDGER) or not rows:
        with open(LEDGER, "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(LEDGER_HEADER)
    with open(LEDGER, "a", encoding="utf-8", newline="") as f:
        csv.writer(f).writerow([
            booking_id, lever.name, lever.trust.value, part_id,
            int(round(saving_musd * 1_000_000)), "Booked",
            f"human sign-off ({agent_name})",
            datetime.date.today().isoformat(),
        ])
    return booking_id


def ledger_rows():
    import csv
    if not core._os.path.exists(LEDGER):
        return []
    with open(LEDGER, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def show_ledger():
    rows = ledger_rows()
    print(f"{C.BOLD}Cost ledger  -  human-approved savings only{C.END}")
    if not rows:
        print(f"  {C.Y}(empty  -  nothing has been signed into it yet){C.END}\n")
        return
    for r in rows:
        musd = float(r["saving_usd_yr"]) / 1_000_000
        print(f"  {C.G}{r['booking_id']}{C.END}  {r['lever']:<22} {C.BOLD}${musd:.1f}M/yr{C.END}"
              f"  {C.DIM}{r['approved_by']}{C.END}")
    total = sum(float(r["saving_usd_yr"]) for r in rows) / 1_000_000
    pct = round(total / core.TARGET_ANNUAL_SAVING * 100)
    print(f"\n  {C.G}{C.BOLD}Booked: ${total:.1f}M/yr{C.END} "
          f"({pct}% of ${core.TARGET_ANNUAL_SAVING}M target)\n")


def record_sign_off(agent_name, approved, saving_musd=0.0):
    """
    Record a human's decision on a live agent finding. Approved findings go
    into the cost ledger; rejected ones go nowhere. Kept in files so the
    decision survives between the separate commands that run and sign it.
    """
    import csv
    new = not core._os.path.exists(SIGNOFF_LOG)
    with open(SIGNOFF_LOG, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if new:
            w.writerow(["agent", "decision", "saving_musd"])
        w.writerow([agent_name, "signed" if approved else "rejected",
                    saving_musd if approved else 0.0])

    if approved:
        print(f"\n  {C.G}{C.BOLD}APPROVED{C.END}  {agent_name}'s finding, signed by a human.")
        if saving_musd > 0:
            bid = book_to_ledger(agent_name, saving_musd)
            print(f"  -> booked into the cost ledger as {C.BOLD}{bid}{C.END}, "
                  f"{C.G}{C.BOLD}${saving_musd:.1f}M/yr{C.END}")
            total = sum(float(r["saving_usd_yr"]) for r in ledger_rows()) / 1_000_000
            print(f"  {C.DIM}ledger now stands at ${total:.1f}M/yr of "
                  f"${core.TARGET_ANNUAL_SAVING}M{C.END}\n")
        else:
            print(f"  {C.DIM}no dollar figure attached, so nothing was booked{C.END}\n")
    else:
        print(f"\n  {C.R}{C.BOLD}REJECTED{C.END}  {agent_name}'s finding.")
        print(f"  {C.DIM}not booked  -  it does not enter the cost ledger{C.END}\n")


def show_signoff_record():
    import csv
    if not core._os.path.exists(SIGNOFF_LOG):
        print(f"{C.Y}No sign-offs recorded yet.{C.END}\n")
        return
    with open(SIGNOFF_LOG, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    print(f"{C.BOLD}Human sign-off record{C.END}")
    for r in rows:
        ok = r["decision"] == "signed"
        print(f"  {(C.G + '[x] signed  ' if ok else C.R + '[ ] rejected')}{C.END} {r['agent']}")
    n = sum(1 for r in rows if r["decision"] == "signed")
    print(f"\n  {C.BOLD}{n}/{len(rows)}{C.END} agent findings carry a human signature.")
    print(f"  {C.DIM}Nothing books without one  -  green = sign-off, every tier.{C.END}\n")


def prompt_sign_off(agent_name):
    """
    The trust rule applied to a live agent finding. No agent is exempt.

    Reads the answer from stdin, so this works both when a human types it and
    when the decisions are piped in for a scripted run. With no answer at all
    available it fails closed: unsigned, never auto-approved.
    """
    try:
        ans = input(f"  Sign off on {agent_name}'s finding? [y/N] ").strip().lower()
    except EOFError:
        print(f"\n  {C.Y}No signature given  -  {agent_name}'s finding stays unsigned.{C.END}\n")
        return False
    if not sys.stdin.isatty():
        print(ans)  # echo the piped answer so the decision is visible on screen
    ok = ans == "y"
    print(f"  -> {(C.G + 'signed off' if ok else C.R + 'rejected')}{C.END}\n")
    return ok


def call_all_agents():
    print(f"{C.BOLD}Agent-by-agent demo  -  each subagent runs live, one at a time{C.END}")
    print(f"{C.DIM}  Green = sign-off, every tier: no agent's finding carries forward "
          f"without a human signature.{C.END}\n")
    signed = []

    def announce(name):
        print(f"{C.P}{C.BOLD}=== {name} ==={C.END}")
        print(f"{C.DIM}  running (15-90s)...{C.END}")

    def show(result):
        print(result.output if result.ok else f"{C.R}{result.output}{C.END}")
        print()
        # Every agent faces the same gate  -  Super Agent, Utility or Human-led.
        signed.append((result.name, prompt_sign_off(result.name)))

    core.run_all_agents(on_start=announce, on_done=show)

    print(f"{C.BOLD}Sign-off record{C.END}")
    for name, ok in signed:
        print(f"  {(C.G + '[x] signed  ' if ok else C.R + '[ ] rejected')}{C.END} {name}")
    print(f"\n  {len([1 for _, ok in signed if ok])}/{len(signed)} agent findings carry "
          f"a human signature.\n")


def call_one_agent():
    names = list(AGENT_PROMPTS)
    for i, n in enumerate(names, 1):
        print(f"  {i}  {n}")
    raw = input("  Pick (number or name): ").strip()
    name = names[int(raw)-1] if raw.isdigit() and 1 <= int(raw) <= len(names) else raw
    if name not in AGENT_PROMPTS:
        print(f"{C.Y}Unknown agent.{C.END}\n"); return
    prompt, web = AGENT_PROMPTS[name]
    print(f"{C.DIM}  Calling {name}... 15-90s{C.END}")
    ok, out = core.call_agent(prompt, needs_web=web)
    print("\n" + (out if ok else f"{C.R}{out}{C.END}") + "\n")
    if ok:
        prompt_sign_off(name)


def interactive(state):
    banner()
    menu = f"""{C.BOLD}Menu{C.END}
  1  Set up Phase 1 foundations (readiness gate)
  2  Run the roadmap pipeline (simulated)
  3  Run the roadmap pipeline (live Claude Code)
  4  Submit an idea (Orchestrator routes it to a lever)
  5  Human sign-off queue
  6  Show full state (booked / pending / blocked)
  7  Call one agent directly (live)
  8  Reset
  9  Run every agent, one by one (live demo)
  q  Quit
"""
    while True:
        print(menu)
        c = input("  > ").strip().lower()
        print()
        if c == "1":
            setup_foundations(state)
        elif c == "2":
            print_steps(core.run_pipeline(state, live=False, on_step=lambda m: print(f"{C.DIM}  {m}{C.END}")))
            show_state(state)
        elif c == "3":
            if not core.claude_available():
                print(f"{C.Y}Claude Code not found.{C.END}\n"); continue
            print_steps(core.run_pipeline(state, live=True, on_step=lambda m: print(f"{C.DIM}  {m}{C.END}")))
            show_state(state)
        elif c == "4":
            submit_idea_flow(state)
        elif c == "5":
            sign_loop(state)
        elif c == "6":
            show_state(state)
        elif c == "7":
            call_one_agent()
        elif c == "8":
            state.__dict__.update(core.RoadmapState().__dict__)
            print(f"{C.G}Reset.{C.END}\n")
        elif c == "9":
            if not core.claude_available():
                print(f"{C.Y}Claude Code not found.{C.END}\n"); continue
            call_all_agents()
        elif c == "q":
            print("Bye!\n"); return
        else:
            print(f"{C.Y}?{C.END}\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--live", action="store_true")
    ap.add_argument("--ready", action="store_true", help="pre-mark all Phase-1 foundations ready")
    ap.add_argument("--agent", metavar="NAME")
    ap.add_argument("--all-agents", action="store_true", help="run every agent in sequence, printing each one's output")
    ap.add_argument("--data", action="store_true", help="show a summary of the synthetic data foundation")
    ap.add_argument("--sign", nargs=2, metavar=("AGENT", "Y_OR_N"),
                    help="record a human's decision on an agent's finding, e.g. --sign vave-ideation y")
    ap.add_argument("--saving", type=float, default=0.0, metavar="M",
                    help="$M/yr the approved finding is worth; booked into the ledger on a 'y'")
    ap.add_argument("--signoff-record", action="store_true", help="show every sign-off decision so far")
    ap.add_argument("--ledger", action="store_true", help="show the cost ledger of approved savings")
    ap.add_argument("--reset-demo", action="store_true", help="clear sign-offs and empty the ledger for a clean run")
    args = ap.parse_args()

    state = core.RoadmapState()

    if args.reset_demo:
        import csv
        if core._os.path.exists(SIGNOFF_LOG):
            core._os.remove(SIGNOFF_LOG)
        with open(LEDGER, "w", encoding="utf-8", newline="") as f:
            csv.writer(f).writerow(LEDGER_HEADER)
        print(f"{C.G}Clean slate  -  sign-offs cleared, cost ledger emptied.{C.END}\n")
        sys.exit(0)

    if args.ledger:
        show_ledger()
        sys.exit(0)

    if args.signoff_record:
        show_signoff_record()
        show_ledger()
        sys.exit(0)

    if args.sign:
        name, decision = args.sign[0], args.sign[1].strip().lower()
        if name not in AGENT_PROMPTS:
            print(f"Unknown agent. Options: {', '.join(AGENT_PROMPTS)}"); sys.exit(1)
        if decision not in ("y", "n", "yes", "no"):
            print(f"Answer must be y or n, got {args.sign[1]!r}"); sys.exit(1)
        record_sign_off(name, decision.startswith("y"), args.saving)
        sys.exit(0)

    if args.data:
        banner()
        import csv, os
        files = [
            ("part_master.csv", "parts across 6 categories, ~$630M/yr"),
            ("spend_cube.csv", "spend by supplier x category"),
            ("warranty_claims.csv", "warranty claim groups by part"),
            ("teardown_ideas.csv", "raw VAVE ideas from competitor teardowns"),
            ("commodity_prices.csv", "steel/rubber/alloy price indices"),
            ("savings_ledger.csv", "booked savings (starts empty)"),
        ]
        print(f"{C.BOLD}Synthetic data foundation (in data/){C.END}\n")
        for fname, desc in files:
            path = os.path.join(core.DATA_DIR, fname)
            n = 0
            if os.path.exists(path):
                with open(path, encoding="utf-8") as f:
                    n = max(sum(1 for _ in f) - 1, 0)
            print(f"  {C.G}{fname:22s}{C.END} {C.BOLD}{n:>4d} rows{C.END}  {C.DIM}{desc}{C.END}")
        print(f"\n{C.DIM}  The agents read these files and compute real results from them.{C.END}\n")
        sys.exit(0)

    if args.all_agents:
        banner()
        call_all_agents()
        sys.exit(0)

    if args.agent:
        if args.agent not in AGENT_PROMPTS:
            print(f"Unknown agent. Options: {', '.join(AGENT_PROMPTS)}"); sys.exit(1)
        prompt, web = AGENT_PROMPTS[args.agent]
        ok, out = core.call_agent(prompt, needs_web=web)
        print(out)
        if ok:
            print(f"\n  {C.Y}{C.BOLD}Awaiting human decision{C.END}  {C.DIM}-  nothing enters "
                  f"the cost ledger until a person approves it.{C.END}")
            print(f"  {C.DIM}Approve:  python cli.py --sign {args.agent} y --saving <$M/yr>{C.END}")
            print(f"  {C.DIM}Reject :  python cli.py --sign {args.agent} n{C.END}\n")
        sys.exit(0 if ok else 1)

    if args.run:
        banner()
        if args.ready:
            for k in state.foundation:
                state.foundation[k] = True
            state.coe_ready = True
            state.bench_ready = True
        show_readiness(state)
        print_steps(core.run_pipeline(state, live=args.live, on_step=lambda m: print(f"{C.DIM}  {m}{C.END}")))
        show_state(state)
        return

    interactive(state)


if __name__ == "__main__":
    main()
