import os
import sys

TARGET_PATH = r"c:\Users\mujaw\Downloads\SIH\SIH_GROUND_REALITY_HANDBOOK.md"

def verify():
    with open(TARGET_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.splitlines()
    print(f"Total Lines: {len(lines)}")
    print(f"Total Chars: {len(content)}")

    # Check code fences
    fences = [l for l in lines if l.strip().startswith("```")]
    print(f"Total Code Fence Markers: {len(fences)}")
    if len(fences) % 2 != 0:
        print("ERROR: Unbalanced code fences!")
    else:
        print("PASS: Code fences are perfectly balanced!")

    key_phrases = [
        "EXECUTIVE SUMMARY & THE UNFILTERED REALITY OF SIH",
        "PART 1: PHASE 1 — PROBLEM STATEMENT SELECTION",
        "PART 2: PHASE 2 — CENTRAL PPT SHORTLISTING",
        "PART 3: PHASE 3 — PRE-HACKATHON PREPARATION",
        "PART 4: PHASE 4 — THE 36-HOUR NODAL CENTER BATTLEFIELD",
        "PART 5: ANATOMY OF WINS VS. LOSSES",
        "PART 6: ACTIONABLE ROLE-SPECIFIC TOOLKITS",
        "PART 7: POST-HACKATHON ROADMAP",
        "PART 8: COMPREHENSIVE MASTER FIELD CHECKLISTS",
        "docker-compose.yml",
        "apiClient.ts",
        "seed.ts",
        "inference_service.py",
        "THE 180-SECOND WINNING PITCH SCRIPT",
        "DPDP Act 2023",
        "Bhashini",
        "C4 LEVEL 2 CONTAINER ARCHITECTURE",
        "DATA FLOW DIAGRAM (DFD LEVEL 1)",
        "THE 4-STEP TACTICAL CURVEBALL RESPONSE PLAYBOOK",
        "THE 90-MINUTE ROTATIONAL SLEEP SHIFT PROTOCOL",
        "The 1080p OBS Screen Recording Safety Net Protocol",
        "The Anti-Tokenism Strategy",
        "THE 7 INSTANT-REJECTION \"TRASH-BIN\" RED FLAGS",
        "5-POINT \"IS IT A TRAP?\" PS FEASIBILITY AUDIT"
    ]

    all_passed = True
    for kp in key_phrases:
        if kp in content:
            print(f" [PASS] Found: '{kp}'")
        else:
            print(f" [FAIL] Missing: '{kp}'")
            all_passed = False

    if all_passed:
        print("\nALL VERIFICATION GATES PASSED PERFECTLY!")
    else:
        print("\nSOME VERIFICATION GATES FAILED.")

if __name__ == "__main__":
    verify()
