# RAG Chatbot using Django

## Overview

A chatbot application that answers questions about your PDFs. The RAG (Retrieval Augmented Generation) pipeline is built through LangChain while the backend is built using Django.

## Features

- Parse multiple PDFs using Google's Cloud Vision API.
- Embed and index your documents using HuggingFace's Instructor Embeddings.
- A Django website that answers user questions through Gemini pro and records user feedback for each response.

## Use Case

<img width="600" height="400" alt="Screenshot 2024-03-13 at 3 31 00 AM" src="https://github.com/param-mehta/RAG_Chatbot_Django/assets/61198990/004cb200-2aaa-49ba-a1a0-3a05450985b3">

- I have built an app that can work as a customer support chatbot for an energy service company. The user is prompted whether their query is about the company's rules and policies or is it about the bill statement. The data for the former comprises several PDFs that document the policies, conditions, and disclaimers pertaining to the company's utility services. For the latter, it is a 5-page billing statement that comprises various tables and figures explaining the breakdown of charges incurred for a particular month.
- I have built separate pipelines for the above two tasks (different vectorstore, prompts, chunk size, etc.) to ensure faster and better performance.
- To adapt this system for your use case, all you need to do is replace the PDFs and the prompt. You can change other hyperparameters later to finetune your system and improve baseline performance.

## Demo

Click below to see a short demo of the app:

[![Demo](https://img.youtube.com/vi/RHn41-COJcY/0.jpg)](https://www.youtube.com/watch?v=RHn41-COJcY)

## Installation

1. Set up an environment:
    ```bash
    conda create --name rag_chatbot python=3.11.7
    ```
    ```bash
    conda activate rag_chatbot
    ```
    ```bash
    bash env.sh
    source env.sh
    ```
    In the env.sh, the variable GOOGLE_API_KEY_STRING needs the contents of the service account JSON file as a string and not its path.

2. Clone the repository and install dependencies:
    ```bash
    git clone https://github.com/param-mehta/RAG_Chatbot_Django.git
    ```
    ```bash
    cd RAG_Chatbot_Django
    ```
    ```bash
    pip install -r requirements.txt
    ```

3. Apply changes in the database:
    ```bash
    cd src/app
    python manage.py migrate
    ```

## Usage

1. Generate a service account JSON file in your Google Cloud Console. Enable the following API:
   - Google Vertex AI API
   - Google Cloud Vision API
   - Google Cloud Storage API

2. Place your PDFs in a folder in your Google Cloud bucket. In `parse_pdfs.py`, add the path of all these PDFs in a list. Make separate lists if you want to segregate your problem into different tasks like I mentioned above. Specify the Google Storage path where you want your PDFs to be stored.

3. Run `parse_pdfs.py` to convert PDFs into text files.

4. Run `embed_docs.py` to convert text into embeddings. 

5. To start the application:
    ```bash
    python manage.py runserver
    ```
6. You can see a db.sqlite3 file inside the app folder. You can access conversations and their feedback through this SQLite database.

## Guide

`parse_pdfs.py`:

- Fetches data from LinkedIn using Jsearch API parameters.
- Stores JSON files in a GCS bucket.

`embed_docs.py`:

This is the main DAG file defining operators and dependencies, running daily.

`data`

- The chroma db files for both the tasks are stored inside this directory. Note that this stores the embeddings for each document and is different from the SQLite3 database I mentioned above.

`app/templates`:

Contains the HTML files for each webpage.

`app/chatbot`:

  - `models.py` - This is where you create new models by defining their schema. Any table that your app is referencing should be initialized here. It's a Django equivalent of create table queries in SQL.
  - `urls.py` - It maps URL patterns to views, which are Python functions or class-based views that handle HTTP requests.
  - `views.py` - This file defines the views, which are Python functions or classes that handle HTTP requests and return HTTP responses. Views encapsulate the core logic of your application.
  - `chatbot_utils.py` - This file contains helper functions to set up the RAG pipeline, which includes creating an instance of a Chroma db vector store and conversation retrieval chain. You also define your LLM prompts in this file.

I am storing conversations in the following structure:

<img width="461" alt="image" src="https://github.com/param-mehta/RAG_Chatbot_Django/assets/61198990/3c1842f6-2fc9-422c-9b98-039f3e3b3eaa">

<br>
<br>

These can be queried through SQL and be used for evaluation and finetuning. You can make other changes to this schema based on your requirement. Make sure to migrate those changes before running the app again.
