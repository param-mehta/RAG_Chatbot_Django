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


## Installation and Usage

#### Google Cloud Composer

To set up on Composer, create a Composer 2 Environment with a Medium size.

1. Configure the following environment variables in the Composer environment:
   ```bash
    #!/bin/bash
    export GS_BUCKET_NAME=""
    export GCP_PROJECT_NAME=""
    export MONGO_USERNAME=""
    export MONGO_PASSWORD=""
    export DB_NAME=""
    export ATLAS_CONNECTION_STRING="mongodb+srv://<user>:<password>@<database_name>.vnw63oa.mongodb.net/?retryWrites=true&w=majority"
    export VECTOR_INDEX_NAME=""
    export COLLECTION_NAME=""
    export JOBS_COLLECTION_NAME=""
    export COLLECTION_NAME_STATS=""
    export OBJC_DISABLE_INITIALIZE_FORK_SAFETY=YES
    ```
2. Install the following dependencies under the PyPI Packages tab in your Composer environment:
    ```bash
    google-cloud-aiplatform
    apache-airflow-providers-apache-spark
    pymongo[srv]==3.11
    langchain==0.1.5
    langchain-community==0.0.18
    langchain-google-vertexai==0.0.2
    InstructorEmbedding==1.0.1
    google-cloud-storage
    pyspark==3.4.1
    certifi
    torch==2.0.1
    sentence_transformers==2.2.22
    ```

#### Local

1. Set up an environment:
    ```bash
    conda create --name job_recommender python=3.11.7
    ```
    ```bash
    conda activate job_recommender
    ```
    ```bash
    bash env.sh
    source env.sh
    ```

2. Clone the repository and install dependencies:
    ```bash
    git clone https://github.com/yourusername/Linkedin_job_recommender.git
    ```
    ```bash
    cd Linkedin_job_recommender
    ```
    ```bash
    pip install -r requirements.txt
    ```

3. Initialize metastore:
    ```bash
    airflow db init
    ```

4. Create a DAG folder:
    ```bash
    mkdir ~/airflow/dags
    ```
    This directory should contain all your DAG files.

5. Start the scheduler to trigger the scheduled DAG runs:
    ```bash
    airflow scheduler
    ```

6. Run the webserver to monitor your DAG runs:
    ```bash
    airflow webserver
    ```

7. Launch the dashboard, upload your resume, and explore recommended jobs:
    ```bash
    streamlit run app.py
    ```

## Guide

`linkedin_dag.py`:

This is the main DAG file defining operators and dependencies, running daily.

`get_jobs_from_api.py`:

- Fetches data from LinkedIn using Jsearch API parameters.
- Stores JSON files in a GCS bucket.

`gcs_to_mongo.py`:

- Reads JSON files from the GCS bucket and converts them into a Spark RDD.
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
