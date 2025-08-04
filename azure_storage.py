from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from azure.core.exceptions import AzureError
from config import Config
import logging
import uuid
import os

class AzureStorage:
    def __init__(self):
        self.connection_string = Config.AZURE_STORAGE_CONNECTION_STRING
        self.container_name = Config.AZURE_CONTAINER_NAME
        self.blob_service_client = None
        
        if self.connection_string:
            try:
                self.blob_service_client = BlobServiceClient.from_connection_string(self.connection_string)
                self._ensure_container_exists()
            except Exception as e:
                logging.error(f"Failed to initialize Azure Storage: {e}")
    
    def _ensure_container_exists(self):
        try:
            container_client = self.blob_service_client.get_container_client(self.container_name)
            if not container_client.exists():
                container_client.create_container()
                logging.info(f"Created container: {self.container_name}")
        except Exception as e:
            logging.error(f"Error ensuring container exists: {e}")
    
    def upload_file(self, file_data, file_name, folder="general"):
        if not self.blob_service_client:
            return None
        
        try:
            # Generate unique filename
            file_extension = os.path.splitext(file_name)[1]
            unique_filename = f"{folder}/{uuid.uuid4()}{file_extension}"
            
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=unique_filename
            )
            
            blob_client.upload_blob(file_data, overwrite=True)
            
            # Return the blob URL
            return blob_client.url
        except AzureError as e:
            logging.error(f"Error uploading file to Azure: {e}")
            return None
    
    def delete_file(self, blob_name):
        if not self.blob_service_client:
            return False
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            blob_client.delete_blob()
            return True
        except AzureError as e:
            logging.error(f"Error deleting file from Azure: {e}")
            return False
    
    def get_file_url(self, blob_name):
        if not self.blob_service_client:
            return None
        
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name, 
                blob=blob_name
            )
            return blob_client.url
        except AzureError as e:
            logging.error(f"Error getting file URL: {e}")
            return None

# Global storage instance
azure_storage = AzureStorage()