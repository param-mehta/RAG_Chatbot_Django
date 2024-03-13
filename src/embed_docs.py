import os
import torch
from langchain.schema.document import Document
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Chroma


def embed_and_chunk_docs(docs_path, db_path, embeddings_function):
    """
    Embed and chunk documents, storing the results in a Chroma vector store.

    Args:
        docs_path (str): Path to the directory containing text documents.
        db_path (str): Path to the directory to store the Chroma vector store.
        embeddings_function: Embeddings function for document content.

    Returns:
        None
    """
    docs = []

    # Read each document and create a Document object
    for filename in os.listdir(docs_path):
        file_path = os.path.join(docs_path, filename)
        with open(file_path, 'r',encoding='latin1') as file:
            content = file.read()
            docs.append(Document(page_content=content))
    print(len(docs))

    # Split documents into chunks using RecursiveCharacterTextSplitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=64)
    texts = text_splitter.split_documents(docs)

    # Create a Chroma vector store from the document chunks
    db = Chroma.from_documents(texts, embeddings_function, persist_directory=db_path)
    return


def main():
    # Check if CUDA is available, set the device accordingly
    DEVICE = "cuda:0" if torch.cuda.is_available() else "cpu"

    # Define paths for two sets of documents and Chroma vector stores
    docs_path_1 = 'data/parsed_rules_docs'
    docs_path_2 = 'data/parsed_bill_docs'

    db_path_1 = 'data/rules_chroma_db'
    db_path_2 = 'data/bill_chroma_db'

    # Define the embeddings function using HuggingFaceInstructEmbeddings
    embeddings_function = HuggingFaceInstructEmbeddings(
        model_name="hkunlp/instructor-large", model_kwargs={"device": DEVICE}
    )

    # Process and store embeddings for two sets of documents
    embed_and_chunk_docs(docs_path_1, db_path_1, embeddings_function)
    embed_and_chunk_docs(docs_path_2, db_path_2, embeddings_function)

if __name__ == "__main__":
    main()
