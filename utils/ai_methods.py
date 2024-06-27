import numpy as np
import torch
from transformers import AutoModel, AutoTokenizer


# Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(
        input_mask_expanded.sum(1), min=1e-9
    )


# This function sorts the given threads based on their total similarity with the given keywords
def sort_by_similarity(thread_objects, keywords):
    # Initialize tokenizer + model.
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
    model = AutoModel.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")

    # Transform the generator to a list of Submission Objects, so we can sort later based on context similarity to
    # keywords
    thread_objects = list(thread_objects)

    threads_sentences = []
    for i, thread in enumerate(thread_objects):
        threads_sentences.append(" ".join([thread.title, thread.selftext]))

    # Threads inference
    encoded_threads = tokenizer(
        threads_sentences, padding=True, truncation=True, return_tensors="pt"
    )
    with torch.no_grad():
        threads_embeddings = model(**encoded_threads)
    threads_embeddings = mean_pooling(threads_embeddings, encoded_threads["attention_mask"])

    # Keyword inference
    encoded_keywords = tokenizer(keywords, padding=True, truncation=True, return_tensors="pt")
    with torch.no_grad():
        keywords_embeddings = model(**encoded_keywords)
    keywords_embeddings = mean_pooling(keywords_embeddings, encoded_keywords["attention_mask"])

    # Compare every keyword w/ every thread embedding
    threads_embeddings_tensor = torch.tensor(threads_embeddings)
    total_scores = torch.zeros(threads_embeddings_tensor.shape[0])
    cosine_similarity = torch.nn.CosineSimilarity()
    for keyword_embedding in keywords_embeddings:
        keyword_embedding = torch.tensor(keyword_embedding).repeat(
            threads_embeddings_tensor.shape[0], 1
        )
        similarity = cosine_similarity(keyword_embedding, threads_embeddings_tensor)
        total_scores += similarity

    similarity_scores, indices = torch.sort(total_scores, descending=True)

    # threads_sentences = np.array(threads_sentences)[indices.numpy()]

    thread_objects = np.array(thread_objects)[indices.numpy()].tolist()

    # print('Similarity Thread Ranking')
    # for i, thread in enumerate(thread_objects):
    #    print(f'{i}) {threads_sentences[i]} score {similarity_scores[i]}')

    return thread_objects, similarity_scores
