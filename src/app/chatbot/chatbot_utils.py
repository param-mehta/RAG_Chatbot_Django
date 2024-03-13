import os
from langchain.prompts import PromptTemplate
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain.schema.messages import HumanMessage, AIMessage
from langchain.chat_models import ChatVertexAI
from google.oauth2 import service_account
from google.cloud import aiplatform


# RAG format for generating prompts
RAG_FORMAT = """
{context}

Question: {question}
"""


# System prompts for different issue types
DEFAULT_SYSTEM_PROMPT = """You are a helpful, respectful and honest assistant. Always answer as helpfully as possible, while being safe. 
Your answers should not include any harmful, unethical, racist, sexist, toxic, dangerous, or illegal content. 
Please ensure that your responses are socially unbiased and positive in nature. If a question does not make 
any sense, or is not factually coherent, explain why instead of answering something not correct. 
If you don't know the answer to a question, please don't share false information."""

RULES_PROMPT = """You are a helpful assistant. Use the following pieces of context to answer the question at the end. The question will be
about some rules regarding electricity bill payment and about the energy company's policies. If you don't know the answer, just say that you don't know, 
don't try to make up an answer."""

BILL_PROMPT = """Use the following pieces of context to answer the question at the end. The context comprises of a billing 
statement issued by an energy company to a consumer. It contains the breakdown of different kinds of charges incurred by a consumer.
Answer any customer queries regarding the charges. Do not answer from outside the context."""


# Mapping of issue types to their respective system prompts and vector store paths
ISSUE_PROMPT = {
    'Rules': RULES_PROMPT,
    'Bill Breakdown': BILL_PROMPT
}

ISSUE_DB_PATH = {
    'Rules': 'src/data/rules_chroma_db',
    'Bill Breakdown': 'src/data/bill_chroma_db'
}


def generate_prompt(prompt: str = RAG_FORMAT, issue_type='Rules') -> str:
    """
    Generate a formatted prompt for the Retrieval QA system.

    Args:
        prompt (str): RAG format prompt template.
        issue_type (str): Type of the issue for which the prompt is generated.

    Returns:
        str: Formatted prompt.
    """
    system_prompt = ISSUE_PROMPT[issue_type]
    return f"""
            [INST] <<SYS>>
            {system_prompt}
            <</SYS>>
        {prompt} [/INST]
        """.strip()

def get_db(issue_type, embedding_function):
    """
    Get a Chroma vector store based on the issue type.

    Args:
        issue_type (str): Type of the issue.
        embedding_function: Embeddings function for document content.

    Returns:
        Chroma: Chroma vector store.
    """
    return Chroma(persist_directory=ISSUE_DB_PATH[issue_type], embedding_function=embedding_function)

def get_qa_chain(llm, db, prompt):
    """
    Create a Retrieval QA chain.

    Args:
        llm: Language model.
        db: Chroma vector store.
        prompt: Prompt template.

    Returns:
        RetrievalQA: Retrieval QA chain.
    """
    qa_chain = ConversationalRetrievalChain.from_llm(
        llm=llm, 
        chain_type="stuff", 
        retriever=db.as_retriever(search_kwargs={"k": 1}),
        get_chat_history=lambda o:o,
        memory=ConversationBufferMemory(memory_key="chat_history", output_key='answer', return_messages=False), 
        combine_docs_chain_kwargs={'prompt': prompt},
        return_generated_question = True,
        return_source_documents = True)
    return qa_chain

def get_chat_history(chats):
    """
    Creates chat_history based on a django queryset of chat messages.

    Args:
        chats (QuerySet): A Django QuerySet of Chat objects containing message-response pairs.

    Returns:
    chat_history: A list of (HumanMessage,AIMessage) tuples.
    """
    chat_history = []
    
    if len(chats) == 0:
        return chat_history

    for chat in chats:
        user_message = HumanMessage(content=chat.message)
        ai_message = AIMessage(content=chat.response)
        chat_history.append((user_message,ai_message))

    return chat_history