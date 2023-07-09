import os,sys
from vnpd.config.s3_operations import S3Operation
from vnpd.entity.config_entity import DataIngestionConfig
from vnpd.entity.artifacts_entity import DataIngestionArtifacts
from vnpd.logger import logging
from vnpd.exception import CustomException
from vnpd.constant import *
from zipfile import ZipFile, Path



class DataIngestion:
    def __init__(self, data_ingestion_config:DataIngestionConfig, s3_operations:S3Operation):
        self.data_ingestion_config = data_ingestion_config
        self.s3_operations = s3_operations

    def get_images_from_s3(self, bucket_file_name: str, bucket_name: str, output_filepath: str) -> zip:
        """
        Method Name :   get_images_from_s3
        Description :   This method will fetch compressed folder from s3 bucket and save it.
        """
        logging.info("Entered the get_data_from_s3 method of Data ingestion class")
        try:
            if not os.path.exists(output_filepath):
                self.s3_operations.read_data_from_s3(bucket_file_name,bucket_name,output_filepath)

            logging.info("Exited the get_data_from_s3 method of Data ingestion class")

        except Exception as e:
            raise CustomException(e, sys) from e 
    
    def _get_updated_list_of_files(self,list_of_files):
        """
        Method Name :   _get_updated_list_of_files
        Description :   This hidden method will check if file is of extension jpeg or xml.
        """
        return [f for f in list_of_files if f.endswith(".jpeg") or (f.endswith(".xml")) ]

    def _preprocess(self, zf:ZipFile, f:str, working_dir):
        """
        Method Name :   _preprocess
        Description :   This hidden method will check if file exists if so , then will extract into target folder
                         & Also checks size of file, if its empty then removes it .
        """
        target_filepath = os.path.join(working_dir,f)
        if not os.path.exists(target_filepath):
            zf.extract(f, working_dir)

        if os.path.getsize(target_filepath==0):
            os.remove(target_filepath)
    
    def unzip_file_and_clean(self, zip_data_filepath: str, unzip_dir_path: str) -> Path:
        """
        Method Name :   unzip_file
        Description :   This method will unzip folder and save it.
        """
        logging.info("Entered the unzip_file method of Data ingestion class")
        try:
            with ZipFile(zip_data_filepath, mode='r') as zip_ref:

                list_of_files = zip_ref.namelist()
                updated_list_of_files = self._get_updated_list_of_files(list_of_files)
                for file in updated_list_of_files:
                    self._preprocess(zip_ref, file, unzip_dir_path)

            logging.info("Exited the unzip_file method of Data ingestion class")
            return unzip_dir_path

        except Exception as e:
            raise CustomException(e, sys) from e
            
    
    def initiate_data_ingestion(self):
        try:
            
            # Creating Data Ingestion Artifacts directory inside artifact folder
            os.makedirs(self.data_ingestion_config.DATA_INGESTION_ARTIFACTS_DIR, exist_ok=True)
            logging.info(
                f"Created {os.path.basename(self.data_ingestion_config.DATA_INGESTION_ARTIFACTS_DIR)} directory."
            )
            self.get_images_from_s3(bucket_file_name=S3_DATA_FOLDER_NAME,
            bucket_name=BUCKET_NAME,
            output_filepath=self.data_ingestion_config.ZIP_DATA_PATH)

            self.unzip_file_and_clean(zip_data_filepath=self.data_ingestion_config.ZIP_DATA_PATH,
            unzip_dir_path= self.data_ingestion_config.UNZIP_FOLDER_PATH)

            data_ingestion_artifacts = DataIngestionArtifacts(image_data_dir=self.data_ingestion_config.DATA_PATH)

            logging.info("Exited the initiate_data_ingestion method of Data Ingestion class ")

            return data_ingestion_artifacts
            
        except Exception as e:
            raise CustomException(e,sys)