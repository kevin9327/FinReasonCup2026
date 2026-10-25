import json
import re
from fractions import Fraction
import sys
sys.path.insert(0, "FinReasonCup2026/task1")
import test_synthesizer as ts

with open("FinReasonCup2026/task1/synthesized_seen_formulas.json", "r", encoding="utf-8") as f:
    SYNTH_CACHE = json.load(f)

def b_str(cond):
    return "true" if cond else "false"

def solve_explicit_seen(tid, q_text):
    v = ts.extract_numbers(q_text)
    ql = q_text.lower()

    if tid == "fp.accounting_and_financial_reporting.depreciation_and_amortization.partial_year_disposal.intermediate.v1":
        # NUMS0: ['50000', '5', '3', '1', '15000']
        cost, life, months, full_yrs, proceeds = v[0], v[1], v[2], v[3], v[4]
        ann_dep = cost / life
        tot_dep = ann_dep * (months / Fraction(12) + full_yrs)
        carrying = cost - tot_dep
        return {"trace_1": ann_dep, "trace_2": tot_dep, "trace_3": carrying}, proceeds - carrying

    if tid == "fp.accounting_and_financial_reporting.depreciation_and_amortization.sum_of_years_digits.basic.v1":
        # NUMS0: ['60000', '5', '1', '1']
        cost, life, yr = v[0], v[1], v[2]
        syd = life * (life + 1) / Fraction(2)
        factor = (life - yr + 1) / syd
        return {"trace_1": syd, "trace_2": factor}, cost * factor

    if tid == "fp.corporate_finance.div_policies.dividend_lintner_smoothing.intermediate.v1":
        # NUMS0: ['2', '35', '3/4', '30', '1000000']
        eps, p_pct, d0, a_pct, shares = v[0], v[1], v[2], v[3], v[4]
        d_target = eps * (p_pct / Fraction(100))
        d_new = d0 + (a_pct / Fraction(100)) * (d_target - d0)
        return {"trace_1": d_target, "trace_2": d_new}, d_new * shares

    if tid == "fp.corporate_finance.div_policies.dividend_lintner_three_year_avg.advanced.v1":
        # NUMS0: ['3/2', '2', '5/2', '35', '2/5', '30', '1000000']
        e1, e2, e3, p_pct, d0, a_pct, shares = v[0], v[1], v[2], v[3], v[4], v[5], v[6]
        e_avg = (e1 + e2 + e3) / Fraction(3)
        d_target = e_avg * (p_pct / Fraction(100))
        d_new = d0 + (a_pct / Fraction(100)) * (d_target - d0)
        return {"trace_1": e_avg, "trace_2": d_new}, d_new * shares

    if tid == "fp.corporate_finance.eps.eps_pref_div_split_weighted.advanced.v1":
        # NUMS0: ['3500000', '12000', '3/10', '300000', '2']
        ni, pref_sh, q_div, beg_sh, split = v[0], v[1], v[2], v[3], v[4]
        ann_pref = pref_sh * q_div * 4
        adj_sh = beg_sh * split
        return {"trace_1": ann_pref, "trace_2": adj_sh}, (ni - ann_pref) / adj_sh

    if tid == "fp.corporate_finance.eps.eps_pref_div_weighted.intermediate.v1":
        # NUMS0: ['2500000', '50000', '450000', '36000', '1', '1', '12', '12']
        ni, pref_div, beg_sh, new_sh, mos = v[0], v[1], v[2], v[3], v[4]
        common_ni = ni - pref_div
        w_sh = beg_sh + new_sh * mos / Fraction(12)
        return {"trace_1": common_ni, "trace_2": w_sh}, common_ni / w_sh

    if tid == "fp.corporate_finance.eps.eps_quarterly_pref_buyback.intermediate.v1":
        # NUMS0: ['365', '3000000', '15000', '3/10', '500000', '20000', '1', '1', '365', '365']
        ni, pref_sh, q_div, beg_sh, buy_sh, days = v[1], v[2], v[3], v[4], v[5], v[6]
        ann_pref = pref_sh * q_div * 4
        w_sh = beg_sh - buy_sh * days / Fraction(365)
        return {"trace_1": ann_pref, "trace_2": w_sh}, (ni - ann_pref) / w_sh

    if tid == "fp.corporate_finance.eps.eps_quarterly_pref_div.basic.v1":
        # NUMS0: ['2000000', '12000', '1/4', '400000']
        ni, pref_sh, q_div, com_sh = v[0], v[1], v[2], v[3]
        ann_pref = pref_sh * q_div * 4
        common_ni = ni - ann_pref
        return {"trace_1": ann_pref, "trace_2": common_ni}, common_ni / com_sh

    if tid == "fp.corporate_finance.wacc.capm_wacc.basic.v1":
        # NUMS0: ['40', '15', '4/5', '2', '8', '4', '25', '1', '100']
        E, D, beta, rf, rm, kd, T = v[0], v[1], v[2], v[3], v[4], v[5], v[6]
        mrp = rm - rf
        ke = rf + beta * mrp
        V = E + D
        wE, wD = E / V, D / V
        wacc = wE * ke + wD * kd * (1 - T / Fraction(100))
        return {"market_risk_premium_percent": mrp, "capm_equity_cost_percent": ke, "debt_weight": wD}, wacc

    if tid == "fp.corporate_finance.wacc.inflation_adjusted_capm_wacc.advanced.v1":
        # NUMS0: ['60', '15', '15', '9/10', '9', '1', '2', '3', '5', '25', ...]
        E, DA, DB, beta, rn, pi, rf, ka, kb, T = v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9]
        rm = Fraction(100) * ((1 + rn / Fraction(100)) / (1 + pi / Fraction(100)) - 1)
        ke = rf + beta * (rm - rf)
        D = DA + DB
        kd = (DA * ka + DB * kb) / D
        V = E + D
        wE, wD = E / V, D / V
        real_wacc = wE * ke + wD * kd * (1 - T / Fraction(100))
        return {"real_market_return_percent": rm, "capm_real_equity_cost_percent": ke, "weighted_real_debt_cost_percent": kd}, real_wacc

    if tid == "fp.corporate_finance.wacc.preferred_capm_wacc.intermediate.v1":
        # NUMS0: ['50', '10', '20', '9/10', '2', '8', '6', '4', '24', '1', '100']
        E, P, D, beta, rf, rm, kp, kd, T = v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8]
        ke = rf + beta * (rm - rf)
        V = E + P + D
        wE, wP, wD = E / V, P / V, D / V
        at_kd = kd * (1 - T / Fraction(100))
        wacc = wE * ke + wP * kp + wD * at_kd
        return {"capm_equity_cost_percent": ke, "preferred_weight": wP, "after_tax_debt_cost_percent": at_kd}, wacc

    if tid == "fp.corporate_finance.wacc.standard_wacc.basic.v1":
        # NUMS0: ['20', '10', '6', '3', '20', '1', '100']
        E, D, ke, kd, T = v[0], v[1], v[2], v[3], v[4]
        V = E + D
        wE, wD = E / V, D / V
        at_kd = kd * (1 - T / Fraction(100))
        wacc = wE * ke + wD * at_kd
        return {"total_capital": V, "equity_weight": wE, "after_tax_debt_cost_percent": at_kd}, wacc

    if tid == "fp.corporate_finance.wacc.weighted_debt_wacc.intermediate.v1":
        # NUMS0: ['40', '20', '3', '10', '6', '6', '22', '1', '100']
        E, Ds, ks, Du, ku, ke, T = v[0], v[1], v[2], v[3], v[4], v[5], v[6]
        D = Ds + Du
        kd = (Ds * ks + Du * ku) / D
        V = E + D
        wE, wD = E / V, D / V
        wacc = wE * ke + wD * kd * (1 - T / Fraction(100))
        return {"total_debt": D, "weighted_debt_cost_percent": kd, "debt_weight": wD}, wacc

    if tid == "fp.crypto_finance.global_events_impact.global_macro_strategy.advanced.v1":
        # NUMS0: ['1100', '-20', '0', '0', '-10', '10']
        P0, i1, i2, i3, flr, cap = v[0], v[1], v[2], v[3], v[4], v[5]
        raw = i1 + i2 + i3
        clipped = min(max(raw, flr), cap)
        mult = 1 + clipped / Fraction(100)
        return {"raw_impact_trace": raw, "clipped_impact_trace": clipped, "price_multiple_trace": mult}, P0 * mult

    if tid == "fp.crypto_finance.sentiments.multi_factor_sentiment.advanced.v1":
        # NUMS0: ['-3', '0', '0', '1', '1', '101/100', '-2', '2']
        s1, s2, s3, w1, w2, w3, flr, cap = v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]
        tw = s1 * w1
        nw = s2 * w2
        pr = s3 * w3
        raw = tw + nw + pr
        clipped = min(max(raw, flr), cap)
        return {"tweet_component_trace": tw, "news_component_trace": nw, "raw_composite_trace": raw}, clipped

    if tid == "fp.finance_regulation.aml.beneficial_ownership.intermediate.v1":
        # NUMS0: ['10', '1499/100', '25']
        direct, indirect, thresh = v[0], v[1], v[2]
        ctrl = "the scenario control flag is true" in ql
        tot = direct + indirect
        met = tot >= thresh
        return {"total_ownership_percent": tot, "ownership_threshold_met": b_str(met)}, b_str(met or ctrl)

    if tid == "fp.finance_regulation.aml.multi_entity_ownership.intermediate.v1":
        # NUMS0: ['5', '5', '5', '25', '15']
        a, b, c, agg_t, max_t = v[0], v[1], v[2], v[3], v[4]
        agg = a + b + c
        largest = max(a, b, c)
        return {"aggregate_ownership_percent": agg, "largest_entity_percent": largest}, b_str(agg >= agg_t or largest >= max_t)

    if tid == "fp.finance_regulation.aml.sar_decision.advanced.v1":
        # NUMS0: ['499/100', '5', '8', '8', '5']
        score, med_t, high_t = v[0], v[1], v[2]
        tx_flag = "transaction flag is true." in ql
        id_flag = "identity flag is true." in ql
        high = score >= high_t or (tx_flag and id_flag)
        rev = score >= med_t or tx_flag or id_flag
        ans = "file_sar" if high else ("manual_review" if rev else "no_action")
        return {"high_trigger": b_str(high), "review_trigger": b_str(rev)}, ans

    if tid == "fp.finance_regulation.aml.structuring_detection.basic.v1":
        # NUMS0: ['4', '9999', '5', '10000']
        cnt, amt, cnt_t, ceil_a = v[0], v[1], v[2], v[3]
        c_met = cnt >= cnt_t
        a_met = amt < ceil_a
        return {"count_trigger_met": b_str(c_met), "amount_below_ceiling": b_str(a_met)}, b_str(c_met and a_met)

    if tid == "fp.finance_regulation.aml.threshold_violation.basic.v1":
        # NUMS0: ['99', '100']
        amt, thresh = v[0], v[1]
        return {"amount_excess": amt - thresh}, b_str(amt >= thresh)

    if tid == "fp.finance_regulation.basel.leverage_ratio.basic.v1":
        # NUMS0: ['1', '299/10', '1000', '3']
        t1, exp, min_pct = v[1], v[2], v[3]
        lev = t1 * Fraction(100) / exp
        return {"leverage_percent": lev}, b_str(lev >= min_pct)

    if tid == "fp.finance_regulation.basel.multi_requirement.advanced.v1":
        # NUMS0: ['1', '30', '1000', '105', '1000', '100', '100', '3', '21/2', '100']
        t1, exp, tot_cap, rwa, liq, outf, l_min, c_min, q_min = v[1], v[2], v[3], v[4], v[5], v[6], v[7], v[8], v[9]
        lm = (t1 * Fraction(100) / exp) >= l_min
        cm = (tot_cap * Fraction(100) / rwa) >= c_min
        qm = (liq * Fraction(100) / outf) >= q_min
        return {"leverage_met": b_str(lm), "capital_met": b_str(cm), "liquidity_met": b_str(qm)}, b_str(lm and cm and qm)

    if tid == "fp.finance_regulation.basel.rwa_increase.intermediate.v1":
        # NUMS0: ['1049/10', '1000', '0', '21/2']
        cap, rwa, inc, thresh = v[0], v[1], v[2], v[3]
        new_rwa = rwa + inc
        new_pct = cap * Fraction(100) / new_rwa
        return {"new_rwa_usd_million": new_rwa, "new_capital_percent": new_pct}, b_str(new_pct >= thresh)

    if tid == "fp.finance_regulation.compliance.composite_risk.advanced.v1":
        inh, ctrl, inc = v[0], v[1], v[2]
        ovr = "high-risk override is true." in ql
        res = inh * (1 - ctrl)
        comp = res + inc
        high = comp >= 8 or ovr
        ans = "high_risk" if high else ("medium_risk" if comp >= 5 else "low_risk")
        return {"residual_risk_score": res, "composite_risk_score": comp, "high_trigger": b_str(high)}, ans

    if tid == "fp.finance_regulation.kyc.country_sector_risk.intermediate.v1":
        base, mult = v[0], v[1]
        ovr = "the scenario high-risk override is true." in ql
        edd = "the sector edd flag is true." in ql
        comp = base * mult
        band = "high_risk" if comp >= 8 else ("medium_risk" if comp >= 5 else "standard_risk")
        ans = "high_risk" if (comp >= 8 or ovr) else ("medium_risk" if (comp >= 5 or edd) else "standard_risk")
        return {"composite_risk_score": comp, "numeric_risk_band": band}, ans

    if tid == "fp.finance_regulation.kyc.customer_risk_rating.advanced.v1":
        res_pts, vol = v[0], v[1]
        m_acc = re.search(r"account type is ([a-z_]+)", ql)
        acc = m_acc.group(1)
        acc_pts = {"savings": Fraction(1), "business": Fraction(3), "offshore": Fraction(4)}[acc]
        vol_pts = Fraction(1) if vol <= 10000 else (Fraction(2) if vol <= 25000 else (Fraction(3) if vol <= 50000 else Fraction(4)))
        esc = Fraction(1) if (acc == "offshore" and vol > 25000) else Fraction(0)
        tot = res_pts + acc_pts + vol_pts + esc
        ans = "low_risk" if tot <= 5 else ("medium_risk" if tot <= 8 else "high_risk")
        return {"volume_risk_points": vol_pts, "escalation_bonus": esc, "total_risk_points": tot}, ans

    if tid == "fp.finance_regulation.kyc.customer_type.basic.v1":
        holders = v[0]
        m_nat = re.search(r"account nature is ([a-z_]+)", ql)
        nat = m_nat.group(1)
        mapping = {
            "personal_savings": ("natural_person", "individual_customer"),
            "joint": ("natural_person", "individual_customer"),
            "minor_account": ("natural_person", "individual_customer"),
            "trust": ("legal_arrangement", "trust_account"),
            "nonprofit_organization": ("nonprofit_entity", "ngo_noncorporate_entity"),
            "partnership": ("partnership_entity", "partnership_customer"),
            "business": ("legal_person", "corporate_customer"),
            "offshore_company": ("legal_person", "corporate_customer"),
        }
        fam, cust = mapping[nat]
        h_cfg = "single_holder" if holders == 1 else "multiple_holders"
        return {"legal_form_family": fam, "holder_configuration": h_cfg}, cust

    if tid == "fp.finance_regulation.kyc.document_validity.basic.v1":
        doc = re.search(r"submitted document is ([a-z_]+)", ql).group(1)
        use = re.search(r"requested use is ([a-z_]+)", ql).group(1)
        cat_map = {
            "passport": "identity_only",
            "national_id_card": "identity_only",
            "utility_bill": "address_only",
            "bank_statement": "address_only",
            "rental_agreement": "address_only",
            "drivers_license": "dual_purpose",
            "employee_id": "unsupported",
            "student_id": "unsupported",
        }
        cat = cat_map[doc]
        if use == "identity_verification":
            valid = cat in ("identity_only", "dual_purpose")
        else:
            valid = cat in ("address_only", "dual_purpose")
        return {"document_category": cat}, b_str(valid)

    if tid == "fp.finance_regulation.kyc.source_of_funds.intermediate.v1":
        s_sc, j_sc, amt = v[0], v[1], v[2]
        trace = re.search(r"traceability is ([a-z_]+)", ql).group(1)
        tot = s_sc + j_sc
        hv_low = amt >= 100000 and trace == "low"
        route = "high_value_low_traceability_route" if hv_low else "standard_amount_route"
        ans = "high_risk" if (tot >= 12 or hv_low) else ("medium_risk" if tot >= 8 else "low_risk")
        return {"total_risk_score": tot, "amount_traceability_route": route}, ans

    if tid == "fp.finance_regulation.security.disclosure_threshold.basic.v1":
        own, thresh = v[0], v[1]
        return {"ownership_margin_percent": own - thresh}, b_str(own >= thresh)

    if tid == "fp.finance_regulation.security.merger_timing.advanced.v1":
        ev, disc, allow = v[0], v[1], v[2]
        leak = "leak flag is true." in ql
        delay = disc - ev
        late = delay > allow
        ans = "immediate_escalation" if leak else ("late_disclosure" if late else "timely_disclosure")
        return {"disclosure_delay_days": delay, "late_condition": b_str(late)}, ans

    if tid == "fp.finance_regulation.security.multiple_reporting_thresholds.intermediate.v1":
        own, val, own_t, val_t = v[0], v[1], v[2], v[3]
        ot, vt = own >= own_t, val >= val_t
        return {"ownership_trigger": b_str(ot), "value_trigger": b_str(vt)}, b_str(ot or vt)

    if tid == "fp.finance_regulation.security.offer_investment_limit.intermediate.v1":
        inc, nw, prop = v[0], v[1], v[2]
        base = max(inc, nw)
        lim = base * Fraction(1, 10)
        return {"financial_base_usd": base, "investment_limit_usd": lim}, b_str(prop <= lim)

    if tid == "fp.financial_markets.bond_pricing.three_year_coupon_bond_price.intermediate.v1":
        face, c_pct, y_pct = v[0], v[1], v[2]
        c = face * c_pct / Fraction(100)
        term_cf = face + c
        y = 1 + y_pct / Fraction(100)
        pv_term = term_cf / (y ** 3)
        price = c / y + c / (y ** 2) + pv_term
        return {"annual_coupon_trace": c, "terminal_cash_flow_trace": term_cf, "pv_terminal_trace": pv_term}, price

    if tid == "fp.financial_markets.option_pricing.one_period_binomial_call.intermediate.v1":
        S, K, u, d, r_pct = v[0], v[1], v[2], v[3], v[4]
        r = r_pct / Fraction(100)
        Cu = max(Fraction(0), S * u - K)
        Cd = max(Fraction(0), S * d - K)
        q_prob = ((1 + r) - d) / (u - d)
        val = (q_prob * Cu + (1 - q_prob) * Cd) / (1 + r)
        return {"up_payoff_trace": Cu, "down_payoff_trace": Cd, "up_probability_trace": q_prob}, val

    if tid == "fp.financial_markets.stock_market_analysis.two_lot_sale_net_profit.advanced.v1":
        n1, p1, n2, p2, psell = v[0], v[1], v[2], v[3], v[4]
        tot_sh = n1 + n2
        tot_cost = n1 * p1 + n2 * p2
        avg_cost = tot_cost / tot_sh
        proceeds = tot_sh * psell
        return {"total_shares_trace": tot_sh, "average_cost_trace": avg_cost, "sale_proceeds_trace": proceeds}, proceeds - tot_cost

    if tid == "fp.financial_ratios.effratio.investment_vs_sales_push.advanced.v1":
        sales, assets, add_a, ded_a, inc_s = v[0], v[1], v[3], v[4], v[6]
        t1 = sales / (assets + add_a - ded_a)
        t2 = (sales * (1 + inc_s / Fraction(100))) / assets
        return {"trace_1": t1, "trace_2": t2}, t2 - t1

    if tid == "fp.financial_ratios.liqratio.liquidity_minimum_quick_ratio.advanced.v1":
        # NUMS0: ['25000', '5000', '20000', '15000', '1000', '30000', '13/10']
        cash, sec, ar, inv, prep, cl, min_qr = v[0], v[1], v[2], v[3], v[4], v[5], v[6]
        tot_ca = cash + sec + ar + inv + prep
        qa = cash + sec + ar
        cr = tot_ca / cl
        qr = qa / cl
        req_qa = cl * min_qr
        return {"trace_1": cr, "trace_2": qr, "trace_3": req_qa}, max(Fraction(0), req_qa - qa)

    if tid == "fp.financial_ratios.profitratio.dual_margin_gap.intermediate.v1":
        # NUMS0: ['250000', '125000', '12500']
        rev, cogs, ni = v[0], v[1], v[2]
        gm = (rev - cogs) * Fraction(100) / rev
        nm = ni * Fraction(100) / rev
        return {"trace_1": gm, "trace_2": nm}, gm - nm

    if tid == "fp.fintech.payment_technologies.effective_monthly_fee.advanced.v1":
        # NUMS0: ['101', '100', '21', '1/10', '2', '10200', '3']
        cnt, avg_v, sub, flat, r1_pct, cap, r2_pct = v[0], v[1], v[2], v[3], v[4], v[5], v[6]
        tot_sales = cnt * avg_v
        t1_sales = min(tot_sales, cap)
        t2_sales = max(Fraction(0), tot_sales - cap)
        tot_fees = sub + cnt * flat + t1_sales * (r1_pct / Fraction(100)) + t2_sales * (r2_pct / Fraction(100))
        return {"total_sales_trace": tot_sales, "tier_two_sales_trace": t2_sales, "total_fees_trace": tot_fees}, tot_fees * Fraction(100) / tot_sales

    if tid == "fp.investment_analysis.ci.midterm_deposit_compound_interest.advanced.v1":
        # NUMS0: ['10500', '2', '550', '1', '2']
        P0, t1, D, r_pct, t2 = v[0], v[1], v[2], v[3], v[4]
        g = 1 + r_pct / Fraction(100)
        init_end = P0 * (g ** int(t1 + t2))
        dep_end = D * (g ** int(t2))
        end_bal = init_end + dep_end
        return {"initial_ending_trace": init_end, "deposit_ending_trace": dep_end, "ending_balance_trace": end_bal}, end_bal - (P0 + D)

    if tid == "fp.investment_analysis.ci.quarterly_compound_interest.basic.v1":
        # NUMS0: ['2111', '8', '2', '4', '1', '100']
        P, r_pct, n_yr = v[0], v[1], v[2]
        q_rate = (r_pct / Fraction(100)) / Fraction(4)
        end_bal = P * ((1 + q_rate) ** int(4 * n_yr))
        return {"quarterly_rate_trace": q_rate, "ending_balance_trace": end_bal}, end_bal - P

    if tid == "fp.investment_analysis.irr.bond_coupon_reinvestment.intermediate.v1":
        # NUMS0: ['7142', '0', '10000', '4', '3', '10000']
        price, par, c_pct, reinv_pct = v[0], v[2], v[3], v[4]
        semi_c = par * (c_pct / Fraction(100)) / Fraction(2)
        reinv_c = semi_c * (1 + (reinv_pct / Fraction(100)) / Fraction(2))
        term_cash = par + semi_c + reinv_c
        irr_pct = (term_cash / price - 1) * Fraction(100)
        return {"semiannual_coupon_trace": semi_c, "reinvested_first_coupon_trace": reinv_c, "terminal_cash_trace": term_cash}, irr_pct

    if tid == "fp.investment_analysis.irr.six_month_after_tax_net_sale.advanced.v1":
        # NUMS0: ['10000', '0', '20000', '500', '20']
        cost, sale_p, sell_cost, tax_pct = v[0], v[2], v[3], v[4]
        net_sale = sale_p - sell_cost
        gain = max(Fraction(0), net_sale - cost)
        tax = gain * (tax_pct / Fraction(100))
        at_proc = net_sale - tax
        mult6 = at_proc / cost
        irr_pct = (mult6 ** 2 - 1) * Fraction(100)
        return {"net_sale_proceeds_trace": net_sale, "after_tax_proceeds_trace": at_proc, "six_month_gross_multiple_trace": mult6}, irr_pct

    if tid == "fp.investment_analysis.npv.four_year_annuity_salvage_npv.intermediate.v1":
        # NUMS0: ['6250', '1265', '550', '0']
        I0, C, S, r_pct = v[0], v[1], v[2], v[3]
        y = 1 + r_pct / Fraction(100)
        y4_tot = C + S
        pv4 = y4_tot / (y ** 4)
        tot_pv = C / y + C / (y ** 2) + C / (y ** 3) + pv4
        return {"year_four_total_trace": y4_tot, "pv_year_four_trace": pv4, "total_pv_trace": tot_pv}, tot_pv - I0

    if tid == "fp.investment_analysis.npv.four_year_cleanup_npv.advanced.v1":
        # NUMS0: ['8300', '1845', '1955', '2165', '2375', '440', '0']
        I0, C1, C2, C3, C4, L, r_pct = v[0], v[1], v[2], v[3], v[4], v[5], v[6]
        y = 1 + r_pct / Fraction(100)
        gross_pv = C1 / y + C2 / (y ** 2) + C3 / (y ** 3) + C4 / (y ** 4)
        pv_clean = L / (y ** 4)
        after_init = gross_pv - I0
        return {"gross_pv_trace": gross_pv, "pv_cleanup_trace": pv_clean, "after_initial_trace": after_init}, after_init - pv_clean

    if tid == "fp.investment_analysis.npv.three_year_salvage_npv.intermediate.v1":
        # NUMS0: ['5200', '740', '955', '1170', '335', '0', '1']
        I0, C1, C2, C3, S, r_pct = v[0], v[1], v[2], v[3], v[4], v[5]
        y = 1 + r_pct / Fraction(100)
        term_cf = C3 + S
        pv3 = term_cf / (y ** 3)
        tot_pv = C1 / y + C2 / (y ** 2) + pv3
        return {"terminal_cash_flow_trace": term_cf, "pv_three_trace": pv3, "total_pv_trace": tot_pv}, tot_pv - I0

    if tid == "fp.investment_analysis.rar.three_asset_capm_portfolio.advanced.v1":
        # NUMS0: ['1100', '-1', '1580', '1/2', '2060', '3/2', '3', '8']
        vA, bA, vB, bB, vC, bC, rf, rm = v[0], v[1], v[2], v[3], v[4], v[5], v[6], v[7]
        tot_v = vA + vB + vC
        bp = (vA * bA + vB * bB + vC * bC) / tot_v
        mrp = rm - rf
        return {"total_value_trace": tot_v, "portfolio_beta_trace": bp, "market_premium_trace": mrp}, rf + bp * mrp

    if tid == "fp.investment_analysis.rar.two_asset_perfect_correlation_sd.basic.v1":
        # NUMS0: ['1', '0', '6', '100', '24', '100', '2']
        wA, sA, wB, sB = v[1], v[2], v[3], v[4]
        cA = wA * sA / Fraction(100)
        cB = wB * sB / Fraction(100)
        sd = cA + cB
        return {"weighted_sd_a_trace": cA, "weighted_sd_b_trace": cB, "variance_trace": sd ** 2}, sd

    if tid == "fp.investment_analysis.roi.mutual_fund_total_roi.advanced.v1":
        # NUMS0: ['55', '21', '17', '1', '2', '0', '100']
        sh, p_buy, p_sell, div_ps, yrs, fee_pct = v[0], v[1], v[2], v[3], v[4], v[5]
        init_inv = sh * p_buy
        proceeds = sh * p_sell
        tot_div = sh * div_ps * yrs
        tot_fees = init_inv * (fee_pct / Fraction(100)) * yrs
        net_prof = proceeds - init_inv + tot_div - tot_fees
        return {"total_dividends_trace": tot_div, "total_fees_trace": tot_fees, "net_profit_trace": net_prof}, net_prof * Fraction(100) / init_inv

    if tid == "fp.mergers_and_acquisitions.deal_structure.control_premium_debt_earnout_calculation.advanced.v1":
        # NUMS0: ['50000000', '10', '5000000', '50', '20']
        base_p, cp_pct, max_eo, ach_pct, debt_pct = v[0], v[1], v[2], v[3], v[4]
        cp_amt = base_p * (cp_pct / Fraction(100))
        pror_eo = max_eo * (ach_pct / Fraction(100))
        tot_cons = base_p + cp_amt + pror_eo
        eq_contrib = tot_cons * (1 - debt_pct / Fraction(100))
        return {"trace_1": cp_amt, "trace_2": tot_cons}, eq_contrib

    if tid == "fp.mergers_and_acquisitions.deal_structure.earnout_with_bonus_calculation.intermediate.v1":
        # NUMS0: ['20000000', '10000000', '100000000', '80000000', '5', '2000000', '110']
        base_p, max_eo, targ_rev, act_rev, bon_r, bon_cap, thresh_pct = v[0], v[1], v[2], v[3], v[4], v[5], v[6]
        basic_eo = min(max_eo, max_eo * act_rev / targ_rev)
        thresh = targ_rev * (thresh_pct / Fraction(100))
        excess = max(Fraction(0), act_rev - thresh)
        bonus = min(bon_cap, excess * (bon_r / Fraction(100)))
        return {"trace_1": basic_eo, "trace_2": bonus}, base_p + basic_eo + bonus

    if tid == "fp.mergers_and_acquisitions.deal_structure.leveraged_buyout_adjusted_shares_calculation.intermediate.v1":
        # NUMS0: ['50000000', '20', '500000', '2000000', '21/20']
        deal_v, debt_pct, sh_p, thresh_p, mult = v[0], v[1], v[2], v[3], v[4]
        eq_val = deal_v * (1 - debt_pct / Fraction(100))
        basic_sh = eq_val / sh_p
        adj_sh = basic_sh * mult if sh_p < thresh_p else basic_sh
        return {"trace_1": eq_val, "trace_2": basic_sh}, adj_sh

    if tid == "fp.mergers_and_acquisitions.due_diligence.due_diligence_dcf_valuation.advanced.v1":
        # NUMS0: ['-1', '200000', '3', '2', '5', '10', '2', '1', '5', '-1', '1', '5', '5']
        fcf1, g_pct, r_pct, gt_pct = v[1], v[2], v[5], v[6]
        g = g_pct / Fraction(100)
        r = r_pct / Fraction(100)
        gt = gt_pct / Fraction(100)
        fcfs = [fcf1 * ((1 + g) ** (t - 1)) for t in range(1, 6)]
        fcf5 = fcfs[4]
        tv5 = fcf5 * (1 + gt) / (r - gt)
        ev = sum(fcfs[t - 1] / ((1 + r) ** t) for t in range(1, 6)) + tv5 / ((1 + r) ** 5)
        return {"trace_1": fcf5, "trace_2": tv5}, ev

    if tid == "fp.mergers_and_acquisitions.post-merger_integration.supply_chain_npv_net_benefit.advanced.v1":
        # NUMS0: ['300', '350', '8', '3', '5', '50', '3', '4', '5', '1']
        sp1, sp2, red_pct, horiz, r_pct, int_cost = v[0], v[1], v[2], v[3], v[4], v[5]
        ann_sav = (sp1 + sp2) * (red_pct / Fraction(100))
        y = 1 + r_pct / Fraction(100)
        npv_sav = sum(ann_sav / (y ** t) for t in range(1, int(horiz) + 1))
        return {"trace_1": ann_sav, "trace_2": npv_sav}, npv_sav - int_cost

    if tid == "fp.mergers_and_acquisitions.valuation_methods.dcf_3yr_gordon_to_equity.advanced.v1":
        # NUMS0: ['1', '3', '17/2', '19/2', '21/2', '8', '2', '45', '6', '3', '-3']
        f1, f2, f3, r_pct, gt_pct, debt, cash = v[2], v[3], v[4], v[5], v[6], v[7], v[8]
        r, gt = r_pct / Fraction(100), gt_pct / Fraction(100)
        y = 1 + r
        tv3 = f3 * (1 + gt) / (r - gt)
        ev = f1 / y + f2 / (y ** 2) + f3 / (y ** 3) + tv3 / (y ** 3)
        return {"trace_1": tv3, "trace_2": ev}, ev - (debt - cash)

    if tid == "fp.mergers_and_acquisitions.valuation_methods.dcf_three_year_terminal_to_equity.intermediate.v1":
        # NUMS0: ['1', '3', '8', '9', '10', '8', '2', '40', '5', '3', '-3']
        f1, f2, f3, r_pct, gt_pct, debt, cash = v[2], v[3], v[4], v[5], v[6], v[7], v[8]
        r, gt = r_pct / Fraction(100), gt_pct / Fraction(100)
        y = 1 + r
        pv_exp = f1 / y + f2 / (y ** 2) + f3 / (y ** 3)
        tv3 = f3 * (1 + gt) / (r - gt)
        pv_tv = tv3 / (y ** 3)
        return {"trace_1": pv_exp, "trace_2": pv_tv}, pv_exp + pv_tv - debt + cash

    if tid == "fp.personal_finance.budgeting.long_term_growth.advanced.v1":
        # NUMS0: ['1000', '0', '1']
        b0, g_r, n_yr = v[0], v[1], v[2]
        gf = 1 + g_r
        cm = gf ** int(n_yr)
        return {"growth_factor": gf, "compounded_multiple": cm}, b0 * cm

    if tid == "fp.personal_finance.loanrepay.early_payoff.advanced.v1":
        # NUMS0: ['1000', '0', '0', '999']
        bal, acc_int, pen_r, cash = v[0], v[1], v[2], v[3]
        waived = "penalty-waived flag is true" in ql
        eff_pen = Fraction(0) if waived else bal * pen_r
        due = bal + acc_int + eff_pen
        surplus = cash - due
        return {"effective_penalty_usd": eff_pen, "payoff_due_usd": due, "cash_surplus_usd": surplus}, b_str(surplus >= 0)

    if tid == "fp.personal_finance.personalinvest.compound_growth.basic.v1":
        # NUMS0: ['1000', '0', '1']
        P, r, n = v[0], v[1], v[2]
        pf = 1 + r
        mult = pf ** int(n)
        return {"period_growth_factor": pf, "compounded_multiple": mult}, P * mult

    if tid == "fp.personal_finance.personalinvest.diversification_risk.advanced.v1":
        # NUMS0: ['1/2', '1/2', '4', '6', '2', '3/5']
        wA, wB, rA, rB, pen, thresh = v[0], v[1], v[2], v[3], v[4], v[5]
        base = wA * rA + wB * rB
        conc = max(wA, wB) >= thresh
        app_pen = pen if conc else Fraction(0)
        return {"base_risk_score": base, "concentration_condition": b_str(conc), "applied_penalty_points": app_pen}, base + app_pen

    if tid == "fp.personal_finance.saveretire.additional_saving.basic.v1":
        target, cur, ann_sav, yrs = v[0], v[1], v[2], v[3]
        proj = cur + ann_sav * yrs
        shortfall = max(Fraction(0), target - proj)
        return {"projected_available_usd": proj, "shortfall_usd": shortfall}, shortfall / yrs

    if tid == "fp.personal_finance.saveretire.early_retirement_bridge.advanced.v1":
        # NUMS0: ['1000', '100', '10', '0', '0']
        sav, spend, yrs, inc, cont_r = v[0], v[1], v[2], v[3], v[4]
        net_need = max(Fraction(0), spend - inc)
        base_need = net_need * yrs
        req_cap = base_need * (1 + cont_r)
        gap = req_cap - sav
        return {"net_annual_need": net_need, "required_capital_usd": req_cap, "funding_gap_usd": gap}, b_str(sav >= req_cap)

    if tid == "fp.personal_finance.saveretire.inflation_adjustment.intermediate.v1":
        spend, inf_r, n = v[0], v[1], v[2]
        inf_f = 1 + inf_r
        inf_m = inf_f ** int(n)
        return {"inflation_factor": inf_f, "inflation_multiple": inf_m}, spend * inf_m

    if tid == "fp.personal_finance.taxcalc.foreign_tax_relief.advanced.v1":
        inc, dom_r, paid, cap_r = v[0], v[1], v[2], v[3]
        dom_tax = inc * dom_r
        allow = min(paid, dom_tax * cap_r)
        return {"domestic_tax_before_relief_usd": dom_tax, "allowed_credit_usd": allow}, max(Fraction(0), dom_tax - allow)

    if tid == "fp.risk_management.regulatory_compliance.multi_factor_regulatory_compliance.advanced.v1":
        E, T, r, C, M, A, Q = v[0], v[1], v[2], v[3], v[4], v[5], v[6]
        pen = max(Fraction(0), E - T) * (r / Fraction(100))
        short = max(Fraction(0), M - C)
        gap = max(Fraction(0), Q - A)
        return {"penalty_trace": pen, "shortfall_trace": short, "gap_trace": gap}, pen + short + gap

    if tid == "fp.risk_management.risk_metrics.multi_factor_portfolio.advanced.v1":
        V, w1, w2, w3, c1, c2, c3, s1, s2, s3 = v[0], v[2], v[4], v[6], v[9], v[11], v[13], v[15], v[17], v[19]
        i1 = V * (w1 / Fraction(100)) * (c1 / Fraction(100)) * s1
        i2 = V * (w2 / Fraction(100)) * (c2 / Fraction(100)) * s2
        i3 = V * (w3 / Fraction(100)) * (c3 / Fraction(100)) * s3
        return {"impact_one_trace": i1, "impact_two_trace": i2, "impact_three_trace": i3}, i1 + i2 + i3

    if tid == "fp.risk_management.scenario_planning.investment_scenario_planning.advanced.v1":
        V, cm, ci, cf, sm, si, sf = v[0], v[1], v[2], v[3], v[4], v[5], v[6]
        em, ei, ef = sm * cm / Fraction(100), si * ci / Fraction(100), sf * cf / Fraction(100)
        return {"market_effect_trace": em, "interest_effect_trace": ei, "inflation_effect_trace": ef}, V * (em + ei + ef)

    if tid in (
        "fp.risk_management.sensitivity_analysis.multi_asset_portfolio.intermediate.v1",
        "fp.risk_management.stress_testing.multi_asset_portfolio.intermediate.v1",
    ):
        V, w1, w2, w3, s1, s2, s3, c = v[0], v[2], v[4], v[6], v[9], v[11], v[13], v[14]
        S = (w1 * s1 + w2 * s2 + w3 * s3) / Fraction(100)
        fr = c / Fraction(100)
        return {"weighted_sensitivity_trace": S, "factor_ratio_trace": fr}, V * fr * S

    if tid == "fp.risk_management.sensitivity_analysis.multi_factor_portfolio.advanced.v1":
        V, ci, cm, cc, si, sm, sc = v[0], v[1], v[2], v[3], v[4], v[5], v[6]
        ei, em, ec = si * ci / Fraction(100), sm * cm / Fraction(100), sc * cc / Fraction(100)
        return {"interest_effect_trace": ei, "market_effect_trace": em, "credit_effect_trace": ec}, V * (ei + em + ec)

    if tid == "fp.risk_management.var.multi_asset.intermediate.v1":
        V, w1, w2, w3, s1, s2, s3, t, c = v[0], v[2], v[4], v[6], v[8], v[10], v[12], v[13], v[14]
        S = (w1 * s1 + w2 * s2 + w3 * s3) / Fraction(100)
        wr = S / Fraction(100)
        m = 1 + (100 - c) / Fraction(100)
        return {"weighted_volatility_trace": S, "weighted_ratio_trace": wr, "confidence_multiplier_trace": m}, V * wr * t * m

    if tid == "fp.risk_management.var.multi_factor.advanced.v1":
        V, a, b, q_val, t, c = v[0], v[1], v[2], v[3], v[4], v[5]
        R = (a + b + q_val) / Fraction(3)
        m = 1 + (100 - c) / Fraction(100)
        return {"combined_risk_trace": R, "confidence_multiplier_trace": m}, V * (R / Fraction(100)) * t * m

    if tid == "fp.risk_management.var.single_asset.basic.v1":
        V, s, t, c = v[0], v[1], v[2], v[3]
        vr = s / Fraction(100)
        m = 1 + (100 - c) / Fraction(100)
        return {"volatility_ratio_trace": vr, "confidence_multiplier_trace": m}, V * vr * t * m

    if tid == "fp.sustainable_finance.carbon_credits.comprehensive_strategy.advanced.v1":
        inv, base_p, disc_pct, target, prem_pct, rebate = v[0], v[3], v[6], v[9], v[13], v[16]
        disc_p = base_p * (1 - disc_pct / Fraction(100))
        cred = inv / disc_p
        surplus = max(Fraction(0), cred - target)
        rev = surplus * disc_p * (1 + prem_pct / Fraction(100))
        return {"discounted_price_trace": disc_p, "credits_purchased_trace": cred, "surplus_credits_trace": surplus}, rev + rebate - inv

    if tid == "fp.sustainable_finance.carbon_credits.credit_rebate.basic.v1":
        I, P, r_rate, T = v[0], v[3], v[6], v[9]
        Q = I / P
        elig = Q * r_rate
        return {"credits_purchased_trace": Q, "eligible_rebate_trace": elig}, (elig if Q > T else Fraction(0))

    if tid == "fp.sustainable_finance.carbon_credits.multi_company_synergy.intermediate.v1":
        c1, c2, P, disc_pct, T = v[1], v[4], v[8], v[11], v[14]
        tot_cred = c1 + c2
        gross = tot_cred * P
        disc_cost = gross * (1 - disc_pct / Fraction(100))
        return {"total_credits_trace": tot_cred, "gross_cost_trace": gross, "discounted_cost_trace": disc_cost}, (disc_cost if tot_cred > T else gross)

    if tid == "fp.sustainable_finance.esg_investing.multi_factor_synergy.advanced.v1":
        init_cost, save_m, tax_cred, op_cost, eff_pct, yrs = v[0], v[3], v[6], v[9], v[12], v[15]
        ann_en = save_m * 12
        ann_eff = op_cost * (eff_pct / Fraction(100))
        tot_sav = yrs * (ann_en + ann_eff + tax_cred)
        return {"annual_energy_savings_trace": ann_en, "annual_efficiency_savings_trace": ann_eff, "total_savings_trace": tot_sav}, tot_sav - init_cost

    if tid == "fp.sustainable_finance.esg_investing.project_roi.intermediate.v1":
        init_inv, save_m, op_cost, cred_yr, yrs = v[0], v[3], v[6], v[9], v[12]
        ann_net = save_m * 12 - op_cost + cred_yr
        tot_net = ann_net * yrs
        roi_r = tot_net / init_inv
        return {"annual_net_savings_trace": ann_net, "total_net_savings_trace": tot_net, "roi_ratio_trace": roi_r}, roi_r * Fraction(100)

    if tid == "fp.sustainable_finance.green_bonds.comprehensive_analysis.advanced.v1":
        P, r_pct, n_yr, tc_pct, sav_yr, bonus_per_blk, blk_sz, reinv_pct, reinv_r_pct = (
            v[0], v[3], v[6], v[9], v[12], v[15], v[16], v[19], v[22]
        )
        ny = int(n_yr)
        interest = P * ((1 + r_pct / Fraction(100)) ** ny - 1)
        tc = interest * (tc_pct / Fraction(100))
        tot_bonus = n_yr * (sav_yr / blk_sz) * bonus_per_blk
        ann_reinv = (interest / n_yr) * (reinv_pct / Fraction(100))
        g_reinv = 1 + reinv_r_pct / Fraction(100)
        reinv_contrib = sum(ann_reinv * (g_reinv ** m) for m in range(ny))
        return {
            "interest_earned_trace": interest,
            "total_bonus_trace": tot_bonus,
            "reinvestment_contribution_trace": reinv_contrib,
        }, interest + tc + tot_bonus + reinv_contrib

    return None

def solve_seen_question(tid, q_obj):
    q_text = q_obj["question"]
    res = solve_explicit_seen(tid, q_text)
    if res is not None:
        raw_slots, raw_final = res
    elif tid in SYNTH_CACHE:
        entry = SYNTH_CACHE[tid]
        raw_nums = ts.extract_numbers(q_text)
        var_indices = entry["var_indices"]
        v = [raw_nums[i] for i in var_indices] if var_indices is not None else list(raw_nums)
        raw_slots = {}
        env = {"v": v, "Fraction": Fraction, "min": min, "max": max, "abs": abs, "int": int}
        for sid, expr_str in entry["steps"]:
            val = eval(expr_str, {"__builtins__": {}}, env)
            raw_slots[sid] = val
            v.append(val)
        raw_final = eval(entry["final"], {"__builtins__": {}}, env)
    else:
        raise ValueError(f"Unknown seen template: {tid}")

    steps_out = []
    for slot in sorted(q_obj["trace_spec"]["slots"], key=lambda s: s["position"]):
        sid = slot["slot_id"]
        spec = slot["result_spec"]
        steps_out.append({
            "slot_id": sid,
            "value": ts.format_value(raw_slots[sid], spec)
        })
    final_str = ts.format_value(raw_final, q_obj["answer_spec"])
    return {
        "schema_version": "finreason.task1.prediction/1.0.0",
        "dataset_version": q_obj["dataset_version"],
        "case_id": q_obj["case_id"],
        "final_answer": {"value": final_str},
        "steps": steps_out,
    }

if __name__ == "__main__":
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
                print(f"TRAIN MISMATCH on {tid} ({q['case_id']}): pred={pred} vs gold={g}")
                break

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
            print(f"DEV MISMATCH on {tid} ({q['case_id']}): pred={pred} vs gold={g}")

    print(f"TRAIN EXACT MATCH: {train_ok} / {train_total}")
    print(f"DEV EXACT MATCH:   {dev_ok} / {dev_total}")
