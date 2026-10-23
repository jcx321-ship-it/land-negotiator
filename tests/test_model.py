import glob, json, os, unittest
from evaluator.engine import evaluate_offer
from evaluator.cashflow import irr_annual
from evaluator.gates import run_gates
from evaluator.protocols import residential_sale, rental, industrial_lots
from evaluator.protocols.base import summarize
from evaluator.criteria import TARGET_IRR_PRETAX

HERE = os.path.dirname(__file__)
def case(name): return json.load(open(os.path.join(HERE, "..", "cases", name), encoding="utf-8"))
def dev(name): return json.load(open(os.path.join(HERE, "..", "developers", name), encoding="utf-8"))
THESES = {"residential_sale": dev("dev1_residential.json"), "industrial_lots": dev("dev2_industrial.json"),
          "rental": dev("dev3_rental.json"), "commercial": dev("dev4_commercial.json")}


class Verdicts(unittest.TestCase):
    def test_expected_verdicts(self):
        exp = {"case_a_residential_go.json": "GO", "case_b_residential_no_go.json": "NO-GO",
               "case_c_residential_borderline.json": "BORDERLINE", "case_d_rental_premium.json": "GO",
               "case_e_industrial_lots.json": "GO", "case_f_land_banking.json": "NO AUTOMATIC VERDICT",
               "case_g_title_kill.json": "NO-GO (land)", "case_h_no_fit.json": "NO FIT",
               "case_i_commercial_proximity.json": "BORDERLINE"}
        for f, v in exp.items():
            c = case(f)
            self.assertEqual(evaluate_offer(c, THESES.get(c["vocation"]))["verdict"], v, f)


class FounderRules(unittest.TestCase):
    def test_solved_land_price_meets_hurdles(self):
        r = residential_sale.evaluate(case("case_a_residential_go.json")["params"])
        m = summarize(r["flows_at_supported"])
        self.assertGreaterEqual(m["irr"], TARGET_IRR_PRETAX - 1e-6)
        self.assertGreaterEqual(m["multiple"], 2.0 - 1e-6)
        for f, mod in [("case_d_rental_premium.json", rental), ("case_e_industrial_lots.json", industrial_lots)]:
            r = mod.evaluate(case(f)["params"])
            self.assertAlmostEqual(summarize(r["flows_at_supported"])["irr"], TARGET_IRR_PRETAX, places=3)

    def test_without_debt_only_the_20pct_irr_applies(self):
        p = {**case("case_a_residential_go.json")["params"], "debt": {"enabled": False}}
        r = residential_sale.evaluate(p)
        self.assertIsNone(r["min_multiple"])
        self.assertAlmostEqual(summarize(r["flows_at_supported"])["irr"], TARGET_IRR_PRETAX, places=3)

    def test_forward_sale_cap_beats_speculative_exit(self):
        p = case("case_d_rental_premium.json")["params"]
        signed = rental.evaluate(p)["supported_land_value"]
        spec = rental.evaluate({**p, "forward_sale": False})["supported_land_value"]
        self.assertGreater(signed, spec)

    def test_rental_reports_yield_on_cost_against_12pct(self):
        r = rental.evaluate(case("case_d_rental_premium.json")["params"])
        self.assertEqual(r["target_yield_on_cost"], 0.12)
        self.assertIn("land_at_target_yield", r)

    def test_stalled_market_discards_the_product(self):
        self.assertEqual(run_gates({"title_certain": True, "seller_can_transfer": True, "market_absorbs": False})["status"],
                         "NO-GO (this vocation)")

    def test_cost_comes_from_finishes_not_segment(self):
        self.assertEqual(residential_sale.hard_cost_m2({"structure": "mid_rise", "finish_level": "high", "amenities_cost_m2": 1500}), 16500)
        self.assertLess(residential_sale.hard_cost_m2({"finish_level": "basic"}), residential_sale.hard_cost_m2({"finish_level": "luxury"}))

    def test_max_bid_is_lower_of_A_and_B(self):
        r = evaluate_offer(case("case_a_residential_go.json"))
        self.assertEqual(r["max_bid"], min(r["value_A_project"], r["value_B_comparables"]))

    def test_asking_comparables_are_ignored(self):
        r = evaluate_offer(case("case_a_residential_go.json"))
        self.assertTrue(any("asking-price" in n for n in r["comparables_notes"]))

    def test_deferral_and_in_kind_increase_supported_value(self):
        r = residential_sale.evaluate(case("case_a_residential_go.json")["params"])
        self.assertGreater(r["structure_value"], 0)

    def test_title_uncertainty_kills_the_land(self):
        self.assertEqual(run_gates({"title_certain": False})["status"], "NO-GO (land)")

    def test_zoning_not_allowing_kills_only_the_vocation(self):
        self.assertEqual(run_gates({"title_certain": True, "seller_can_transfer": True,
                                    "current_zoning_allows_product": False})["status"], "NO-GO (this vocation)")

    def test_partial_protocols_never_invent_a_price(self):
        r = evaluate_offer(case("case_f_land_banking.json"))
        self.assertNotIn("max_bid", r)

    def test_irr_helper(self):
        self.assertAlmostEqual(irr_annual([-100] + [0] * 11 + [120]), 0.20, places=3)


if __name__ == "__main__":
    unittest.main()


class Commercial(unittest.TestCase):
    def test_only_binding_loi_identifies_the_user(self):
        from evaluator.protocols import commercial
        p = case("case_i_commercial_proximity.json")["params"]
        spec = commercial.evaluate(p)
        loi = commercial.evaluate({**p, "loi_binding": True})
        self.assertFalse(spec["user_identified"])
        self.assertTrue(loi["user_identified"])
        self.assertGreater(loi["supported_land_value"], spec["supported_land_value"])
        self.assertAlmostEqual(spec["exit_cap"], 0.12)

    def test_investor_target_irr_changes_land_value(self):
        from evaluator.protocols import commercial
        p = case("case_i_commercial_proximity.json")["params"]
        self.assertGreater(commercial.evaluate({**p, "target_irr": 0.15})["supported_land_value"],
                           commercial.evaluate({**p, "target_irr": 0.20})["supported_land_value"])

    def test_format_gates_kill_the_product(self):
        g = run_gates({"title_certain": True, "seller_can_transfer": True, "access_visibility": False}, "commercial")
        self.assertEqual(g["status"], "NO-GO (this vocation)")

    def test_risk_factors_are_evidence_not_numbers(self):
        from evaluator.protocols import commercial
        rf = commercial.evaluate(case("case_i_commercial_proximity.json")["params"])["risk_factors"]
        self.assertTrue(all(set(x) == {"factor", "direction", "evidence"} for x in rf))

    def test_exit_routes(self):
        from evaluator.protocols import commercial
        p = case("case_i_commercial_proximity.json")["params"]
        for route in ("stabilized_sale", "unit_sale", "hold"):
            self.assertIsNotNone(commercial.evaluate({**p, "exit_route": route})["supported_land_value"])


class Spanish(unittest.TestCase):
    def test_spanish_view_translates_reasons_but_not_verdicts(self):
        import webapi
        for f in ("case_a_residential_go.json", "case_i_commercial_proximity.json", "case_h_no_fit.json"):
            code, r = webapi.post("/api/evaluate", {"offer": case(f), "lang": "es", "use_ai": False})
            _, en = webapi.post("/api/evaluate", {"offer": case(f), "lang": "en", "use_ai": False})
            res, ref = r["result"], en["result"]
            self.assertEqual(res["verdict"], ref["verdict"])
            self.assertEqual(res.get("max_bid"), ref.get("max_bid"))
            for es_line, en_line in zip(res["reasons"], ref["reasons"]):
                self.assertNotEqual(es_line, en_line)
