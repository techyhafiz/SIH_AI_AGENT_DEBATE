import sys, os

# Ensure UTF-8 stdout
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

HANDBOOK_PATH = r"c:\Users\mujaw\Downloads\SIH\SIH_GROUND_REALITY_HANDBOOK.md"

def verify():
    print("=== STARTING COMPREHENSIVE HANDBOOK VERIFICATION ===")
    with open(HANDBOOK_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    checks = []

    # 1. Sleep Schedule & Round 2 Window Check
    checks.append((
        "Sleep Schedule & Round 2 Window (01:00-04:00 AM All-Hands)",
        "01:00 - 04:00 (Hour 17-20) : ALL-HANDS BATTLE STATIONS" in content and
        "TL, Backend Lead, and ML Lead 100% ALERT AT DESK" in content and
        "22:30 - 01:00" in content and
        "04:15 - 06:45" in content and
        "4 Active at Desk" in content
    ))

    # 2. Caffeine & Red Phone Sentinel Protocol Check
    checks.append((
        "Caffeine Timing & Red Phone Sentinel Protocol",
        "Caffeine Pharmacokinetics Protocol" in content and
        "10:30 AM" in content and
        "Desk Sentinel \"Red Phone\" Emergency Paging Protocol" in content and
        "15-Minute Wake-up & Face-Wash Buffer" in content
    ))

    # 3. Facade / JSONB Shadow Schema Pattern Check
    checks.append((
        "Facade / JSONB Shadow Schema Pattern (PostgreSQL & FastAPI)",
        "Facade / JSONB Shadow Schema" in content and
        "CREATE TABLE subsidy_applications" in content and
        "metadata JSONB DEFAULT" in content and
        "idx_subsidy_metadata_gin ON subsidy_applications USING GIN (metadata)" in content and
        "class FractionalOwner(BaseModel)" in content and
        "class DAGApprovalStep(BaseModel)" in content
    ))

    # 4. Smartphone-as-Edge-Probe MQTT Gateway Check
    checks.append((
        "Smartphone-as-Edge-Probe MQTT Gateway Pattern",
        "Smartphone-as-Edge-Probe" in content and
        "eclipse-mosquitto:2.0-alpine" in content and
        "HTML5 Device Motion Sensor" in content and
        "devicemotion" in content
    ))

    # 5. Trunk-Based Micro-Branching & Feature Toggles Check
    checks.append((
        "Trunk-Based Micro-Branching Git Strategy (<90 min)",
        "TRUNK-BASED MICRO-BRANCHING LIFECYCLE (<90 MIN)" in content and
        "Short-Lived Micro-Branches (< 90 Minutes)" in content and
        "FEATURE_FLAGS" in content and
        "Forensic Git Audit Checklist" in content and
        "git shortlog -sn --all" in content
    ))

    # 6. UIDAI Offline Paperless e-KYC Check
    checks.append((
        "UIDAI Offline Paperless e-KYC (Statutory Compliance)",
        "UIDAI Offline Paperless e-KYC" in content and
        "4-digit Share Code" in content and
        "Aadhaar Regulations 2019 (Section 16A)" in content and
        "NEVER store raw 12-digit Aadhaar numbers" in content
    ))

    # 7. DPDP Act 2023 Architecture & Erasure Endpoints Check
    checks.append((
        "DPDP Act 2023 Electronic Consent Artefact & Erasure",
        "Electronic Consent Artefact" in content and
        "Purpose Limitation" in content and
        "/api/v1/privacy/consent/revoke" in content and
        "/api/v1/privacy/erasure-request" in content
    ))

    # 8. MeghRaj GI Cloud / SDC Bill of Materials (~Rs 12,500/mo) Check
    checks.append((
        "Itemized MeghRaj / SDC Monthly BOM (~12,500/mo)",
        "12,500/month" in content and
        "MeghRaj Tier-III Linux Compute Instances" in content and
        "Managed PostgreSQL / PostGIS DB Cluster" in content and
        "High-Throughput S3-Compatible Object Storage" in content
    ))

    # 9. Legacy NIC SOAP 1.2 / WS-Security Interoperability Proxy Check
    checks.append((
        "Legacy NIC SOAP 1.2 / WS-Security Interoperability Proxy",
        "NIC SOAP 1.2 / WS-Security Proxy Adapter" in content and
        "WSDL-compliant XSD" in content and
        "X.509 PKCS#7 Digital Signature" in content and
        "NIC 504 Gateway Timeouts" in content
    ))

    # 10. Docker Image Cache Tag Alignment Check
    checks.append((
        "Docker Cache Bundling (postgis/postgis:16-3.4-alpine)",
        "docker pull postgis/postgis:16-3.4-alpine" in content and
        "docker save -o sih_docker_images.tar postgis/postgis:16-3.4-alpine" in content
    ))

    # 11. MinIO Distroless Healthcheck Check
    checks.append((
        "MinIO Container Distroless Healthcheck (mc ready local)",
        'test: ["CMD-SHELL", "mc ready local || exit 1"]' in content
    ))

    # 12. AI Inference Service Overflow Bounding Check
    checks.append((
        "AI Inference Service Clipped Exponential Bounding",
        "z = np.clip(np.dot(self.weights, features) + self.bias, -60.0, 60.0)" in content
    ))

    # 13. Fast Batch Seeding Check
    checks.append((
        "Indian Demographic Seeder Batching (createMany)",
        "prisma.user.createMany" in content and
        "prisma.inspectionRecord.createMany" in content
    ))

    all_passed = True
    print("\n--- RESULTS MATRIX ---")
    for name, passed in checks:
        status = "[PASS]" if passed else "[FAIL]"
        print(f"{status} : {name}")
        if not passed:
            all_passed = False

    print("\n----------------------")
    print(f"Total Checks: {len(checks)}")
    print(f"Overall Result: {'ALL CHECKS PASSED!' if all_passed else 'SOME CHECKS FAILED'}")
    return all_passed

if __name__ == "__main__":
    verify()
