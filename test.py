import requests
import json
import time

API_URL = "http://adv-rag-eval-bhavya.eastus.azurecontainer.io:8000/evaluate"
HEADERS = {"Authorization": "Bearer sk-adv-rag-eval-enterprise-777"}

stress_cases = [
    {
        "name": "🏢 Case 7: The Legal Jargon Test",
        "context": "Pursuant to Section 4.2 of the Master Service Agreement, the Indemnification Clause shall only be triggered upon a breach of confidentiality exceeding $500,000 in damages.",
        "answer": "If you leak data and it costs $600,000, the indemnification clause kicks in.",
        "expected": "PASS (Supported)"
    },
    {
        "name": "📑 Case 8: The Table/List Format Test",
        "context": "Product Inventory: \n- SKU-101: 50 units\n- SKU-102: 15 units\n- SKU-103: 0 units (Out of stock)",
        "answer": "We currently have 50 units of SKU-101 and 15 units of SKU-103 available.",
        "expected": "FAIL (Entity Swap or Numerical Drift - SKU-103 is out of stock)"
    },
    {
        "name": "🔄 Case 9: The Date Flip",
        "context": "The conference was moved from July 15th to August 20th due to venue availability issues.",
        "answer": "The conference is happening on July 15th because the venue was available.",
        "expected": "FAIL (Direct Contradiction)"
    }
]

def run_stress_test():
    print("🚀 Starting Enterprise API Stress Test...\n")
    for case in stress_cases:
        print(f"Testing {case['name']}...")
        payload = {
            "context": case["context"],
            "answer": case["answer"]
        }
        
        start_time = time.time()
        response = requests.post(API_URL, json=payload, headers=HEADERS)
        latency = round(time.time() - start_time, 2)
        
        if response.status_code == 200:
            print(f"✅ Success ({latency}s)")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Failed: {response.status_code} - {response.text}")
        print("-" * 50)

if __name__ == "__main__":
    run_stress_test()