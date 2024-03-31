from bertscoretest import bm25, ftsent, bertscore, load_data

def main():
    # Load the documents
    docs = load_data('../csvProcessing/allData.json')  # Adjust the path as necessary

    # Initialize the models
    bm25_model = bm25(docs)
    ftsent_model = ftsent(
        docs, model_path="fasttext-tmp/model.bin"
    )  # Adjust the path as necessary
    bert_model = bertscore(docs)

    # Define your query
    query = "rahul gandhi drinking"

    # Using BM25 model to rank documents
    bm25_idx, bm25_scores = bm25_model.rank(query)
    print("BM25 Results:")
    for idx, score in zip(bm25_idx[:10], bm25_scores[:10]):
        print(f"Document ID: {idx}, Score: {score}")

    # Using fastText sentence embeddings model to rank documents
    ftsent_idx, ftsent_scores = ftsent_model.rank(query)
    print("\nFastText Sentence Embeddings Results:")
    for idx, score in zip(ftsent_idx[:10], ftsent_scores[:10]):
        print(f"Document ID: {idx}, Score: {score}")

    # Using combined BM25 and BERTScore model to rank documents
    bert_idx, bert_scores = bert_model.rank(query)
    print("\nCombined BM25 and BERTScore Results:")
    for idx, score in zip(bert_idx[:10], bert_scores[:10]):
        print(f"Document ID: {idx}, Score: {score}", docs[idx])

if __name__ == '__main__':
    main()
