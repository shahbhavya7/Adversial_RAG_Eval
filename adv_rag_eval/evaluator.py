import json
from huggingface_hub import hf_hub_download
from llama_cpp import Llama

# Global variable to keep the model loaded in RAM/VRAM between function calls
_judge_model = None

def _get_model():
    global _judge_model
    if _judge_model is None:
        print("Checking for Grounding Judge model...")
        print("If this is your first time, it will download the 4.9GB model. Please wait...")
        
        # 1. Automatically download and cache the .gguf file from Hugging Face
        # (Note: You must upload your file to Hugging Face and replace this repo_id)
        model_path = hf_hub_download(
            repo_id="bhavyashah7/adv-rag-judge", 
            filename="grounding_judge_model.gguf"
        )
        
        print("Booting up the inference engine...")
        
        # 2. Load the model directly into Python (offloads to GPU if available)
        _judge_model = Llama(
            model_path=model_path,
            n_gpu_layers=-1, # Automatically uses the user's GPU (like your RTX 3050)
            n_ctx=2048,
            verbose=False    # Keeps the terminal output clean
        )
    return _judge_model

def evaluate_answer(context: str, generated_answer: str) -> dict:
    """
    Evaluates a RAG-generated answer against its source context to detect hallucinations.
    """
    model = _get_model()
    
    # 3. Hardcode the strict Llama-3 Instruct formatting
    system_prompt = "You are an expert RAG Evaluator. Given a context and a generated answer, output a JSON object evaluating the faithfulness of the answer. It must contain 'hallucination_detected' (bool), 'error_type' (string or null), and 'reasoning' (string)."
    user_prompt = f"Context:\n{context}\n\nGenerated Answer:\n{generated_answer}"
    
    formatted_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

{system_prompt}<|eot_id|><|start_header_id|>user<|end_header_id|>

{user_prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""

    try:
        # 4. Generate the response directly in Python
        output = model(
            formatted_prompt,
            max_tokens=128,
            stop=["<|eot_id|>"],
            temperature=0.1
        )
        
        raw_text = output['choices'][0]['text'].strip()
        
        # 5. Parse and return the JSON
        evaluation = json.loads(raw_text)
        return evaluation
        
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON. Model output drifted."}
    except Exception as e:
        return {"error": f"Inference failed: {str(e)}"}