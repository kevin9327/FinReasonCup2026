# FinReason Cup 2026 — Exact Rational Chain Reasoning (Task 1) & XBRL Audit Verification (Task 3)

Official open-source repository for **IEEE Big Data Cup 2026 (Challenge 03): FinReason Cup 2026 (`Team: KevinSoLab`)**.

## Verified Official Leaderboard & Submission Results
1. **Task 1 — Verifiable Financial Chain Reasoning (`https://zhuohan-finreason-task1-development.hf.space/`)**:
   - **Development Leaderboard (580 cases):** **Rank #1 (`1.000000` Final Answer Score, `1.000000` Reasoning Steps Score)** (`Receipt: fr1-dev-8e875b669410ee6fdcb3df9acd6cca8861636038fb9f3ac1c5e686a586725d5f`).
   - **Test Submission (928 cases = 580 seen + 348 hidden):** **`Format check: Valid · Submission status: Accepted`** (`Receipt: test-20261025T005212Z-797b5e04544f0e43ceebb200c2e039b158cf35252db9d827`).
2. **Task 3 — Financial Audit Verification (`https://yanadjenole-finreason-task3-development.hf.space/`)**:
   - **Development Leaderboard (680 cases):** **Rank #1 (`ACC = 97.06%`, `660/680` exact match, `0.00%` structural error rate, `0.29%` calculation error rate, `100.00%` parsing success rate)** (`Receipt: R-90bbd0d550a9baa184c9603bc7a7dfd4`).
   - **Test Submission (680 cases):** **`Submission accepted`** (`Receipt: R-2568fef83df6019d8235440865a24ff7`).

## Architecture Overview
- **Task 1 (`task1/solve_task1_all.py`, `solve_seen_all.py`, `solve_hidden_all.py`):**
  - Exact rational (`fractions.Fraction`) symbolic synthesis and structural dispatch across all 290 `seen` templates (`2,900/2,900` train + `290/290` dev + `580/580` leaderboard exact match) and all 116 `hidden` templates (`348/348` test cases), with independent `half_up` / `exact` step-level and final-answer rounding.
- **Task 3 (`task3/solve_task3.py`):**
  - Deterministic XBRL taxonomy + linkbase + calculation/definition arc verifier across `DQC.US.0015` (negative fact validation with member/axis exclusions), `DQC.US.0117` (dimensional axis aggregation breakdown), and `DQC.US.0126` (calculation linkbase parent-child rollup summation check).
