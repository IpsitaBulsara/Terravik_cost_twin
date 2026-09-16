"""
core.py  -  shared brain for the Terravik Cost Twin, modelled on the
"Roadmap to Intent-Driven Savings" (from data -> to intent -> to proven value).

Both cli.py (terminal) and app.py (Streamlit) import this, so the model,
the trust tiers, the readiness gate, and the Claude Code bridge live once.

Roadmap structure:
  PHASE 1 - FOUNDATIONS (0-6 mo): data foundation + R&D redesign that must
    exist before ANY saving can be booked. This is the readiness gate.
  THE DECISION TREE (Phases 2-3):
    Tier 1 - Orchestrator: AI routes each idea; a human sets the mandate.
    Tier 2 - the 10 working levers, each with a TRUST TYPE:
      SUPER_AGENT  - AI owns the screen (Should-Cost, Tail-Spend,
                     Commonization, Sub-Tier teardown)
      UTILITY      - AI checks, a human signs (Specifications, Packaging,
                     Freight-Lane, Travel/office policy)
      HUMAN_LED    - AI assists only (Alternate/dual sourcing,
                     Process / design-to-value)
    Tier 3 - Shared tools: Should-cost recompute, Warranty screen,
             Double-count check.
  The rule, every tier: green = human sign-off. And: you cannot save until
  you can COMPUTE (CoE + data foundation) and SIGN (validation bench).

Agents run via Claude Code headless (claude -p ...) on a Claude Pro plan;
no API key. Subagents live in .claude/agents/.
"""

from __future__ import annotations
import os
import shutil
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Optional

TARGET_ANNUAL_SAVING = 36.5
ORIGINAL_TIMELINE_MONTHS = 24
NEW_TIMELINE_MONTHS = 18


class Trust(str, Enum):
    SUPER_AGENT = "Super Agent"
    UTILITY = "Utility"
    HUMAN_LED = "Human-led"


AUTONOMY = {
    Trust.SUPER_AGENT: "AI drafts and screens; bench-validated method",
    Trust.UTILITY: "AI checks; a human signs every recommendation",
    Trust.HUMAN_LED: "AI only assists; the human leads and decides",
}

DATA_FOUNDATION = {
    "part_master": ("Part master + live index", "feeds Should-Cost, Commonization", "part_master.csv"),
    "spend_cube": ("Spend cube", "feeds Tail-Spend", "spend_cube.csv"),
    "warranty_rekey": ("Warranty re-keyed to component", "feeds Warranty screen", "warranty_claims.csv"),
    "savings_ledger": ("Single savings ledger", "feeds Double-count check", "savings_ledger.csv"),
}

# where the synthetic foundation data lives, relative to this file
import os as _os
DATA_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "data")


def foundation_file(key: str) -> str:
    """Absolute path to the CSV backing a given foundation piece."""
    return _os.path.join(DATA_DIR, DATA_FOUNDATION[key][2])


def foundation_data_exists(key: str) -> bool:
    """True if the synthetic data file for this foundation is present."""
    return _os.path.exists(foundation_file(key))


def load_foundation_rows(key: str) -> list:
    """Read a foundation CSV into a list of dict rows (empty if missing)."""
    import csv
    path = foundation_file(key)
    if not _os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))

RND_REDESIGN = {
    "delayer": ("De-layer 5 to 3", None),
    "category_pods": ("Category pods", None),
    "absorb_coord": ("Absorb coordination", None),
}
ENGINEERS_FREED = 16
BENCH_ENGINEERS = 6


@dataclass
class Lever:
    id: str
    name: str
    trust: Trust
    phase: str
    needs: list
    est_saving: float
    agent: str


LEVERS = [
    Lever("should_cost", "Should-Cost", Trust.SUPER_AGENT, "P2", ["part_master"], 6.0, "should-cost-analytics"),
    Lever("tail_spend", "Tail-Spend", Trust.SUPER_AGENT, "P2", ["spend_cube"], 3.5, "should-cost-analytics"),
    Lever("commonization", "Commonization", Trust.SUPER_AGENT, "P2", ["part_master"], 2.4, "parts-commonization"),
    Lever("subtier_teardown", "Sub-Tier teardown", Trust.SUPER_AGENT, "P3", ["part_master"], 4.0, "vave-ideation"),
    Lever("specifications", "Specifications", Trust.UTILITY, "P2", ["part_master"], 2.0, "vave-ideation"),
    Lever("packaging", "Packaging", Trust.UTILITY, "P3", ["spend_cube"], 1.2, "should-cost-analytics"),
    Lever("freight_lane", "Freight - Lane", Trust.UTILITY, "P3", ["spend_cube"], 1.5, "should-cost-analytics"),
    Lever("travel_office", "Travel + office policy", Trust.UTILITY, "P2", ["spend_cube"], 0.8, "should-cost-analytics"),
    Lever("alt_sourcing", "Alternate, dual sourcing", Trust.HUMAN_LED, "P3", ["part_master", "spend_cube"], 5.0, "should-cost-analytics"),
    Lever("design_to_value", "Process, design-to-value", Trust.HUMAN_LED, "P3", ["part_master"], 6.0, "vave-ideation"),
]

SHARED_TOOLS = {
    "should_cost_recompute": ("Should-cost recompute", "reads the live index", "part_master"),
    "warranty_screen": ("Warranty screen", "reads warranty history", "warranty_rekey"),
    "double_count_check": ("Double-count check", "reads the savings ledger", "savings_ledger"),
}


def claude_available() -> bool:
    return shutil.which("claude") is not None


def call_agent(instruction, needs_web=False, timeout=150):
    if not claude_available():
        return False, ("Claude Code isn't installed or not on PATH. Install it and run "
                       "`claude -p \"say hi\"` from this folder before using live mode.")
    allowed = "WebSearch,WebFetch,Read,Write,Bash,Grep,Glob" if needs_web else "Read,Write,Bash,Grep,Glob"
    try:
        r = subprocess.run(
            ["claude", "-p", instruction, "--allowedTools", allowed],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout, cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        if r.returncode != 0:
            return False, f"Claude Code error:\n{(r.stderr or '').strip()}"
        return True, (r.stdout or "").strip()
    except subprocess.TimeoutExpired:
        return False, f"Claude Code timed out after {timeout}s."
    except Exception as e:
        return False, f"Couldn't run Claude Code: {e}"


# --- agent registry: prompts for calling each subagent directly, live ------
AGENT_PROMPTS = {
    "orchestrator": ("Use the orchestrator subagent to classify this idea: a hydraulic fitting shared across two loader models.", False),
    "commodity-watch": ("Use the commodity-watch subagent. Read data/commodity_prices.csv and data/part_master.csv, compute the price move and estimated dollar erosion per commodity, and show the numbers.", True),
    "should-cost-analytics": ("Use the should-cost-analytics subagent. Read data/part_master.csv and data/spend_cube.csv, compute the should-cost gap per part and aggregate by category and supplier, then show a ranked table of the top 5 opportunities with the dollar and percent gaps you computed.", False),
    "vave-ideation": ("Use the vave-ideation subagent. Read data/teardown_ideas.csv and data/warranty_claims.csv, keep the feasible ideas, rank them by saving, and show the top 5-6 as a table with saving, load-bearing flag, and warranty flag.", False),
    "parts-commonization": ("Use the parts-commonization subagent. Read data/part_master.csv, find real commonization candidate pairs within each category, score them, and show a ranked table with part ids, similarity, load-bearing flag, combined spend, and estimated saving.", False),
    "savings-ledger": ("Use the savings-ledger subagent. Read data/savings_ledger.csv, sum the booked savings, check for double-counting by part_id, and report the total against the $36.5M target.", False),
}

AGENT_ORDER = ["commodity-watch", "should-cost-analytics", "vave-ideation",
               "parts-commonization", "orchestrator", "savings-ledger"]


@dataclass
class AgentRunResult:
    name: str
    ok: bool
    output: str


def run_all_agents(order=None, on_start=None, on_done=None, timeout=150):
    """
    Call every subagent in `order` (default AGENT_ORDER) one at a time,
    live via Claude Code. Announces each agent before it runs (on_start)
    and hands back its output as soon as it finishes (on_done), so a caller
    (CLI or Streamlit) can reveal them one by one instead of waiting for
    the whole batch.
    """
    results = []
    for name in order or AGENT_ORDER:
        if on_start:
            on_start(name)
        prompt, needs_web = AGENT_PROMPTS[name]
        ok, out = call_agent(prompt, needs_web=needs_web, timeout=timeout)
        result = AgentRunResult(name, ok, out)
        results.append(result)
        if on_done:
            on_done(result)
    return results


@dataclass
class Booking:
    id: str            # unique identity for this booking (dedup key)
    lever_id: str       # which of the 10 levers it belongs to (category)
    lever_name: str
    trust: Trust
    saving: float
    status: str
    note: str = ""
    source: str = "Roadmap"   # "Roadmap" (the 10 fixed levers) or "Submitted"


@dataclass
class RoadmapState:
    foundation: dict = field(default_factory=lambda: {k: False for k in DATA_FOUNDATION})
    bench_ready: bool = False
    coe_ready: bool = False
    booked: list = field(default_factory=list)
    pending: list = field(default_factory=list)
    blocked: list = field(default_factory=list)
    submitted_count: int = 0

    @property
    def foundation_ready(self):
        return all(self.foundation.values())

    @property
    def can_compute(self):
        return self.coe_ready and self.foundation_ready

    @property
    def can_sign(self):
        return self.bench_ready

    def lever_ready(self, lever):
        missing = [DATA_FOUNDATION[k][0] for k in lever.needs if not self.foundation.get(k)]
        if missing:
            return False, "missing foundation: " + ", ".join(missing)
        if not self.coe_ready:
            return False, "Should-Cost CoE not stood up (cannot compute)"
        if not self.bench_ready:
            return False, "validation bench not ready (cannot sign)"
        return True, ""

    @property
    def booked_total(self):
        return round(sum(b.saving for b in self.booked), 1)

    @property
    def pending_total(self):
        return round(sum(b.saving for b in self.pending), 1)

    @property
    def pct_of_target(self):
        return round(self.booked_total / TARGET_ANNUAL_SAVING * 100)

    def sign_off(self, booking_id, approve):
        for i, b in enumerate(self.pending):
            if b.id == booking_id:
                if approve:
                    b.status = "Booked"
                    self.booked.append(b)
                else:
                    b.status = "Rejected"
                self.pending.pop(i)
                return


@dataclass
class StepResult:
    name: str
    detail: str
    live_output: Optional[str] = None


def _seen(state, booking_id):
    return any(b.id == booking_id for b in state.booked + state.pending + state.blocked)


def lever_by_id(lever_id):
    for l in LEVERS:
        if l.id == lever_id:
            return l
    return None


def _place(state, booking_id, lever, desc, saving, load_bearing, source="Roadmap"):
    """
    The one shared gate + trust rule, used for both the 10 fixed levers and
    any idea submitted later (e.g. from a live agent's output). Returns
    "booked" | "pending" | "blocked" | "skipped".
    """
    if _seen(state, booking_id):
        return "skipped"
    ready, reason = state.lever_ready(lever)
    if not ready:
        state.blocked.append(Booking(booking_id, lever.id, lever.name, lever.trust, saving,
                                     "Blocked - not ready", reason, source))
        return "blocked"
    # Green = sign-off, EVERY tier: nothing books on its own, not even a
    # Super Agent lever. Trust type still sets how much the AI did first, but
    # it never decides whether a human has to sign.
    note = desc or AUTONOMY[lever.trust]
    if load_bearing:
        note = (desc + "  -  " if desc else "") + "flagged load-bearing"
    state.pending.append(Booking(booking_id, lever.id, lever.name, lever.trust, saving,
                                 "Awaiting sign-off", note, source))
    return "pending"


def route_lever(state, lever):
    """Route one of the 10 fixed roadmap levers (called once per pipeline run)."""
    return _place(state, lever.id, lever, "", lever.est_saving, load_bearing=False, source="Roadmap")


def submit_idea(state, lever_id, description, saving, load_bearing=None):
    """
    Submit a new idea (e.g. a candidate from a live agent's output) into the
    pipeline under an existing lever. Reuses that lever's trust type and
    readiness requirements, but gets its own unique id so it never collides
    with  -  or gets skipped because of  -  the base lever's own run.

    load_bearing=None means "use the lever's own default risk posture"
    (False for everything except where the idea explicitly says otherwise).
    """
    lever = lever_by_id(lever_id)
    if lever is None:
        raise ValueError(f"Unknown lever_id: {lever_id}")
    state.submitted_count += 1
    booking_id = f"{lever_id}-SUB-{state.submitted_count}"
    lb = bool(load_bearing)
    outcome = _place(state, booking_id, lever, description, saving, load_bearing=lb, source="Submitted")
    return booking_id, outcome


# --- simple offline classifier (used when live mode is off) ----------------
# Ordered so the more specific / higher-signal categories are checked first.
# Multi-word phrases are matched as substrings (safe); single short words are
# matched on whole-word boundaries to avoid false hits like "spec" inside
# "thread spec" or "pin" inside "pinpoint".
_KEYWORDS = {
    "commonization": {
        "phrases": ["commoniz", "common part", "merge part", "shared part",
                    "share the same", "interchangeable", "same thread",
                    "across model", "across variant", "near-identical", "identical part"],
        "words": ["bracket", "hinge", "bolt", "pin", "fitting", "fastener", "clip"],
    },
    "should_cost": {
        "phrases": ["should-cost", "should cost", "cost model", "spend gap", "overpriced"],
        "words": [],
    },
    "tail_spend": {
        "phrases": ["tail spend", "tail-spend", "long tail", "fragmented spend", "fragmented tail"],
        "words": [],
    },
    "subtier_teardown": {
        "phrases": ["teardown", "sub-tier", "subtier", "tier-2 supplier", "competitor teardown"],
        "words": [],
    },
    "specifications": {
        "phrases": ["over-spec", "overspec", "specification", "tolerance band", "tight tolerance"],
        "words": ["tolerance"],
    },
    "packaging": {
        "phrases": ["packaging", "skid", "crate", "carton"],
        "words": [],
    },
    "freight_lane": {
        "phrases": ["freight", "shipping lane", "logistics lane", "ocean freight"],
        "words": ["lane"],
    },
    "travel_office": {
        "phrases": ["travel policy", "office consolidation", "booking tool"],
        "words": ["travel"],
    },
    "alt_sourcing": {
        "phrases": ["dual source", "dual-source", "alternate supplier", "second source", "resourcing"],
        "words": [],
    },
    "design_to_value": {
        "phrases": ["design-to-value", "design to value", "process redesign", "redesign the process"],
        "words": [],
    },
}


def classify_idea_offline(description: str):
    """Deterministic keyword fallback classifier  -  no Claude needed."""
    import re
    text = description.lower()
    for lever_id, spec in _KEYWORDS.items():
        for phrase in spec["phrases"]:
            if phrase in text:
                return lever_id, False, f"matched phrase '{phrase}' (offline classifier, no live agent)"
        for word in spec["words"]:
            if re.search(rf"\b{re.escape(word)}\b", text):
                return lever_id, False, f"matched word '{word}' (offline classifier, no live agent)"
    return "commonization", False, "no keyword match; defaulted to Commonization (offline classifier)"


def classify_idea(description: str, live: bool = False):
    """
    Tier 1 routing: classify a free-text idea to one of the 10 levers.
    Returns (lever_id, load_bearing, rationale, raw_agent_output_or_None).
    Live=True calls the real orchestrator subagent; otherwise uses the
    offline keyword classifier so this always works without Claude Code.
    """
    if not live:
        lever_id, lb, why = classify_idea_offline(description)
        return lever_id, lb, why, None

    ok, out = call_agent(
        "Use the orchestrator subagent to classify this idea. Reply in the "
        f"exact 3-line format it specifies.\n\nIdea: {description}",
        needs_web=False,
    )
    if not ok:
        lever_id, lb, why = classify_idea_offline(description)
        return lever_id, lb, f"(live orchestrator failed, used offline fallback: {why})", out

    lever_id, lb, why = None, False, ""
    for line in out.splitlines():
        low = line.strip().lower()
        if low.startswith("lever_id:"):
            lever_id = line.split(":", 1)[1].strip()
        elif low.startswith("load_bearing:"):
            lb = "yes" in line.split(":", 1)[1].strip().lower()
        elif low.startswith("rationale:"):
            why = line.split(":", 1)[1].strip()
    if lever_id is None or lever_by_id(lever_id) is None:
        # couldn't parse or invalid id -> fall back offline, but keep the raw output visible
        fb_id, fb_lb, fb_why = classify_idea_offline(description)
        return fb_id, fb_lb, f"(couldn't parse orchestrator output, used offline fallback: {fb_why})", out
    return lever_id, lb, why, out


def run_pipeline(state, live=False, on_step=None):
    def announce(m):
        if on_step:
            on_step(m)

    steps = []

    announce("Step 1/4  Foundations: checking data + CoE + bench readiness")
    missing = [DATA_FOUNDATION[k][0] for k, v in state.foundation.items() if not v]
    gate = []
    if missing:
        gate.append("data foundation incomplete: " + ", ".join(missing))
    if not state.coe_ready:
        gate.append("Should-Cost CoE not stood up (cannot compute)")
    if not state.bench_ready:
        gate.append("validation bench not ready (cannot sign)")
    detail = ("All foundations ready - levers may run." if not gate
              else "Readiness gate holding back savings: " + "; ".join(gate))
    steps.append(StepResult("1. Phase 1 - Foundations", detail))

    announce("Step 2/4  Orchestrator: routing the 10 levers by trust type")
    counts = {"booked": 0, "pending": 0, "blocked": 0, "skipped": 0}
    for lever in LEVERS:
        counts[route_lever(state, lever)] += 1
    step2 = StepResult(
        "2. Tier 1 - Orchestrator",
        f"{counts['pending']} lever(s) routed and awaiting human sign-off, "
        f"{counts['blocked']} lever(s) blocked by the readiness gate. "
        f"No lever books itself  -  not even a Super Agent.")
    if live:
        announce("Step 2/4  Orchestrator: calling live agent for a routing summary")
        lever_list = ", ".join(f"{l.name} ({l.trust.value})" for l in LEVERS)
        ok, out = call_agent(
            "Use the orchestrator subagent's judgement (not its 3-line format this "
            "time) to write one or two sentences summarizing, for a live audience, "
            f"how these 10 levers were just routed by trust type: {lever_list}. "
            f"{counts['booked']} booked automatically, {counts['pending']} sent for "
            f"human sign-off, {counts['blocked']} blocked by the Phase 1 readiness gate.",
            needs_web=False,
        )
        step2.live_output = out if ok else f"(live call failed: {out})"
    steps.append(step2)

    announce("Step 3/4  Sign-off: an engineer/category manager signs each rec")
    steps.append(StepResult(
        "3. Tier 2 - Human sign-off",
        f"${state.pending_total}M/yr of Utility + Human-led savings is waiting for a "
        f"human signature. Nothing books without it  -  green = sign-off, every tier."))

    announce("Step 4/4  Double-count check: reconciling the booked ledger")
    step4 = StepResult(
        "4. Tier 3 - Double-count check",
        f"Booked: ${state.booked_total}M/yr ({state.pct_of_target}% of target). "
        f"Awaiting sign-off: ${state.pending_total}M/yr.")
    if live:
        announce("Step 4/4  calling live savings-ledger agent to check double-counting")
        summary = "\n".join(f"- {b.lever_name} ({b.trust.value}): ${b.saving}M/yr" for b in state.booked) or "(none booked yet)"
        ok, out = call_agent(
            "Use the savings-ledger subagent to reconcile these booked savings and "
            f"check for double-counting:\n{summary}", needs_web=False)
        step4.live_output = out if ok else f"(live call failed: {out})"
    steps.append(step4)

    announce("Done.")
    return steps
