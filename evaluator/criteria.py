"""The Founder's land-buying criteria, with provenance.

Every constant says where it comes from:
  CONFIRMED  = stated by the Founder in the 2026-10 interview (current doctrine)
  HISTORICAL = observed in past models; evidence, not doctrine
  HYPOTHESIS = proposed, pending the Founder's confirmation
Interview beats history when they differ.
"""

TARGET_IRR_PRETAX = 0.20          # CONFIRMED: in Mexico a purchase must support 20% IRR before taxes
IRR_BASIS = "equity, with debt when the financing switch is on"  # CONFIRMED 2026-10: for sale, thresholds are usually measured with debt
MIN_EQUITY_MULTIPLE = 2.0         # CONFIRMED: for sale, the deal must also return 2.0x the equity
RENTAL_TARGET_YIELD_ON_COST = 0.12  # CONFIRMED: develop for rent aiming at 12% NOI / total investment (land included)
RENTAL_SPECULATIVE_EXIT_CAP = 0.10  # CONFIRMED: without a signed buyer, assume a speculative exit at a 10% cap
# CONFIRMED: "the IRR must always aim at 20%": in rental the 12%/10% pair is the mechanism, the 20% IRR approves.
# CONFIRMED: the holding horizon is given by market absorption (lease-up), then sale at stabilization.
CONTINGENCY_PER_BLOCK = 0.05      # CONFIRMED: ~5% per cost block, never a duplicate global bucket
DECISION_PRETAX = True            # CONFIRMED: buy decision is taken before taxes

# CONFIRMED quick test (sale destination only): land / revenue
LAND_TO_REVENUE_BANDS = {"low": (0.05, 0.10), "reference": 0.20, "high": (0.20, 0.30)}
# CONFIRMED (2026-10-16): standard hard costs are ~40% of the sales value. Together with the HISTORICAL
# ~20% land / ~20% margin it closes the 20/40/20 quick test. A quick test, not a hurdle: the IRR approves.
HARD_COST_TO_SALES_STANDARD = 0.40
# CONFIRMED as the Founder's reference pro forma for for-sale projects (share of sales value, 2026-10-16).
# Validated against public references: 20% profit on sales value is the usual residual-appraisal standard.
PROFORMA_STANDARD = {"land": 0.20, "hard_costs": 0.40, "soft_and_sales_costs": 0.10, "finance": 0.05,
                     "contingency_and_other": 0.05, "margin": 0.20}
# HISTORICAL heuristic mentioned by the Founder, NOT a rule: ~20% land / ~40% costs / ~20% margin
RULE_20_40_20 = {"land": 0.20, "costs": 0.40, "margin": 0.20}

RULES = [
    ("CONFIRMED", "No certainty of title and power to transfer -> NO-GO."),
    ("CONFIRMED", "Underwrite on CURRENT zoning only; future density or rezoning is upside, never paid today."),
    ("CONFIRMED", "Do not buy avoidable risk: investigate, resolve, accredit, quantify or protect before exposure."),
    ("CONFIRMED", "Material community opposition able to stop execution -> NO-GO, even if legal and profitable."),
    ("CONFIRMED", "Remediable physical issue -> cost into the model (effective land cost = price + extraordinary cost); non-remediable -> kills that vocation, not necessarily the land."),
    ("CONFIRMED", "Each vocation has its own protocol; never force the residential model onto other land."),
    ("CONFIRMED", "Land is the unknown: every line item must fit proportionally; land price is solved to reach the required IRR."),
    ("CONFIRMED", "Maximum bid = the LOWER of (value supported by the project) and (similar land on offer nearby)."),
    ("CONFIRMED", "Defer as much of the land payment as possible; pay cash upfront only if structuring fails and the deal still works."),
    ("CONFIRMED", "Pay in kind as much as the seller accepts; units valued at a special price that passes on the saved sales commission."),
    ("CONFIRMED", "Sensitivities come from market evidence and are used to find the negotiation space; no arbitrary fixed stress."),
    ("CONFIRMED", "Product: current zoning first, then the market validates price and pace; slow absorption lowers the land price, no absorption (stalled product nearby) = no market = discard."),
    ("CONFIRMED", "No closed comparables in the zone -> widen to another zone similar in use, level and type."),
    ("CONFIRMED", "Bridge loan is lent on hard construction costs only; land and soft costs are equity."),
    ("CONFIRMED", "Standard hard construction costs are about 40% of the sales value (quick test, not a hurdle)."),
    ("CONFIRMED", "For sale: value from the sales projection; approve at 20% equity IRR AND 2.0x equity multiple, usually with debt."),
    ("CONFIRMED", "Rental: value from rent and NOI; target 12% yield on total cost, exit at the signed buyer's cap or a speculative 10%; the 20% IRR approves."),
    ("CONFIRMED", "Forward sale (binding letter of intent with an institutional buyer) fixes the exit cap; seek a higher yield on cost to keep the margin."),
    ("CONFIRMED", "Exit cap = market + entry cap + risk + liquidity; ramp-up modelled apart from stabilized operation."),
    ("CONFIRMED", "Prefer committed demand (pre-leasing) before building; borrow long if asset yield exceeds debt cost; no universal DSCR."),
    ("CONFIRMED", "Premium and irreplaceable -> keep and rent; replaceable -> develop, sell, recycle capital."),
    ("CONFIRMED", "Commercial: demand first, product second; potential demand is not economically viable demand."),
    ("CONFIRMED", "Commercial: the investor sets the target IRR (20% pre-tax is the development reference, not a floor); risk is weighed with evidence, never with automatic percentages."),
    ("CONFIRMED", "Commercial: a user is identified only with a binding letter of intent signed before paying for the land; a solid lease locks the rent and has an AAA tenant."),
    ("CONFIRMED", "Commercial exit: sell the stabilized asset at a standard 12% cap (lower for AAA / institutional), sell rental units to small investors, or hold and exit later."),
    ("HYPOTHESIS", "Supply gap + sufficient demand = opportunity; gap without demand = probably justified absence."),
    ("HYPOTHESIS", "Large tracts: vocation is a portfolio (driver + complementary + required amenities)."),
    ("HYPOTHESIS", "Only closed transactions count as comparables, never asking prices (observed in rental valuation)."),
]
