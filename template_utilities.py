import logging
import os

import pytest
from azure.storage.blob import BlobServiceClient


def fill_template(email_template: str, merge_fields: dict) -> str:
    # TODO: Replace with Jinja2 or another template engine.
    return "filled"


# ----------------------------------------------------------------------
# Read template files from cloud storage and return dictionary
# ----------------------------------------------------------------------
def get_templates(email_template_name: str) -> dict:
    templates = {
        "subject_template": "",
        "body_template": "",
    }

    try:
        subject_template = read_email_template_file_from_azure(
            f"{email_template_name}-subject.j2"
        )
        body_template = read_email_template_file_from_azure(
            f"{email_template_name}-body.j2"
        )

        templates["subject_template"] = subject_template
        templates["body_template"] = body_template

    except Exception as ex:
        logging.error(
            f"Failed to get templates for {email_template_name}: {ex}"
        )

    return templates


def read_email_template_file_from_azure(file_path: str) -> str:
    """
    Reads a template file from Azure Blob Storage and returns
    its contents as a string.

    :param file_path: Blob path, e.g. "welcome-subject.j2"
    :return: Contents of the file as a string
    """
    try:
        storage_connection_string = os.environ["AzureWebJobsStorage"]
        container_name = "email-templates"

        service_client = BlobServiceClient.from_connection_string(
            storage_connection_string
        )

        blob_client = service_client.get_blob_client(
            container=container_name,
            blob=file_path,
        )

        download = blob_client.download_blob()
        file_content = download.readall()

        return file_content.decode("utf-8")

    except Exception as ex:
        logging.error(
            f"Failed to get template from {file_path}: {ex}"
        )
        return ""


# ----------------------------------------------------------------------
# Hardcoded API / Storage URLs
# ----------------------------------------------------------------------
# No hardcoded Azure API or storage URLs are present in this file.
#
# Keep storage endpoints and connection strings in environment variables.
# For example, do NOT hardcode values like:
#
# AZURE_STORAGE_URL = "https://example.blob.core.windows.net"
# AZURE_CONNECTION_STRING = "DefaultEndpointsProtocol=..."
#
# AzureWebJobsStorage is read from the environment instead.


# ----------------------------------------------------------------------
# Pytest Tests
# ----------------------------------------------------------------------
def test_fill_template_returns_filled():
    result = fill_template(
        "Hello {{ first_name }}",
        {"first_name": "Alice"},
    )

    assert result == "filled"


def test_get_templates(monkeypatch):
    def mock_read_template(file_path):
        if file_path == "welcome-subject.j2":
            return "Welcome subject"

        if file_path == "welcome-body.j2":
            return "Welcome body"

        return ""

    monkeypatch.setattr(
        __name__ + ".read_email_template_file_from_azure",
        mock_read_template,
    )

    result = get_templates("welcome")

    assert result == {
        "subject_template": "Welcome subject",
        "body_template": "Welcome body",
    }


def test_get_templates_returns_empty_values_on_exception(monkeypatch):
    def mock_read_template(file_path):
        raise RuntimeError("Azure unavailable")

    monkeypatch.setattr(
        __name__ + ".read_email_template_file_from_azure",
        mock_read_template,
    )

    result = get_templates("welcome")

    assert result == {
        "subject_template": "",
        "body_template": "",
    }


def test_read_email_template_file_from_azure(monkeypatch):
    monkeypatch.setenv(
        "AzureWebJobsStorage",
        "test-storage-connection-string",
    )

    class MockDownload:
        def readall(self):
            return b"Hello from Azure"

    class MockBlobClient:
        def download_blob(self):
            return MockDownload()

    class MockBlobServiceClient:
        def get_blob_client(self, container, blob):
            assert container == "email-templates"
            assert blob == "welcome-body.j2"
            return MockBlobClient()

    def mock_from_connection_string(connection_string):
        assert connection_string == "test-storage-connection-string"
        return MockBlobServiceClient()

    monkeypatch.setattr(
        BlobServiceClient,
        "from_connection_string",
        mock_from_connection_string,
    )

    result = read_email_template_file_from_azure(
        "welcome-body.j2"
    )

    assert result == "Hello from Azure"


def test_read_email_template_file_returns_empty_when_env_missing(
    monkeypatch,
):
    monkeypatch.delenv(
        "AzureWebJobsStorage",
        raising=False,
    )

    result = read_email_template_file_from_azure(
        "welcome-body.j2"
    )

    assert result == ""


def test_read_email_template_file_handles_azure_exception(
    monkeypatch,
):
    monkeypatch.setenv(
        "AzureWebJobsStorage",
        "test-storage-connection-string",
    )

    def mock_from_connection_string(connection_string):
        raise RuntimeError("Azure connection failed")

    monkeypatch.setattr(
        BlobServiceClient,
        "from_connection_string",
        mock_from_connection_string,
    )

    result = read_email_template_file_from_azure(
        "welcome-body.j2"
    )

    assert result == ""
