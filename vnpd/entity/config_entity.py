import os
from from_root import from_root
from dataclasses import dataclass
from vnpd.constants import *

@dataclass
class DataIngestionConfig:
    def __init__(self):
        self.DATA_INGESTION_ARTIFACTS_DIR: str = os.path.join(from_root(), ARTIFACTS_DIR, DATA_INGESTION_ARTIFACTS_DIR)
        self.ZIP_DATA_PATH: str = os.path.join(self.DATA_INGESTION_ARTIFACTS_DIR, S3_DATA_FOLDER_NAME)
        self.UNZIP_FOLDER_PATH: str = os.path.join(self.DATA_INGESTION_ARTIFACTS_DIR)
        self.DATA_PATH: str = os.path.join(self.DATA_INGESTION_ARTIFACTS_DIR, UNZIP_FOLDER_NAME)

