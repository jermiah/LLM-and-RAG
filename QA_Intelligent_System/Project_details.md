#  Skypher QA Intelligence System

##  Overview
Skypher is a robust Question Answering (QA) inference pipeline designed for cybersecurity and compliance domains. It intelligently answers standardized and custom security questionnaires using a combination of:
- Exact-match lookup
- Logistic regression classification
- Lexical (BM25) + semantic (FAISS) retrieval
- Cross-encoder reranking
- Controlled LLM-based answer generation

---

##  Problem Statement
The system must predict accurate answers to unseen compliance questions for a variety of user IDs. Responses must be contextually relevant and reliable, with strong support for personalization and avoiding hallucinations.

---

##  Dataset Details
- `training.json`: Nested dictionary of question-answer pairs with user_id.
- `test.csv`: Contains new `question` and `user_id` fields to predict answers for.
- ~258 training samples, 30 unique answers (class labels).

### Preprocessing
- Cleaned input by stripping whitespace, lowercasing, removing tags like "e.g.", and standardizing brackets.
- Used `json5` for loose syntax loading, then validated with custom scripts for structural integrity.

---

##  Exploratory Insights
- 41 test questions match training questions
- 7 test rows match both question and user_id →  perfect early exits
- Heavy class imbalance across answer labels
- Questions are short and templated

---

##  Architecture

###  Step 1: Exact Match
- High Confidence: Match on both `question_clean` and `user_id`
- Medium Confidence: Match on `question_clean` only

###  Step 2: Classification
- Model: `LogisticRegression(class_weight='balanced')`
- Embeddings: `BAAI/bge-large-en-v1.5`
- Features:
  - `question_only` for generic classifier
  - `question + [USER] user_id` for personalized classifier

###  Step 3: Lexical BM25
- Retrieves top-k similar questions from training corpus based on token overlap

###  Step 4: Dense Retrieval (FAISS)
- Embedding Model: `BAAI/bge-large-en-v1.5`
- Retrieval Variants:
  - `index_q_only` (semantic only)
  - `index_q_user` (personalized)

###  Step 5: Candidate Deduplication
- Combine classifier, BM25, and FAISS results
- Deduplicate (question, answer) pairs

###  Step 6: Cross-Encoder Reranking
- Model: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- Scores relevance between `test_question` and candidate questions

###  Step 7: LLM Answer Generation
- Model: `mistralai/Mistral-7B-Instruct-v0.3` (4-bit quantized)
- Prompt crafted with:
  - Top reranked Q/A pairs
  - Explicit instructions to avoid hallucination and stay under 45 words

---

##  Evaluation Methodology

### 1. Exact Match
- 7 user-personalized → high confidence
- 34 generic matches → medium confidence

### 2. Classifier Results
| Model Type | Features | Mean Accuracy | Macro F1 |
|------------|----------|----------------|----------|
| Generic    | question only | ~89% | ~0.82 |
| User-Aware| question + user_id | ~90% | ~0.84 |

### 3. LLM Evaluation
- Spot-checked for hallucination
- Reranked candidates only if score ≥ 1.0
- Prompt designed for factual, concise answers

---

## Improvements Achieved
-  Saved compute: 41/109 answered via exact match
-  Personalized predictions when user_id known
-  Reduced hallucinations via cross-encoder reranking

---

##  References & Tools

### Libraries
- `transformers`, `sentence-transformers`, `rank_bm25`, `faiss-cpu`, `scikit-learn`, `pandas`, `numpy`

### Models
- `BAAI/bge-large-en-v1.5` (Embedding)
- `cross-encoder/ms-marco-MiniLM-L-6-v2` (Reranker)
- `mistralai/Mistral-7B-Instruct-v0.3` (LLM Generator)

---

##  Future Enhancements
- Fine-tune LLMs on cybersecurity domain
- Add rejection classifier for ambiguous inputs
- Incorporate soft label validation (e.g., BERTScore)
- Integrate human-in-the-loop feedback


