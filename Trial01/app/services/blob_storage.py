from __future__ import annotations

import mimetypes
import os
from pathlib import Path
from typing import BinaryIO


class BlobStorageService:
    """Uploads car images to Azure Blob Storage and returns public blob URLs."""

    def __init__(self) -> None:
        self.connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        self.container_name = os.getenv("AZURE_STORAGE_CONTAINER", "car-images")
        self.account_url = os.getenv("AZURE_STORAGE_ACCOUNT_URL")

    def _container_client(self):
        if not self.connection_string and not self.account_url:
            raise RuntimeError(
                "Set AZURE_STORAGE_CONNECTION_STRING or AZURE_STORAGE_ACCOUNT_URL "
                "before uploading images."
            )

        try:
            from azure.storage.blob import BlobServiceClient, ContainerClient, ContentSettings
        except ImportError as error:
            raise RuntimeError(
                "Install azure-storage-blob before using Azure image storage."
            ) from error

        if self.connection_string:
            service_client = BlobServiceClient.from_connection_string(self.connection_string)
            container_client = service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
            return container_client

        return ContainerClient(account_url=self.account_url, container_name=self.container_name)

    def upload_image(self, image_path: str | Path, car_id: str) -> str:
        path = Path(image_path)
        if not path.is_file():
            raise FileNotFoundError(f"Image not found: {path}")
        with path.open("rb") as image_file:
            return self.upload_file(image_file, path.name, car_id)

    def upload_file(self, image_file: BinaryIO, filename: str, car_id: str) -> str:
        container_client = self._container_client()
        blob_name = f"{car_id}/{filename}"
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        blob_client = container_client.get_blob_client(blob_name)
        blob_client.upload_blob(
            image_file,
            overwrite=True,
            content_settings=ContentSettings(content_type=content_type),
        )
        return blob_client.url
