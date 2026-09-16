# Demo Video Script  -  Terravik Cost Twin

A run-through script for recording your demo. Follow it top to bottom; each
scene has exactly what to type/click and a one-line talking point. Total
runtime: roughly 4-6 minutes depending on pacing.

---

## Before you hit record

1. Unzip the project, open a terminal in the folder.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. (Optional, for the live-agent moment) confirm Claude Code works:
   ```
   claude -p "say hi"
   ```
   If that responds, live mode will work on camera. If not, skip Scene 6 
   the whole demo still works perfectly in simulated mode.
4. Close any old terminals/browser tabs from previous test runs so you start clean.
5. Have two windows ready: a terminal (for Scenes 1-3) and a browser tab at
   `localhost:8501` (for Scenes 4-6, after running `streamlit run app.py`).

---

## Scene 1  -  The readiness gate, closed (Terminal)

**Command:**
```
python cli.py --run
```

**What appears:** all 10 levers show `Blocked by the readiness gate`, and
`Booked: $0M/yr (0% of $36.5M)`.

**Say something like:**
> "This is the rule at the heart of the roadmap: you cannot book a saving
> until you can compute it and sign it. No foundations, no data  -  so
> right now, every single lever is blocked. Zero dollars booked."

---

## Scene 2  -  Stand up the foundations, then run again (Terminal)

**Command:**
```
python cli.py --run --ready
```

**What appears:** `All foundations ready`, then 4 Super-Agent levers booked
automatically (~$15.9M), 6 Utility/Human-led levers waiting for sign-off
(~$16.5M).

**Say something like:**
> "Once the data foundation and validation bench are stood up, the gate
> opens. The Orchestrator routes all 10 levers by trust type: Super Agents
> book themselves instantly, but anything Utility or Human-led still needs
> a human signature before it counts."

---

## Scene 3  -  Submit a new idea through the Orchestrator (Terminal)

**Command:**
```
python cli.py
```
Then at the menu:
```
1            (stand up foundations)
a            (mark everything ready)
b            (back to menu)
4            (submit an idea)
```
When prompted, type an idea, e.g.:
```
Hydraulic quick-connect fitting on Model X and Model Z loaders shares the same thread spec but different seal material
```
Saving: `0.6`

> **Note:** you'll only see a "Use the live orchestrator agent to classify?"
> prompt here if Claude Code is installed on this machine. If it appears,
> answer `n` for this scene (keeps it fast and deterministic  -  do the live
> version in Scene 6). If it doesn't appear, that's expected too  -  just
> continue to the next prompt.

Then:
```
y            (submit under the suggested lever)
[Enter]      (keep the load-bearing flag as suggested)
```

**What appears:** routed to **Commonization (Super Agent)**, not
load-bearing, then `BOOKED`.

**Say something like:**
> "This is how a brand-new idea  -  say, something the commonization agent
> just found  -  enters the system. The Orchestrator reads it, decides
> which of the 10 levers it belongs to, and it goes through the exact same
> gate and trust rule as everything else."

---

## Scene 4  -  Switch to Streamlit, show the sign-off queue (Browser)

**Command (new terminal):**
```
streamlit run app.py
```

In the browser: click **✍️ Sign-off Queue**.

**What appears:** the 6 Utility/Human-led items from Scene 2, each with an
Approve (✅) / Reject (❌) button.

**Say something like:**
> "Every one of these still needs a human. Watch what happens when I sign
> one off."

Click ✅ on one or two items. Point out the sidebar total updating live.

---

## Scene 5  -  Submit an idea visually (Browser)

Click **💡 Submit an Idea**. Paste an idea (can reuse the same one, or a new
one like a tyre or seat-frame example), click **Classify with Orchestrator**,
show the routing result, then **Submit to pipeline**.

**Say something like:**
> "Same Orchestrator, same rule, now as something you'd actually hand to a
> category manager on stage."

---

## Scene 6 (optional, if Claude Code is connected)  -  Go live

In the sidebar, toggle **⚡ Live Claude mode** on. Click **Test connection**
to prove it's real, then re-run Scene 5 with **live orchestrator** on, or
go to **🤖 Call an Agent** and run one directly.

**Say something like:**
> "Everything you just saw also runs on real Claude agents  -  no API key,
> this is running on Claude Code right now."

Live calls take 15-90 seconds; don't be afraid to let it sit on camera for a
few seconds, or cut here and resume once it returns.

---

## Closing beat

Go to **📒 Booked Ledger**, show the final total against the $36.5M target.

**Say something like:**
> "From a closed gate and zero dollars, to a live, growing, human-signed
> number  -  that's Intent-Driven Savings end to end."

---

## If something goes wrong on camera

- **Streamlit shows a blank/loading page:** give it 5-10 seconds on first
  load, it's compiling.
- **"Claude Code not found":** live mode isn't available on this machine
  right now  -  just stay in simulated mode, nobody will know the difference.
- **Numbers look different from this script:** you probably clicked
  "Reset run" or foundations weren't fully checked  -  go to **Phase 1
  Foundations** and click **Stand up everything (quick)**.
- **Want a clean slate mid-recording:** sidebar -> **Reset run**.
