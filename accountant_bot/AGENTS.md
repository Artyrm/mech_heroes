# 🤖 Mech Heroes Project Knowledge Base for Agents

This document serves as the comprehensive guide for any AI agent needing to operate within the Mech Heroes billing/analytics repository. It synthesizes architectural principles, system mechanics, and undocumented behavioral patterns (Gotchas) discovered during codebase analysis.

## 🗺 1. High-Level Architecture & Goals

The project is divided into two major, semi-independent analytical streams, both feeding into final reports:
1.  **Arena Analytics:** Focuses on Top-50 PvP ranking data, energy, and short-term performance. Its goal is near real-time dashboarding. (Location: `arena/`)
2.  **Clan Accountability:** Focuses on long-term, systemic character/clan growth tracking over weeks/days. (Location: `clan_monitor/`)

**Overall Flow:** The typical workflow involves **Data Collection $\rightarrow$ Processing/Calculation $\rightarrow$ Reporting/Deployment.**

## ⚙️ 2. Essential Commands & Execution Context

As of current knowledge, no single `Makefile` dictates the build lifecycle. The project relies on specialized, purpose-built Python scripts.

| Area | Script | Purpose | Notes / Usage |
| :--- | :--- | :--- | :--- |
| **Arena Fetching** | `arena/fetch_arena.py` | Pulls raw leaderboard state (`userState.arena.leaderboards`) from the live API. | Requires active session/API key. Primary source of *fresh* ranking data. |
| **Arena Syncing** | `arena/sync_from_init.py` | Re-imports historical data from `init_dumps/` folders. | Used for offline analysis. **Crucial:** It handles multiple possible JSON structures for historical dumps. |
| **Arena Analysis** | `arena/analytics_engine.py` | Core logic for comparing two snapshots ($T_1 \rightarrow T_2$). | Must be called with two valid data dictionaries (snapshots). |
| **Clan Accounting** | `clan_monitor/clan_accountant.py` | Calculates complex, non-native metrics (e.g., contribution percentages, true cost). | Highly customized logic. Requires clean, processed data dumps. |
| **General Workflow** | `arena/arena_update.py` | The main orchestration script. | Runs the full pipeline (Fetch $\rightarrow$ Store $\rightarrow$ Generate $\rightarrow$ Deploy). |
| **Reporting** | `arena/generate_dashboard.py` | Consolidates all snapshots and renders the interactive report. | Output is a self-contained, standalone HTML file. |
| **Deployment** | `deploy.py` | Uploads the final reports to the public server. | **CRITICAL:** Depends on the `.env` file for FTP credentials. |

## 🧠 3. Core Architectural Concepts & Patterns

### 3.1. Data Philosophy: Local-First / Offline Resilience
*   **Principle:** All critical components are designed to function even when disconnected from the live API (Local-First).
*   **Implementation:** Scripts prioritize reading data from `init_dumps/` or `snapshots/` if the network connection fails, ensuring historical analysis is always possible.
*   **Gotcha:** When analyzing a dump, assume the timestamp is the source of truth for that data point, even if the API was called later.

### 3.2. API Interaction Pattern (The `/init` Request)
*   **Endpoint:** `/init`.
*   **Payload Structure:** The full state is nested deeply within `data.userState`.
*   **Critical Naming:** The leaderboard cache is found under `userState.arena.leaderboards`.
*   **Mandatory Field Check:** Always check for `lastUpdateTime` to determine data freshness.
*   **Failure Handling:** If the API returns status codes other than 200 (e.g., 404 due to session mismatch), the system should fall back to local dump handling rather than failing the entire job.

### 3.3. Data Format Gotchas & Conventions (MANDATORY)
1.  **Localization:** All numerical data transferred from the API (e.g., `opponentRating`, `ourRatingDelta`, `damageDone`) are **STRINGS**. They use the Russian comma (`,`) as a decimal separator (e.g., `"105495,098"`). Any arithmetic operation **MUST** convert the string to a float/decimal (`float("105495,098".replace(",", "."))`) before calculation.
2.  **Date Handling:** The full timestamp format is `DD/MM/YYYY_HH:MM:SS.xxxx`. Use Python's `datetime` library, but be aware of potential mixed day/month orderings depending on the source dump.
3.  **Unit Levels (Mechanics):** The API uses a pseudo-level system (`raw_level` 0-475). Agents must use the provided mapping (advanced math in `docs/mech_heroes_game_notes.md`) or rely on the stored `statsCoefficients` list to understand the true growth curve and identify the "jump" mechanics (e.g., level jumps occur at specific indexed points in the API dump).
4.  **Data Structure Reference:** The `battlesHistory` list (in the API dump) is the source of truth for historical conflict data and should be the primary input for any comparison tool.

### 3.4. Analytics Specific Conventions
*   **Arena Delta Calculation:** The core logic for calculating relative change ($\Delta R$, $\Delta W$, $\Delta L$) is non-trivial; the formula for rank change requires tracking the difference in position, not just overall rating difference.
*   **Reporting Generation:** The dashboard (`generate_dashboard.py`) architecture expects all raw snapshots to be aggregated and passed as a large JSON blob to the browser. This means the preprocessing step must be highly robust and non-destructive.

## 🚨 4. Global Project Gotchas (Non-Obvious Knowledge)

1.  **State Staleness in Reports:** The reports (`dashboard.html`) are **static, fully contained files**. Any analysis of *change* must be done by comparing two time-stamped inputs ($T_1$ and $T_2$) processed by `analytics_engine.py` and then embedding that delta calculation into the template, never by trusting the raw snapshot data for change analysis alone.
2.  **Stat Tracking vs Historical Data:** The sheer volume of historical battle data (the directories like `battle_2026-05-19_14-27-57_0000.html`) is often *redundant* for modern analytics. The most reliable data source for combat statistics is the `battlesHistory` array within the *live* `/init` payload, though the individual HTML reports provide excellent granular detail and are useful for debugging.
3.  **Dependencies:** The system relies heavily on a specific Python environment (Anaconda/Python 3.x environment indicated by `arena_update.py`'s path) because of its scientific computing nature (potential use of `pandas` or `numpy`, though not explicitly listed). **Do not** run setup without confirming the Anaconda environment activation.

## 🧹 5. Best Practices for Agent Workflow

*   **Analysis First:** Always run analysis functions (`analytics_engine.py`) *before* generating reports (`generate_dashboard.py`).
*   **Debug Isolation:** Use the `debug/` directory content (e.g., `alo_v2.py`, `find_all_hashes.py`) to isolate and verify specific calculation methods (e.g., cost calculation, rating decay).
*   **Data Verification:** Use the `compare_ksotar_logic.py` suite in `clan_monitor/` to validate any complex calculation modules before deploying a new feature.