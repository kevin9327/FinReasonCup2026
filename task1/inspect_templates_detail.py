import json
import re
from collections import defaultdict

train_q = {r["case_id"]: r for r in (json.loads(line) for line in open("FinReasonCup2026/task1/train_questions.jsonl", encoding="utf-8"))}
train_g = {r["case_id"]: r for r in (json.loads(line) for line in open("FinReasonCup2026/task1/train_gold.jsonl", encoding="utf-8"))}
train_m = {r["case_id"]: r for r in (json.loads(line) for line in open("FinReasonCup2026/task1/train_manifest.jsonl", encoding="utf-8"))}

dev_q = {r["case_id"]: r for r in (json.loads(line) for line in open("FinReasonCup2026/task1/dev_questions.jsonl", encoding="utf-8"))}
dev_g = {r["case_id"]: r for r in (json.loads(line) for line in open("FinReasonCup2026/task1/dev_gold.jsonl", encoding="utf-8"))}
dev_m = {r["case_id"]: r for r in (json.loads(line) for line in open("FinReasonCup2026/task1/dev_manifest.jsonl", encoding="utf-8"))}

lb_q = [json.loads(line) for line in open("FinReasonCup2026/task1/leaderboard_questions.jsonl", encoding="utf-8")]
test_q = [json.loads(line) for line in open("FinReasonCup2026/task1/test_questions.jsonl", encoding="utf-8")]

def strip_contract(qtext):
    idx = qtext.rfind("\n\nAnswer format:")
    return qtext[:idx] if idx != -1 else qtext

by_template = defaultdict(list)
for cid, m in list(train_m.items()) + list(dev_m.items()):
    q = train_q.get(cid) or dev_q.get(cid)
    g = train_g.get(cid) or dev_g.get(cid)
    by_template[m["template_id"]].append((q, g, m))

print("Total seen templates:", len(by_template))

# Build a canonical regex per template by diffing tokens across its 11 instances
# Tokenize into numbers, words, or punctuation
TOKEN_RE = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:/[1-9][0-9]*)?|[A-Za-z_][A-Za-z0-9_-]*|\s+|[^\w\s]")

template_regexes = {}
for tid, items in by_template.items():
    bodies = [strip_contract(q["question"]) for q, _, _ in items]
    tok_lists = [TOKEN_RE.findall(b) for b in bodies]
    lengths = {len(t) for t in tok_lists}
    if len(lengths) == 1:
        L = next(iter(lengths))
        pat_parts = []
        var_idx = 0
        for i in range(L):
            vals = {t[i] for t in tok_lists}
            is_num = all(re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:/[1-9][0-9]*)?", v) for v in vals)
            if len(vals) == 1 and not is_num:
                pat_parts.append(re.escape(next(iter(vals))))
            elif is_num:
                pat_parts.append(rf"(?P<v{var_idx}>-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:/[1-9][0-9]*)?)")
                var_idx += 1
            else:
                pat_parts.append(rf"(?P<v{var_idx}>[A-Za-z0-9_-]+)")
                var_idx += 1
        template_regexes[tid] = re.compile("^" + "".join(pat_parts) + "$")
    else:
        print("Variable token length template:", tid, lengths)

lb_matched = 0
for r in lb_q:
    body = strip_contract(r["question"])
    matched_tids = [tid for tid, rx in template_regexes.items() if rx.match(body)]
    if len(matched_tids) == 1:
        lb_matched += 1
    else:
        print("LB odd match:", r["case_id"], matched_tids, body[:120])
print(f"LB matched with template_regexes: {lb_matched}/{len(lb_q)}")

test_seen = []
test_hidden = []
for r in test_q:
    body = strip_contract(r["question"])
    matched_tids = [tid for tid, rx in template_regexes.items() if rx.match(body)]
    if len(matched_tids) == 1:
        test_seen.append((r, matched_tids[0]))
    elif len(matched_tids) == 0:
        test_hidden.append(r)
    else:
        print("Test multiple match:", r["case_id"], matched_tids)

print(f"Test seen: {len(test_seen)}, Test hidden: {len(test_hidden)}")
