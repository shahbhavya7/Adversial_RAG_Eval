from setuptools import setup, find_packages

setup(
    name='adv-rag-eval',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'llama-cpp-python>=0.2.56',
        'huggingface-hub>=0.20.0'
    ],
    author='Bhavya Shah',
    description='A standalone, zero-cost RAG hallucination evaluator.',
    python_requires='>=3.8',
)