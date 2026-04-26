# Adversarial RAG Evaluator (adv-rag-eval)

A fully local, zero-cost Python library to evaluate RAG pipelines for hallucinations. 
Powered by a custom fine-tuned Llama-3 model.

## Installation
`pip install adv-rag-eval`

## Usage
```python
from adv_rag_eval import evaluate_answer

result = evaluate_answer("Context here...", "Answer here...")
print(result)