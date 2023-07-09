import os
from from_root import from_root
from datetime import datetime

TIMESTAMP:str = datetime.now().strftime('%m_%d_%Y_%H_%M_%S')


# Data Ingestion related constants
ARTIFACTS_DIR = os.path.join(from_root(), "artifacts")
BUCKET_NAME = 'vnpd-io-files'
S3_DATA_FOLDER_NAME = "images.zip"
DATA_INGESTION_ARTIFACTS_DIR = "DataIngestion"
UNZIP_FOLDER_NAME = 'images/'

