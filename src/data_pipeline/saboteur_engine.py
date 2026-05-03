import asyncio
import json
import logging
import os
from datasets import load_dataset
from dotenv import load_dotenv
from typing import Literal

# Load environment variables from .env file
load_dotenv()

import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted, GoogleAPIError
from pydantic import BaseModel, ValidationError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------
class SaboteurOutput(BaseModel):
    original_context: str
    question: str
    answer: str
    reasoning: str 
    hallucination_detected: bool
    error_type: Literal["Entity Swap", "Numerical Drift", "Logical Negation", "None"]

# ---------------------------------------------------------------------------
# Prompts
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = """You are the Saboteur. Your goal is to generate a balanced dataset.
For every context, flip a coin:
- HEADS: Generate a CLEAN paraphrase. Set hallucination_detected=false and error_type='None'. Use sophisticated paraphrasing so the judge learns that different words do not mean a hallucination.
- TAILS: Generate a SABOTAGED mutation. Set hallucination_detected=true and inject exactly ONE of the following errors:
  1. "Entity Swap": Replace a key person, place, or organization with a plausible but incorrect alternative.
  2. "Numerical Drift": Change a key date, amount, percentage, or other number.
  3. "Logical Negation": Flip the meaning of a key sentence.

You MUST write the 'reasoning' field first, explaining exactly why the answer is either a faithful paraphrase or a hallucination.

Your output MUST be valid JSON matching the following schema:
{
  "reasoning": "Step-by-step logic",
  "original_context": "The exact original paragraph",
  "question": "A question that the original context answers",
  "answer": "The generated answer",
  "hallucination_detected": boolean,
  "error_type": "Entity Swap, Numerical Drift, Logical Negation, or None"
}

Do not include any other text, markdown formatting, or explanation. Only output the raw JSON object.
"""

# ---------------------------------------------------------------------------
# Core Engine
# ---------------------------------------------------------------------------
async def generate_sabotage_for_context(
    model: genai.GenerativeModel, 
    context: str, 
    semaphore: asyncio.Semaphore, 
    max_retries: int = 3
) -> SaboteurOutput | None:
    """Processes a single context string to generate a sabotaged record."""
    async with semaphore:
        for attempt in range(max_retries):
            try:
                prompt = f"Stochastically choose to generate a CLEAN or SABOTAGED output for this context:\n{context}"
                response = await model.generate_content_async(
                    prompt,
                    generation_config=genai.GenerationConfig(
                        response_mime_type="application/json",
                        temperature=0.85,
                    )
                )
                
                content = response.text
                if not content:
                    raise ValueError("Empty response from model")
                
                # Parse and validate with Pydantic
                data = json.loads(content)
                parsed_output = SaboteurOutput(**data)
                return parsed_output

            except ResourceExhausted as e:
                # Exponential backoff for rate limits
                wait_time = (2 ** attempt) + 1
                logger.warning(f"Rate limited. Retrying in {wait_time} seconds... ({e})")
                await asyncio.sleep(wait_time)
            except (GoogleAPIError, ValidationError, json.JSONDecodeError, ValueError) as e:
                logger.error(f"Error processing context (Attempt {attempt+1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    return None
                await asyncio.sleep(1)
        return None

async def generate_sabotage_data(contexts: list[str], output_path: str, concurrency_limit: int = 5):
    """Main generation loop that processes contexts concurrently."""
    # Note: Requires GEMINI_API_KEY environment variable to be set.
    # export GEMINI_API_KEY="your_key"
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        logger.error("GEMINI_API_KEY environment variable is not set. Please set it before running.")
        return

    # Configure Gemini API
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-3-flash-preview', system_instruction=SYSTEM_PROMPT)
    
    # Semaphore to limit concurrent API calls
    semaphore = asyncio.Semaphore(concurrency_limit)
    
    logger.info(f"Starting sabotage generation for {len(contexts)} contexts...")
    
    # Create tasks for all contexts
    tasks = [
        generate_sabotage_for_context(model, context, semaphore)
        for context in contexts
    ]
    
    # Ensure directory exists before saving
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Removed file clearing to allow appending for smart resume
    pass
    
    # Run tasks concurrently and stream results as they finish
    successful_count = 0
    for future in asyncio.as_completed(tasks):
        res = await future
        if res is not None:
            successful_count += 1
            # Append line-by-line so progress is visible immediately
            with open(output_path, "a", encoding="utf-8") as f:
                f.write(res.model_dump_json() + "\n")
            
    logger.info(f"Successfully generated {successful_count} out of {len(contexts)} samples.")
    logger.info(f"Dataset successfully saved to {output_path}")

# ---------------------------------------------------------------------------
# Initialization / Testing
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Ensure dependencies are installed before running:
    # pip install google-generativeai pydantic pandas datasets
    
    # Use absolute path for output
    output_file = os.path.join(os.path.dirname(__file__), "..", "..", "data", "raw", "saboteur_dataset.jsonl")
    output_file = os.path.abspath(output_file)

    # Smart Resume (Checkpointing)
    processed_contexts = set()
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        record = json.loads(line)
                        if "original_context" in record:
                            processed_contexts.add(record["original_context"])
                    except json.JSONDecodeError:
                        pass
    
    logger.info(f"Found {len(processed_contexts)} already processed contexts.")
    
    # Load the SQuAD dataset
    logger.info("Loading SQuAD dataset...")
    squad = load_dataset('squad', split='train')
    
    # Extract and deduplicate contexts, filtering out already processed ones
    unique_contexts = []
    seen = set()
    for ctx in squad['context']:
        if ctx not in seen and ctx not in processed_contexts:
            seen.add(ctx)
            unique_contexts.append(ctx)
            
    target_total = 1000
    remaining_needed = target_total - len(processed_contexts)
    
    if remaining_needed <= 0:
        logger.info(f"Target of {target_total} records already met. Nothing to do.")
    else:
        # Slice to the exact remaining number needed
        test_contexts = unique_contexts[:remaining_needed]
        logger.info(f"Selected {len(test_contexts)} new contexts for sabotage to reach target of {target_total}.")
        
        # Run the async generation loop with safe concurrency
        asyncio.run(generate_sabotage_data(test_contexts, output_file, concurrency_limit=3))
