# 🤖 LLMs and RAG Projects

This repository showcases intelligent NLP solutions that combine **Large Language Models (LLMs)** and **Retrieval-Augmented Generation (RAG)** for complex reasoning, personalized QA, and enterprise-grade applications.

---

##  Repository Structure

```plaintext
LLMs-RAG-Projects/
├── README.md                        # Project overview and documentation
├── QA_Intelligent_System/           #  Cybersecurity QA System 
│   ├── QA_Intelligent_System.ipynb  # End-to-end QA pipeline notebook
│   ├── training.json                # Cleaned and structured training data
│   ├── test.csv                     # Test questions with user_id
│   ├── predictions.csv              # Final LLM-generated answers
└── other_projects/                  #  Placeholder for future RAG/LLM projects
```
---

##  Projects

###  1. Skypher QA Intelligence System
A production-ready hybrid QA pipeline for security compliance automation.

**Use Case**: Answer standardized cybersecurity questionnaires with high precision and personalization.

**Key Highlights:**
- Exact match retrieval using question + user_id
- Logistic regression classification with BGE embeddings
- BM25 lexical search and dense retrieval (FAISS)
- Cross-encoder reranking with `MiniLM`
- LLM answer generation using `Mistral-7B-Instruct` (4-bit quantized)

**Architecture:**
- Fast early exit for known questions
- Personalized embeddings (`question + [USER] user_id`)
- Reranking before generation to reduce hallucination
- Controlled LLM outputs with max token, temperature, repetition constraints

**Evaluation:**
- ~41/109 test questions were answered via exact match (no compute)
- Remaining passed through classification, retrieval, reranking, and LLM
- Human and reranker-based validation ensured factual, concise output

 Read full project in [QA Intelligent System](./QA_Intelligent_System/Project_details.md)

---

##  Tech Stack
- **LLMs**: Mistral-7B (HF Transformers)
- **Embeddings**: BAAI/bge-large-en-v1.5
- **Reranker**: cross-encoder/ms-marco-MiniLM-L-6-v2
- **Retrieval**: FAISS (dense), BM25 (rank_bm25)
- **Modeling**: Scikit-learn (Logistic Regression)
- **Libraries**: pandas, numpy, sentence-transformers, transformers

---

##  Contributing
We welcome pull requests for:
- New LLM or RAG architectures
- Benchmarks on MTEB or custom QA sets
- UI demos with Gradio/Streamlit

---

##  License
This project is open-sourced under the MIT License.
