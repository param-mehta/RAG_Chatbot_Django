import os
import json
import re
from google.cloud import storage
from google.cloud import vision
from google.oauth2 import service_account
from google.cloud import aiplatform


def async_detect_document(gcs_source_uri, gcs_destination_uri):
    """
    Perform OCR on PDF/TIFF files stored on Google Cloud Storage asynchronously.

    Args:
        gcs_source_uri (str): The GCS URI of the source file.
        gcs_destination_uri (str): The GCS URI to store the output JSON file.

    Returns:
        list: List of extracted text from the document.
    """

    # Supported mime_types are: 'application/pdf' and 'image/tiff'
    mime_type = "application/pdf"

    # How many pages should be grouped into each json output file.
    batch_size = 1

    client = vision.ImageAnnotatorClient()
    feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

    # Set up input and output configurations
    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)
    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size
    )

    # Create an asynchronous request
    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config, output_config=output_config
    )

    # Execute the asynchronous request
    operation = client.async_batch_annotate_files(requests=[async_request])

    print("Waiting for the operation to finish.")
    operation.result(timeout=420)
    
    # Access the result files stored on GCS
    storage_client = storage.Client()
    match = re.match(r"gs://([^/]+)/(.+)", gcs_destination_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)
    bucket = storage_client.get_bucket(bucket_name)
    
    # Extract text from each result file
    docs = []
    for filename in [blob for blob in list(bucket.list_blobs(prefix=prefix)) if not blob.name.endswith("/")]:
        json_string = filename.download_as_bytes().decode("utf-8")
        response = json.loads(json_string)
        response = response["responses"][0]
        annotation = response["fullTextAnnotation"]
        docs.append(annotation['text'])

    return docs

def save_parsed_docs(filenames, gs_output_path, local_output_path):
    """
    Save parsed documents to local files.

    Args:
        filenames (list): List of GCS URIs of source documents.
        gs_output_path (str): GCS URI to store OCR output.
        local_output_path (str): Local directory to store parsed text files.

    Returns:
        None
    """

    # Authenticate google service account
    json_creds = json.loads(os.environ['GOOGLE_API_KEY_STRING'],strict=False)
    project_id = json_creds['project_id']
    credentials = service_account.Credentials.from_service_account_info(json_creds)
    aiplatform.init(project=project_id, credentials=credentials)

    # Process each document and gather extracted text
    docs = []
    for filename in filenames:
        docs.extend(async_detect_document(filename, gs_output_path))
    print(len(docs))

    # Save each parsed document to a local text file
    for i, text in enumerate(docs):
        filename = f"{local_output_path}/{i}.txt"
        with open(filename, "w") as file:
            file.write(text)

def main():
    # Define input and output paths for two sets of documents
    bucket_name = os.environ['GS_BUCKET_NAME']
    filenames_1 = [f'gs://{bucket_name}/pdfs/rules.pdf']
    filenames_2 = [f'gs://{bucket_name}/pdfs/rules.pdf']

    gs_output_path_1 = f'gs://{bucket_name}/rules_output/'
    gs_output_path_2 = f'gs://{bucket_name}/bill_output/'

    local_output_path_1 = 'data/parsed_rules_docs'
    local_output_path_2 = 'data/parsed_bill_docs'

    # Process and save documents
    save_parsed_docs(filenames_1, gs_output_path_1, local_output_path_1)
    save_parsed_docs(filenames_2, gs_output_path_2, local_output_path_2)

if __name__ == "__main__":
    main()
