import requests
import json

# Your Live Cloud Engine
API_URL = "http://adv-rag-eval-bhavya.eastus.azurecontainer.io:8000/evaluate"
API_KEY = "sk-adv-rag-eval-enterprise-777"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Simulating a company's RAG Pipeline outputs
rag_tests = [
    {
        "scenario": "✅ Case 1: The Perfect Match",
        "retrieved_context": "The company Q3 earnings report states that revenue grew by 12% to $1.4 billion. The growth was primarily driven by the enterprise software division.",
        "llm_answer": "In Q3, the company saw a 12% revenue increase, reaching $1.4 billion, largely thanks to their enterprise software division."
    },
    {
        "scenario": "🚨 Case 2: The Sneaky Hallucination (Feature Addition)",
        "retrieved_context": "The new Sentinel X smartwatch features heart rate tracking, a 3-day battery life, and water resistance up to 50 meters. It retails for $249.",
        "llm_answer": "The Sentinel X is a $249 smartwatch that tracks your heart rate, has a 3-day battery, and includes built-in GPS for running."
    }
]

print("🚀 Starting Enterprise RAG Evaluation Test...\n")

for test in rag_tests:
    print(f"Running {test['scenario']}...")
    
    # Construct the exact JSON your API expects
    payload = {
        "context": test["retrieved_context"],
        "answer": test["llm_answer"]
    }
    
    try:
        # Pinging your Azure Cloud!
        response = requests.post(API_URL, json=payload, headers=headers)
        
        if response.status_code == 200:
            result = response.json()
            # Print the formatted JSON response from your engine
            print(json.dumps(result, indent=2))
        else:
            print(f"Failed! Status Code: {response.status_code}")
            print(response.text)
            
    except Exception as e:
        print(f"Connection Error: {e}")
        
    print("-" * 50 + "\n")