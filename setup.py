from setuptools import setup, find_packages
from pathlib import Path

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='adv-rag-eval',
    version='0.1.2',
    packages=find_packages(),
    install_requires=[
        'llama-cpp-python>=0.2.56',
        'huggingface-hub>=0.20.0'
    ],
    author='Bhavya Shah',
    description='A standalone, zero-cost RAG hallucination evaluator.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    python_requires='>=3.8',
)