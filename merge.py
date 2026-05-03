import json
import random
import os

# 1. Dynamically locate the data/raw directory
current_dir = os.path.dirname(os.path.abspath(__file__))
if "src" in current_dir:
    raw_data_dir = os.path.join(current_dir, "..", "..", "data", "raw")
else:
    raw_data_dir = os.path.join(current_dir, "data", "raw")

# 2. Exact filenames
files_to_merge = [
    "saboteur_dataset.jsonl",            # The Old V1 Data
    "saboteur_dataset_v2 (6).jsonl",     # The Gemini Data
    "saboteur_dataset_v2 (7).jsonl",     # The Groq Data (Mostly Clean)
    "saboteur_dataset_v2_part2.jsonl"    # The Rest of the Groq Data
]

output_file = os.path.join(raw_data_dir, "final_antigravity_dataset.jsonl")

dataset = []
seen_contexts = set() 

def normalize_and_append(filepath):
    count = 0
    if not os.path.exists(filepath):
        print(f"⚠️ Could not find {filepath}. Skipping.")
        return 0
        
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip(): continue
            try:
                record = json.loads(line)
                
                # --- SCHEMA NORMALIZER ---
                # Fix the "Answer" key
                if "sabotaged_answer" in record:
                    record["answer"] = record.pop("sabotaged_answer")
                
                # Fix missing "hallucination_detected" (V1 was 100% hallucinations)
                if "hallucination_detected" not in record:
                    record["hallucination_detected"] = True
                    
                # Fix missing "reasoning"
                if "reasoning" not in record:
                    record["reasoning"] = f"Legacy V1 Data - Hallucination type: {record.get('error_type', 'Unknown')}."
                # -------------------------

                # Deduplication check
                if record['original_context'] not in seen_contexts:
                    seen_contexts.add(record['original_context'])
                    dataset.append(record)
                    count += 1
                    
            except json.JSONDecodeError:
                continue
    return count

# 3. Load and Normalize all datasets
print("Normalizing and Merging datasets from data/raw/ ...\n")
total_loaded = 0

for filename in files_to_merge:
    filepath = os.path.join(raw_data_dir, filename)
    count = normalize_and_append(filepath)
    print(f"Loaded and normalized {count} unique records from {filename}")
    total_loaded += count

# 4. Shuffle the dataset
random.seed(42) 
random.shuffle(dataset)

# 5. Save the final masterpiece
with open(output_file, 'w', encoding='utf-8') as f:
    for record in dataset:
        f.write(json.dumps(record) + '\n')

# 6. Calculate the Final Balance
total = len(dataset)
if total > 0:
    sabotaged = sum(1 for r in dataset if r.get('hallucination_detected') is True)
    clean = sum(1 for r in dataset if r.get('hallucination_detected') is False)

    print("\n" + "="*50)
    print(f"🚀 MERGE COMPLETE")
    print(f"Saved to: data/raw/final_antigravity_dataset.jsonl")
    print("="*50)
    print(f"Total Unique Records : {total}")
    print(f"Sabotaged (True)     : {sabotaged} ({round((sabotaged/total)*100, 1)}%)")
    print(f"Clean (False)        : {clean} ({round((clean/total)*100, 1)}%)")
    print("="*50)
else:
    print("\n⚠️ No records were loaded. Check your file paths.")