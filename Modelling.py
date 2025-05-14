import EDA_and_Cleaning as eda
import numpy as np
import pandas as pd
from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
from transformers import pipeline
import torch, gc

def get_exact_match_answer(test_question, test_user_id, train_df):
    # High confidence: match on both question and user_id
    personalized_match = train_df[
        (train_df['question_clean'] == test_question.strip()) &
        (train_df['user_id'] == test_user_id)
    ]
    if not personalized_match.empty:
        return personalized_match['answer'].values[0], "high"

    # Medium confidence: match only on question
    generic_match = train_df[
        (train_df['question_clean'] == test_question.strip())
    ]
    if not generic_match.empty:
        return generic_match['answer'].values[0], "medium"

    return None, "none"

def prepare_question_embedding(question, embedding_model, user_id=None):
    cleaned_q = eda.clean_question_text(question)
    
    parts = [cleaned_q]

    if user_id:
        parts.append(f"[USER] {user_id}")
    
    query = ' '.join(parts)
    embedding = embedding_model.encode([query], normalize_embeddings=True)
    return embedding

def get_user_aware_top_k_answers(df,test_question, test_user, 
                                 model_generic, model_user_specific, 
                                 embedding_model, label_encoder, k=5):
    # Use correct embedding and model based on user_id
    if test_user in df['user_id'].values:
        embedding = prepare_question_embedding(test_question, embedding_model, user_id=test_user)
        model = model_user_specific
    else:
        embedding = prepare_question_embedding(test_question, embedding_model, user_id=None)
        model = model_generic

    # Predict class probabilities
    probs = model.predict_proba(embedding)[0]
    top_k_indices = np.argsort(probs)[-k:][::-1]
    top_k_labels = label_encoder.inverse_transform(top_k_indices)

    # Get corresponding question-answer pairs for these labels
    question_answer_pairs = []
    for label in top_k_labels:
        matches = df[df['answer'] == label]
        if not matches.empty:
            # Just pick the first match (or customize this logic)
            q = matches.iloc[0]['question_clean']
            a = matches.iloc[0]['answer']
            question_answer_pairs.append((q, a))

    return question_answer_pairs


def dense_retrieve_answers(df,embedding_model,test_question, user_id=None, k=5,index_q_user=None,index_q_only=None):
    # Prepare embedding
    query_emb = prepare_question_embedding(test_question, embedding_model, user_id=user_id)  # shape: (1, dim)

    # Select index
    if user_id and user_id in df['user_id'].values:
        index = index_q_user
        source_df = df  # use full user-augmented questions
    else:
        index = index_q_only
        source_df = df

    # Search top-k
    scores, indices = index.search(query_emb, k)
    
    # Extract top answers and metadata
    top_answers = [source_df.iloc[i]['answer_clean'] for i in indices[0]]
    top_questions = [source_df.iloc[i]['question_clean'] for i in indices[0]]
    top_scores = scores[0]

    return list(zip(top_questions, top_answers, top_scores))

def clear_gpu():
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()

def load_llm():
    clear_gpu()
    model_id = "mistralai/Mistral-7B-Instruct-v0.3"

    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_compute_dtype=torch.float16,
        bnb_4bit_use_double_quant=True
    )

    tokenizer = AutoTokenizer.from_pretrained(model_id)

    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        quantization_config=bnb_config,
        device_map={"": 0},  # force entire model to GPU 0
        low_cpu_mem_usage=True,
        torch_dtype=torch.float16,
    )

    model.eval()
    return pipeline("text-generation", model=model, tokenizer=tokenizer)

