import json
import re
from collections import defaultdict
from decimal import Decimal, ROUND_HALF_UP, localcontext
from fractions import Fraction

train_q = {r["case_id"]: r for r in (json.loads(line) for line in open("FinReasonCup2026/task1/train_questions.jsonl", encoding="utf-8"))}
train_g = {r["case_id"]: r for r in (json.loads(line) for line in open("FinReasonCup2026/task1/train_gold.jsonl", encoding="utf-8"))}
train_m = {r["case_id"]: r for r in (json.loads(line) for line in open("FinReasonCup2026/task1/train_manifest.jsonl", encoding="utf-8"))}

dev_q = {r["case_id"]: r for r in (json.loads(line) for line in open("FinReasonCup2026/task1/dev_questions.jsonl", encoding="utf-8"))}
dev_g = {r["case_id"]: r for r in (json.loads(line) for line in open("FinReasonCup2026/task1/dev_gold.jsonl", encoding="utf-8"))}
dev_m = {r["case_id"]: r for r in (json.loads(line) for line in open("FinReasonCup2026/task1/dev_manifest.jsonl", encoding="utf-8"))}

def strip_contract(qtext):
    idx = qtext.rfind("\n\nAnswer format:")
    return qtext[:idx] if idx != -1 else qtext

NUM_RE = re.compile(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?(?:/[1-9][0-9]*)?")

def extract_numbers(qtext):
    body = strip_contract(qtext)
    # Remove CO2e -> CO_two_e or similar fixed numbers? Wait, if we compare across the 10 train instances, fixed numbers in the template are just constants!
    return [Fraction(s) for s in NUM_RE.findall(body)]

def format_value(val, spec):
    if spec["type"] == "enum":
        return str(val)
    rounding = spec["rounding"]
    if rounding["mode"] == "exact":
        d = val.denominator
        twos = 0
        fives = 0
        while d % 2 == 0:
            d //= 2
            twos += 1
        while d % 5 == 0:
            d //= 5
            fives += 1
        if d != 1:
            return f"{val.numerator}/{val.denominator}"
        places = max(twos, fives)
        scaled = abs(val.numerator) * (2 ** (places - twos)) * (5 ** (places - fives))
        scale = 10 ** places
        whole, frac = divmod(scaled, scale)
        sign = "-" if val < 0 else ""
        if places == 0 or frac == 0:
            return f"{sign}{whole}"
        return f"{sign}{whole}.{f'{frac:0{places}d}'.rstrip('0')}"
    else:
        places = rounding["decimal_places"]
        scale = 10 ** places
        scaled_num = val.numerator * scale
        den = val.denominator
        if scaled_num >= 0:
            rounded = (2 * scaled_num + den) // (2 * den)
        else:
            rounded = -((2 * (-scaled_num) + den) // (2 * den))
        sign = "-" if rounded < 0 else ""
        whole, frac = divmod(abs(rounded), scale)
        if places == 0:
            return f"{sign}{whole}"
        return f"{sign}{whole}.{frac:0{places}d}"

by_template_train = defaultdict(list)
for cid, m in train_m.items():
    by_template_train[m["template_id"]].append((train_q[cid], train_g[cid]))

by_template_dev = {}
for cid, m in dev_m.items():
    by_template_dev[m["template_id"]] = (dev_q[cid], dev_g[cid])

# Check how many templates have enum final_value or enum slots
enum_templates = []
num_templates = []
for tid, items in sorted(by_template_train.items()):
    q0, g0 = items[0]
    has_enum = (q0["answer_spec"]["type"] == "enum") or any(s["result_spec"]["type"] == "enum" for s in q0["trace_spec"]["slots"])
    if has_enum:
        enum_templates.append(tid)
    else:
        num_templates.append(tid)

print(f"Total templates: {len(by_template_train)}, numeric-only: {len(num_templates)}, has_enum: {len(enum_templates)}")
for tid in enum_templates:
    q0, g0 = by_template_train[tid][0]
    print("  ENUM template:", tid, "ans:", q0["answer_spec"], "slots:", [(s["slot_id"], s["result_spec"]) for s in q0["trace_spec"]["slots"]])
