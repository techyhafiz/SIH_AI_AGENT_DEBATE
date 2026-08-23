import sys
import os

# Test importing and executing inference_service
sys.path.insert(0, r"c:\Users\mujaw\Downloads\SIH\.agents\auditor_1\code_tests")

try:
    from test_0 import app, evaluate_governance_risk, GovernanceInput, rule_based_fallback
    print("Successfully imported test_0.py (inference_service.py)")
    
    # Test Tier 3 fallback directly
    inp = GovernanceInput(
        record_id="SIH-2026-BH-10042",
        category="AGRICULTURE_SUBSIDY",
        claim_amount=150000.0,
        land_area_hectares=0.05,
        previous_disbursements_count=6,
        soil_moisture_index=0.45,
        elevation_meters=80.0
    )
    fb = rule_based_fallback(inp)
    print("Fallback result:", fb)
    assert fb["risk_category"] == "HIGH"
    assert fb["anomaly_detected"] is True
    print("ML Logic Verification PASSED.")
except Exception as e:
    print("Error during ML execution test:", e)
