"""
case_model.py  -  the economics of the Grand Finale twist.

The Campus-round plan assumed commercial negotiation plus VAVE would carry the
~$36.5M/yr. The twist breaks that plan in three places, and this module
recomputes what is actually achievable against each one:

  Pressure 1  Commodity shock  -  steel/rubber/alloy indices jump, so the
              negotiated commercial saving is wiped out by raw-material cost.
  Pressure 2  Trust shock  -  an AI-proposed VAVE change on a LOAD-BEARING
              part failed in the field, so engineering now signs every idea.
              That makes the validation bench, not the idea pool, the limit.
  Pressure 3  Deadline shock  -  the full number is due in 18 months, not 24,
              with transformation spend capped.

Every figure here is computed from the case's own tables in data/
(category_rates.csv, indirect_opportunities.csv, part_master.csv). Anything
that is an assumption rather than a case figure is listed in ASSUMPTIONS and
printed with the results, so it can be challenged directly.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, field

import core

DATA = core.DATA_DIR

# --- assumptions, stated so they can be argued with -------------------------
ASSUMPTIONS = {
    "material_share": "share of a part's cost that is raw material, per category "
                      "(drives how much of a commodity move reaches part cost)",
    "ideas_per_engineer_month": "validation throughput per bench engineer, per month",
    "implementation_lag_months": "validated idea -> implemented -> earning run-rate",
    "feasible_idea_pool": "case says 25+ teardowns and 150+ workshops yield thousands "
                          "of ideas but only a few hundred truly feasible",
    "ai_triage_multiplier": "how much AI pre-screening lifts engineer throughput when "
                            "the engineer still signs every idea",
}

IDEAS_PER_ENGINEER_MONTH = 2.0
IMPLEMENTATION_LAG_MONTHS = 3
FEASIBLE_IDEA_POOL = 300
AI_TRIAGE_MULTIPLIER = 2.0
# A non-load-bearing idea still gets signed, but it needs a desk check rather
# than the full fatigue/qualification bench that broke the last change.
FAST_LANE_MULTIPLIER = 3.0


def _rows(name):
    path = os.path.join(DATA, name)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def categories():
    out = []
    for r in _rows("category_rates.csv"):
        out.append({
            "category": r["category"],
            "spend": float(r["annual_spend_usd"]),
            "commercial_mid": (float(r["commercial_lo"]) + float(r["commercial_hi"])) / 2,
            "vave_lo": float(r["vave_lo"]),
            "vave_hi": float(r["vave_hi"]),
            "vave_mid": (float(r["vave_lo"]) + float(r["vave_hi"])) / 2,
            "commodity": r["commodity"],
            "material_share": float(r["material_share"]),
            "risk": r["main_risk"],
        })
    return out


def commodity_moves():
    """Index move per commodity, as a fraction (e.g. 0.34 for 100 -> 134)."""
    moves = {}
    for r in _rows("commodity_prices.csv"):
        moves[r["commodity"]] = (float(r["current_index"]) - float(r["baseline_index"])) / 100
    return moves


def load_bearing_share():
    """Share of each category's spend sitting on load-bearing parts."""
    tot, lb = {}, {}
    for r in core.load_foundation_rows("part_master"):
        c, s = r["category"], float(r["annual_spend_usd"])
        tot[c] = tot.get(c, 0) + s
        if r["load_bearing"].strip().lower() == "true":
            lb[c] = lb.get(c, 0) + s
    return {c: (lb.get(c, 0) / t if t else 0) for c, t in tot.items()}


# --- Pressure 1: what the commodity shock does to commercial ----------------
@dataclass
class CommercialResult:
    rows: list = field(default_factory=list)
    planned: float = 0.0
    surviving: float = 0.0

    @property
    def evaporated(self):
        return self.planned - self.surviving


def commercial_after_shock():
    """
    A commodity index move raises part cost by (move x material_share). Where
    that increase exceeds the negotiated commercial saving, the saving is gone
    -- this is the case's "the number on paper no longer holds".
    """
    moves = commodity_moves()
    res = CommercialResult()
    for c in categories():
        planned = c["spend"] * c["commercial_mid"]
        move = moves.get(c["commodity"], 0.0)
        cost_up_pct = move * c["material_share"]
        cost_up = c["spend"] * cost_up_pct
        surviving = max(0.0, planned - cost_up)
        res.rows.append({**c, "planned": planned, "cost_up_pct": cost_up_pct,
                         "cost_up": cost_up, "surviving": surviving})
        res.planned += planned
        res.surviving += surviving
    return res


# --- Pressure 2 + 3: what the bench can actually validate in 18 months ------
@dataclass
class VaveResult:
    potential: float
    achievable: float
    ideas_needed: int
    ideas_possible: int
    avg_saving_per_idea: float
    binding: str


def vave_potential(aggressive=False):
    """
    Midpoint of the case's VAVE range per category, or the top of it. The top
    of the range means the deepest design changes -- material substitution and
    weight reduction on structural parts -- which is precisely the change that
    failed in the field.
    """
    key = "vave_hi" if aggressive else "vave_mid"
    return sum(c["spend"] * c[key] for c in categories())


def vave_achievable(bench_engineers=core.BENCH_ENGINEERS,
                    months=core.NEW_TIMELINE_MONTHS,
                    ai_triage=False, fast_lane=False, aggressive=False):
    """
    Post-failure, every idea needs an engineering signature, so the bench is
    the constraint -- not the idea pool. Only ideas validated early enough to
    be implemented are earning run-rate by the deadline.
    """
    potential = vave_potential(aggressive)
    avg = potential / FEASIBLE_IDEA_POOL

    rate = IDEAS_PER_ENGINEER_MONTH
    if ai_triage:
        rate *= AI_TRIAGE_MULTIPLIER
    validating_months = max(0, months - IMPLEMENTATION_LAG_MONTHS)
    ideas = bench_engineers * rate * validating_months

    if fast_lane:
        # Non-load-bearing spend gets a desk check rather than the full bench,
        # so those ideas clear far faster. Weight by where the spend actually is.
        lb = load_bearing_share()
        cats = categories()
        total = sum(c["spend"] for c in cats)
        non_lb_weight = sum(c["spend"] * (1 - lb.get(c["category"], 1.0)) for c in cats) / total
        ideas *= (1 - non_lb_weight) + non_lb_weight * FAST_LANE_MULTIPLIER

    ideas = min(ideas, FEASIBLE_IDEA_POOL)
    achievable = min(potential, ideas * avg)
    binding = "idea pool (bench has spare capacity)" if ideas >= FEASIBLE_IDEA_POOL \
        else "validation bench throughput"
    return VaveResult(potential, achievable, FEASIBLE_IDEA_POOL, int(ideas), avg, binding)


# --- indirect: fast, and it does not queue behind the bench -----------------
def indirect_achievable():
    rows = _rows("indirect_opportunities.csv")
    lo = sum(float(r["opportunity_lo_usd"]) for r in rows)
    hi = sum(float(r["opportunity_hi_usd"]) for r in rows)
    return (lo + hi) / 2, rows


# --- scenarios --------------------------------------------------------------
@dataclass
class Scenario:
    name: str
    note: str
    commercial: float
    vave: float
    indirect: float
    vave_detail: VaveResult
    integrity_risk: str = ""

    @property
    def total(self):
        return self.commercial + self.vave + self.indirect

    @property
    def pct_of_target(self):
        return self.total / (core.TARGET_ANNUAL_SAVING * 1e6) * 100

    @property
    def gap(self):
        return core.TARGET_ANNUAL_SAVING * 1e6 - self.total


def scenarios():
    comm = commercial_after_shock()
    ind, _ = indirect_achievable()

    paper = vave_achievable(months=core.ORIGINAL_TIMELINE_MONTHS)
    s0 = Scenario(
        "S0  Campus plan, before the twist",
        "24 months, commercial intact, no engineering gate on every idea",
        comm.planned, vave_potential(), ind, paper)

    s1 = vave_achievable()
    s1s = Scenario(
        "S1  After the twist, nothing changed",
        "18 months, commercial gone, every idea queues for the same 6-engineer bench",
        comm.surviving, s1.achievable, ind, s1)

    s2 = vave_achievable(ai_triage=True, fast_lane=True)
    s2s = Scenario(
        "S2  + AI triage and a non-load-bearing fast lane",
        "AI screens and drafts, engineer signs; desk check where nothing is structural",
        comm.surviving, s2.achievable, ind, s2)

    s3 = vave_achievable(ai_triage=True, fast_lane=True, aggressive=True)
    s3s = Scenario(
        "S3  + VAVE pushed to the top of the case range",
        "the deepest design changes, mostly on load-bearing parts",
        comm.surviving, s3.achievable, ind, s3,
        integrity_risk="this is the change that failed in the field  -  buying the "
                       "last stretch with load-bearing risk")

    return comm, [s0, s1s, s2s, s3s]


def bench_needed_to_close(scenario):
    """How many bench engineers S3's rules would need to reach the target."""
    ind, _ = indirect_achievable()
    comm = commercial_after_shock().surviving
    target = core.TARGET_ANNUAL_SAVING * 1e6
    for n in range(core.BENCH_ENGINEERS, 60):
        v = vave_achievable(bench_engineers=n, ai_triage=True, fast_lane=True)
        if comm + v.achievable + ind >= target:
            return n, v
    return None, None
