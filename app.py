"""
app.py  -  Streamlit face of the Terravik Cost Twin (Intent-Driven Savings roadmap).
Shares core.py with cli.py. Run: streamlit run app.py
Live Claude mode uses your local Claude Code (Claude Pro, no API key).
"""
import pandas as pd
import streamlit as st
import core

st.set_page_config(page_title="Terravik Cost Twin", page_icon="⚙️", layout="wide")

st.markdown("""
<style>
.acn-banner{background:linear-gradient(120deg,#0B0014 0%,#2B0052 45%,#A100FF 100%);
 border-radius:10px;padding:22px 30px;margin-bottom:16px;}
.acn-banner .lg{font-size:13px;font-weight:700;letter-spacing:1px;color:#E6B8FF;}
.acn-banner .lg span{color:#A100FF;font-weight:900;}
.acn-banner h1{color:#fff!important;font-size:24px;margin:4px 0 2px;font-weight:800;}
.acn-banner p{color:#D8B4FE;margin:0;font-size:13px;}
.stTabs [aria-selected="true"]{color:#A100FF!important;border-bottom:3px solid #A100FF!important;}
[data-testid="stMetric"]{background:#F9F0FF;border:1px solid #E6D0FF;border-radius:8px;padding:8px 12px;}
[data-testid="stSidebar"]{border-right:2px solid #A100FF;}
</style>
<div class="acn-banner">
  <div class="lg">accenture <span>&gt;</span></div>
  <h1>Terravik Cost Twin  -  Intent-Driven Savings</h1>
  <p>From data &rsaquo; to intent &rsaquo; to proven value</p>
</div>
""", unsafe_allow_html=True)

if "state" not in st.session_state:
    st.session_state.state = core.RoadmapState()
if "steps" not in st.session_state:
    st.session_state.steps = []
if "live" not in st.session_state:
    st.session_state.live = False
state: core.RoadmapState = st.session_state.state

TRUST_COLOR = {core.Trust.SUPER_AGENT: "#A100FF", core.Trust.UTILITY: "#BE82FF", core.Trust.HUMAN_LED: "#DCAFFF"}

# --- sidebar ---
st.sidebar.title("⚙️ Orchestrator")
st.sidebar.metric("Target", f"${core.TARGET_ANNUAL_SAVING}M/yr")
st.sidebar.metric("Booked (signed)", f"${state.booked_total}M/yr", f"{state.pct_of_target}% of target")
st.sidebar.metric("Awaiting sign-off", f"${state.pending_total}M/yr")
st.sidebar.progress(min(state.booked_total / core.TARGET_ANNUAL_SAVING, 1.0))
gate_ok = state.can_compute and state.can_sign
st.sidebar.markdown(f"**Readiness gate:** {'🟢 OPEN' if gate_ok else '🔴 CLOSED'}")

st.sidebar.markdown("---")
st.session_state.live = st.sidebar.toggle("⚡ Live Claude mode", value=st.session_state.live,
    help="Off = instant. On = your local Claude Code (Claude Pro, no API key). Same machine only.")
if st.session_state.live:
    if core.claude_available():
        st.sidebar.success("Claude Code found.")
        if st.sidebar.button("Test connection"):
            with st.sidebar, st.spinner("claude -p ..."):
                ok, out = core.call_agent("Say hi in one short sentence.", timeout=30)
            (st.sidebar.success if ok else st.sidebar.error)(out[:150])
    else:
        st.sidebar.error("Claude Code not on PATH  -  falling back to simulated.")
else:
    st.sidebar.caption("Simulated mode  -  instant.")
if st.sidebar.button("Reset run"):
    st.session_state.state = core.RoadmapState(); st.session_state.steps = []; st.rerun()

# --- tabs ---
t_found, t_run, t_submit, t_sign, t_ledger, t_agent, t_demo = st.tabs(
    ["🏗️ Phase 1 Foundations", "🎬 Run Roadmap", "💡 Submit an Idea",
     "✍️ Sign-off Queue", "📒 Booked Ledger", "🤖 Call an Agent", "🎭 Agent-by-Agent Demo"])

# 1) Foundations / readiness gate
with t_found:
    st.subheader("Phase 1  -  Foundations (the readiness gate)")
    st.write("You cannot book a saving until you can **compute** (Should-Cost CoE + data foundation) "
             "and **sign** (validation bench). Stand these up first.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Data foundation**")
        for k, (label, feeds, fname) in core.DATA_FOUNDATION.items():
            # no explicit `key=` here on purpose: with a fixed key, Streamlit
            # ignores `value=` on rerun and the checkbox gets stuck showing
            # its own cached state instead of reflecting programmatic changes
            # (e.g. from the "stand up everything" button below).
            n = len(core.load_foundation_rows(k))
            has = core.foundation_data_exists(k)
            cap = f"{feeds}  -  {fname} ({n} rows)" if has else f"{feeds}  -  no data file found"
            state.foundation[k] = st.checkbox(f"{label}", value=state.foundation[k], help=cap)
            st.caption(cap)
    with c2:
        st.markdown("**R&D redesign  -  frees the bench + CoE**")
        st.caption(f"De-layer 5 to 3, category pods, absorb coordination -> {core.ENGINEERS_FREED} engineers freed "
                   f"(Should-Cost CoE 4, Category pods 6, Validation bench {core.BENCH_ENGINEERS}).")
        state.coe_ready = st.checkbox("Should-Cost CoE stood up (can COMPUTE)", value=state.coe_ready)
        state.bench_ready = st.checkbox("Validation bench stood up (can SIGN)", value=state.bench_ready)
    if st.button("Stand up everything (quick)"):
        for k in state.foundation:
            state.foundation[k] = True
        state.coe_ready = True; state.bench_ready = True; st.rerun()
    st.markdown("---")
    if state.can_compute and state.can_sign:
        st.success("Gate OPEN  -  the 10 levers may run.")
    else:
        st.error("Gate CLOSED  -  savings are blocked until foundations, CoE, and bench are ready.")

    with st.expander("Preview the synthetic foundation data"):
        which = st.selectbox("Foundation file", list(core.DATA_FOUNDATION),
                             format_func=lambda k: core.DATA_FOUNDATION[k][0])
        rows = core.load_foundation_rows(which)
        if rows:
            st.caption(f"{core.DATA_FOUNDATION[which][2]}  -  {len(rows)} rows")
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
        else:
            st.info("This file is empty or not found (the savings ledger starts empty by design).")

# 2) Run roadmap
with t_run:
    st.subheader("The Decision Tree  -  route the 10 levers")
    # show levers grouped by trust
    for trust in core.Trust:
        levers = [l for l in core.LEVERS if l.trust == trust]
        chips = "  ".join(f"<span style='background:{TRUST_COLOR[trust]};color:#fff;padding:2px 8px;"
                          f"border-radius:10px;font-size:12px'>{l.name}</span>" for l in levers)
        st.markdown(f"**{trust.value}**  <span style='color:#888;font-size:12px'>({core.AUTONOMY[trust]})</span><br>{chips}",
                    unsafe_allow_html=True)
        st.write("")
    live = st.session_state.live and core.claude_available()
    if st.button("▶ Run roadmap pipeline", type="primary"):
        with st.status("Running...", expanded=True) as status:
            steps = core.run_pipeline(state, live=live, on_step=lambda m: status.update(label=m))
            status.update(label="Pipeline complete.", state="complete")
        st.session_state.steps = steps; st.rerun()
    for s in st.session_state.steps:
        with st.container(border=True):
            st.markdown(f"**{s.name}**"); st.write(s.detail)
            if s.live_output:
                with st.expander("Live Claude Code response"):
                    st.markdown(s.live_output)
    if state.blocked:
        st.error(f"{len(state.blocked)} lever(s) blocked by the readiness gate  -  see Phase 1 Foundations tab.")

# 3) submit an idea  -  Tier 1 Orchestrator, live or offline
with t_submit:
    st.subheader("Submit an idea")
    st.write(
        "Feed in an idea  -  e.g. an illustrative commonization candidate from a live "
        "agent run  -  and the **Orchestrator** (Tier 1) routes it to the right lever. "
        "It still goes through the same readiness gate and trust rule as everything else."
    )

    if "clf" not in st.session_state:
        st.session_state.clf = None  # (lever_id, load_bearing, rationale, raw)

    desc = st.text_area("Idea description", placeholder=(
        "e.g. Hydraulic quick-connect fitting on Model X and Model Z loaders shares the "
        "same thread spec but different seal material"))
    saving = st.number_input("Estimated saving ($M/yr)", min_value=0.0, value=0.5, step=0.1)

    use_live = st.session_state.live and core.claude_available()
    c1, c2 = st.columns([1, 1])
    if c1.button("🧭 Classify with Orchestrator", disabled=not desc):
        with st.spinner("Classifying..." + (" (live)" if use_live else " (offline keyword match)")):
            lever_id, lb, why, raw = core.classify_idea(desc, live=use_live)
        st.session_state.clf = (lever_id, lb, why, raw)
    if c2.button("Clear", disabled=st.session_state.clf is None):
        st.session_state.clf = None
        st.rerun()

    if st.session_state.clf:
        lever_id, lb, why, raw = st.session_state.clf
        lever = core.lever_by_id(lever_id)
        st.markdown("---")
        st.markdown(
            f"**Routed to:** <span style='background:{TRUST_COLOR[lever.trust]};color:#fff;"
            f"padding:2px 9px;border-radius:10px'>{lever.name}</span>  ({lever.trust.value})",
            unsafe_allow_html=True)
        st.caption(why)
        if raw:
            with st.expander("Live orchestrator response"):
                st.text(raw)

        final_lever_id = st.selectbox(
            "Lever to submit under (override if the routing looks wrong)",
            [l.id for l in core.LEVERS],
            index=[l.id for l in core.LEVERS].index(lever_id),
            format_func=lambda i: core.lever_by_id(i).name,
        )
        final_lb = st.checkbox("Load-bearing / safety-critical", value=lb,
                               help="Overrides the lever's usual trust  -  load-bearing items always need sign-off.")

        if st.button("✅ Submit to pipeline", type="primary"):
            bid, outcome = core.submit_idea(state, final_lever_id, desc, saving, load_bearing=final_lb)
            st.session_state.clf = None
            st.session_state.last_submit = (bid, outcome)
            st.rerun()

    if st.session_state.get("last_submit"):
        bid, outcome = st.session_state.last_submit
        label = {"booked": "Booked automatically", "pending": "Sent for human sign-off",
                 "blocked": "Blocked by the readiness gate", "skipped": "Already submitted"}[outcome]
        fn = {"booked": st.success, "pending": st.warning, "blocked": st.error, "skipped": st.info}[outcome]
        fn(f"**{bid}**: {label}")
        if outcome == "blocked":
            st.caption("See the Phase 1 Foundations tab  -  stand up the readiness gate, then resubmit.")
        if st.button("Dismiss"):
            st.session_state.last_submit = None
            st.rerun()

# 4) sign-off
with t_sign:
    st.subheader("Human sign-off  -  green = sign-off, every tier")
    st.write("Utility and Human-led levers never book without a human signature.")
    if not state.pending:
        st.info("Nothing awaiting sign-off. Run the pipeline with the gate open.")
    for b in list(state.pending):
        with st.container(border=True):
            c1, c2 = st.columns([4, 1])
            c1.markdown(f"<span style='background:{TRUST_COLOR[b.trust]};color:#fff;padding:1px 7px;"
                        f"border-radius:9px;font-size:11px'>{b.trust.value}</span> **{b.lever_name}**",
                        unsafe_allow_html=True)
            c1.caption(f"${b.saving}M/yr  -  {b.note}")
            bb1, bb2 = c2.columns(2)
            if bb1.button("✅", key=f"s_{b.id}", help="Sign off"):
                state.sign_off(b.id, True); st.rerun()
            if bb2.button("❌", key=f"x_{b.id}", help="Reject"):
                state.sign_off(b.id, False); st.rerun()

# 5) ledger
with t_ledger:
    st.subheader("Booked Ledger")
    if state.booked:
        df = pd.DataFrame([{"Lever": b.lever_name, "Trust type": b.trust.value,
                            "Saving ($M/yr)": b.saving, "Status": b.status,
                            "Source": b.source} for b in state.booked])
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.metric("Total booked", f"${state.booked_total}M/yr", f"{state.pct_of_target}% of target")
    else:
        st.info("Nothing booked yet.")
    if state.blocked:
        st.markdown("**Blocked by the readiness gate:**")
        st.dataframe(pd.DataFrame([{"Lever": b.lever_name, "Why": b.note} for b in state.blocked]),
                     use_container_width=True, hide_index=True)

# 6) agent
with t_agent:
    st.subheader("Call a single agent (live)")
    if not (st.session_state.live and core.claude_available()):
        st.info("Turn on Live Claude mode (needs Claude Code) to call agents directly.")
    else:
        agent = st.selectbox("Agent", ["commodity-watch", "should-cost-analytics",
                                        "vave-ideation", "parts-commonization", "savings-ledger"])
        extra = st.text_input("Extra instruction (optional)")
        if st.button("Run agent"):
            prompt = f"Use the {agent} subagent to help with the Terravik case."
            if extra:
                prompt += f" Specifically: {extra}"
            with st.spinner(f"Calling {agent}... 15-90s"):
                ok, out = core.call_agent(prompt, needs_web=(agent == "commodity-watch"))
            (st.success if ok else st.error)("Done" if ok else "Failed")
            st.markdown(out)

# 7) agent-by-agent demo  -  runs every subagent live, one at a time, and
# reveals each one's output as soon as it finishes (not all at once at the end)
with t_demo:
    st.subheader("Agent-by-agent demo  -  watch every subagent run, live, one at a time")
    st.write(
        "Runs the full agent lineup in sequence  -  commodity-watch, should-cost-analytics, "
        "vave-ideation, parts-commonization, orchestrator, savings-ledger  -  each one calling "
        "the real Claude Code subagent against the data files. Each card fills in as soon as "
        "that agent finishes, so you can watch them work one by one instead of waiting for the "
        "whole batch."
    )
    live_ready = core.claude_available()
    if not live_ready:
        st.error("Claude Code not found on PATH  -  this demo needs live agents to run.")
    else:
        if st.button("▶ Run every agent, one by one", type="primary"):
            placeholders = {name: st.empty() for name in core.AGENT_ORDER}
            for name, ph in placeholders.items():
                with ph.container(border=True):
                    st.markdown(f"**{name}**")
                    st.caption("queued...")

            def on_start(name):
                with placeholders[name].container(border=True):
                    st.markdown(f"**⏳ {name}**")
                    st.caption("running now  -  15-90s")

            def on_done(result):
                with placeholders[result.name].container(border=True):
                    icon = "✅" if result.ok else "❌"
                    st.markdown(f"**{icon} {result.name}**")
                    st.markdown(result.output)

            core.run_all_agents(on_start=on_start, on_done=on_done)
            st.success("All agents finished.")

st.markdown("---")
st.caption("Team Fourmula One  -  Accenture B-School Challenge, Decade Edition, Grand Finale.")
