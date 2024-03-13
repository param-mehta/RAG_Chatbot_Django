# RAG Chatbot using Django

## Overview

An Chatbot application that answers questions about your PDFs. The RAG (Retrieval Augmented Generation) pipeline is built through LangChain while the backend is built using Django

## Features

- Parse multiple PDFs using Google's Cloud Vision API
- Embed and index your documents using HuggingFace's Instructor Embeddings
- A Django website that answers user questions through Gemini pro and records user feedback for each reponse

 
## Use Case
<img width="600" height="400" alt="Screenshot 2024-03-13 at 3 31 00 AM" src="https://github.com/param-mehta/RAG_Chatbot_Django/assets/61198990/004cb200-2aaa-49ba-a1a0-3a05450985b3">
<br>
<br>

- I have built an app that can work as a customer support chatbot for an energy service company. The user is prompted whether their query is about the company's rules and policies or is it about the bill statement. The data for the former comprises of several pdfs that document the policies, conditions and disclaimers pertaining to the company's utility services. For the later, it is a 5 page billing statement that comprises of various tables and figures explaining the breakdown of charges incurred for a particular month.
- I have built separate pipelines for the above two tasks (different vectorstore, prompts, chunksize, etc) to ensure faster and better performance.
- To adapt this system for your use case, all you need to do is replace the pdfs and the prompt. You can change other hyperparameters later to finetune your system and improve baseline performance.


## Demo
[![IMAGE ALT TEXT HERE](https://img.youtube.com/vi/RHn41-COJcY/0.jpg)](https://www.youtube.com/watch?v=RHn41-COJcY)


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

2. Clone the repository and install dependencies:
    ```bash
    git clone https://github.com/yourusername/RAG_Chatbot_Django.git
    ```
    ```bash
    cd RAG_Chatbot_Django
    ```
    ```bash
    pip install -r requirements.txt
    ```

3. Apply changes in database:
    ```bash
    cd src/app
    python manage.py migrate
    ```
## Usage

1. Place your pdfs in a folder in your google cloud bucket. In `parse_pdfs.py`, add the path of all these pdfs in a list. Make separate lists if you want to segregate your problem into different tasks like I mentioned above. Specify the google storage path where you want your pdfs to be stored.

2. Run `parse_pdfs.py` to convert pdfs into text files.

3. Run `embed_docs.py` to convert text into embeddings. 

4. To start the application:
    ```bash
    python manage.py runserver
    ```
5. You can see a db.sqlite3 file inside the app folder. You can access conversations and their feedback through this sqlite database.

## Guide

`parse_pdfs.py`:

- Fetches data from LinkedIn using Jsearch API parameters.
- Stores JSON files in a GCS bucket.

`embed_docs.py`:

This is the main DAG file defining operators and dependencies, running daily.

`data`

- The chroma db files for both the tasks are stored inside this directory. 
- Filters and modifies specific fields based on the desired format.
- Applies text cleaning functions to the job description field.
- Stores job details as a collection on a MongoDB Atlas cluster.

`convert_to_embeddings.py`:

Converts the description field into embeddings using Langchain, utilizing Instructor Embeddings from Hugging Face.

`calculate_summary_statistics.py`:

Converts the description field into embeddings using Langchain, utilizing Instructor Embeddings from Hugging Face.

`app.py`:

This Streamlit dashboard:
- Displays job statistics about collected jobs.
- Prompts the user to select search parameters and upload a resume.
- Parses resume text, embeds it, and performs similarity search to recommend top job positions.
- For each job, displays details like salary, location, URL, and similarity score.
- Also presents a Gemini-induced summary explaining why the resume is a good match for the selected job.

`helper.py`:

Contains helper functions used by `app.py`.

`user_definition.py`: 

Configuration file for importing environment variables.

## Time to find a job!
