import logging
import os

from azure.storage.blob import BlobServiceClient

def fill_template(email_template: str, merge_fields: dict) -> str:
    # TODO something with jinja
    return 'filled'


# read template files from cloud storage and return dictionary
def get_templates(email_template_name: str) -> dict:
    templates = {'subject_template': '', 'body_template': ''}

    try:
        subject_template = read_email_template_file_from_azure(f'{email_template_name}-subject.j2')
        body_template = read_email_template_file_from_azure(f'{email_template_name}-body.j2')
        templates['subject_template'] = subject_template
        templates['body_template'] = body_template
    except:
        logging.error(f'Failed to get templates for {email_template_name}')

    return templates



def read_email_template_file_from_azure(file_path) -> str:
    """
    Reads a file from Azure File Storage and returns its contents as a string.

    :param file_path: Path to the file in the share (e.g., "folder1/file.txt")
    :return: Contents of the file as a string
    """
    try:
        storage_connection_string = os.environ['AzureWebJobsStorage']
        container_name = 'email-templates'
        service_client = BlobServiceClient.from_connection_string(storage_connection_string)
        blob_client = service_client.get_blob_client(container_name, file_path)
        download = blob_client.download_blob()
        file_content = download.readall()
        content = file_content.decode('utf-8')
        return content
    except:
        logging.error(f'failed to get template from {file_path}')
        return ''
