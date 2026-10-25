import json
import sys
sys.path.insert(0, "FinReasonCup2026/task1")
import test_synthesizer as ts
from inspect_templates_detail import lb_q, test_q
from solve_seen_all import solve_seen_question
from solve_hidden_all import match_seen_tid, solve_hidden_question

def main():
    # 1. Verify Train (2900/2900) and Dev (290/290)
    train_ok = 0
    train_total = 0
    for tid, items in ts.by_template_train.items():
        for q, g in items:
            train_total += 1
            pred = solve_seen_question(tid, q)
            s_map = {s["slot_id"]: s["value"] for s in pred["steps"]}
            if pred["final_answer"]["value"] == g["final_value"] and s_map == g["slot_values"]:
                train_ok += 1
            else:
                raise AssertionError(f"Train mismatch on {tid} ({q['case_id']})")

    dev_ok = 0
    dev_total = 0
    dev_preds = []
    for tid, (q, g) in ts.by_template_dev.items():
        dev_total += 1
        pred = solve_seen_question(tid, q)
        dev_preds.append(pred)
        s_map = {s["slot_id"]: s["value"] for s in pred["steps"]}
        if pred["final_answer"]["value"] == g["final_value"] and s_map == g["slot_values"]:
            dev_ok += 1
        else:
            raise AssertionError(f"Dev mismatch on {tid} ({q['case_id']})")

    print(f"TRAIN EXACT MATCH: {train_ok} / {train_total}")
    print(f"DEV EXACT MATCH:   {dev_ok} / {dev_total}")

    dev_preds.sort(key=lambda r: r["case_id"])
    with open("FinReasonCup2026/task1/dev_eval_predictions.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in dev_preds:
            f.write(json.dumps(r, sort_keys=True) + "\n")

    # 2. Generate Leaderboard Predictions (580 seen questions)
    lb_preds = []
    for q in lb_q:
        tid = match_seen_tid(q["question"])
        assert tid is not None, f"Unmatched LB question: {q['case_id']}"
        lb_preds.append(solve_seen_question(tid, q))

    with open("FinReasonCup2026/task1/leaderboard_predictions.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in lb_preds:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print(f"LEADERBOARD PREDICTIONS WRITTEN: {len(lb_preds)}")

    # 3. Generate Test Predictions (928 questions = 580 seen + 348 hidden)
    test_preds = []
    seen_cnt = 0
    hidden_cnt = 0
    for q in test_q:
        tid = match_seen_tid(q["question"])
        if tid is not None:
            seen_cnt += 1
            test_preds.append(solve_seen_question(tid, q))
        else:
            hidden_cnt += 1
            test_preds.append(solve_hidden_question(q))

    with open("FinReasonCup2026/task1/test_predictions.jsonl", "w", encoding="utf-8", newline="\n") as f:
        for r in test_preds:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    print(f"TEST PREDICTIONS WRITTEN: {len(test_preds)} (seen={seen_cnt}, hidden={hidden_cnt})")

if __name__ == "__main__":
    main()
