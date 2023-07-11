import os,sys
import pandas as pd
import numpy as np
import cv2
import xml.etree.ElementTree as xet
from vnpd.config.s3_operations import S3Operation
from vnpd.entity.config_entity import *
from vnpd.entity.artifacts_entity import *
from vnpd.logger import logging
from vnpd.exception import CustomException
from vnpd.utils.utils import *
from vnpd.constant import *
from glob import glob
from tensorflow.keras.preprocessing.image import img_to_array, load_img

class DataTransformation:
    def __init__(self, data_transformation_config : DataTransformationConfig, data_ingestion_artifact:DataIngestionArtifacts):
        self.data_transformation_config = data_transformation_config
        self.data_ingestion_artifact = data_ingestion_artifact

    def get_bounding_box_coordinates(self):
        """
        Method Name :   get_bounding_box_coordinates
        Description :   This method will indivisually take each file and parse into  xml.etree and find the object and find bndbox object. 
                        Then we extract xmin,xmax,ymin,ymax and saved those values in the dictionary named labels_dict.
        """
        path = glob(os.path.join(self.data_ingestion_artifact.image_data_dir,'*.xml'))
        labels_dict = dict(filepath=[],xmin=[],xmax=[],ymin=[],ymax=[])
        for filename in path:
            info = xet.parse(filename)
            root = info.getroot()
            member_object = root.find('object')
            labels_info = member_object.find('bndbox')
            xmin = int(labels_info.find('xmin').text)
            xmax = int(labels_info.find('xmax').text)
            ymin = int(labels_info.find('ymin').text)
            ymax = int(labels_info.find('ymax').text)

            labels_dict['filepath'].append(filename)
            labels_dict['xmin'].append(xmin)
            labels_dict['xmax'].append(xmax)
            labels_dict['ymin'].append(ymin)
            labels_dict['ymax'].append(ymax)
            
        dataframe = pd.DataFrame(labels_dict)
        dataframe.to_csv(self.data_transformation_config.LABELED_DATAFRAME,index=False)
        return dataframe
    
    def data_preprocessing(self,labels_dataframe, image_path_list):
        """
        Method Name :   data_preprocessing
        Description :   In this method we will first normalize our data &
                        We will resize image into (224,224) because it is the standard compatible size of pre trained transfer learning model ie. Inception Resnet v2.
        """
        labels=labels_dataframe.iloc[:,1:].values
        data = []
        output = []
        for index in range(len(image_path_list)):
            image = image_path_list[index]
            image_array = cv2.imread(image)
            height,width,depth = image_array.shape
            
            load_image = load_img(image, target_size=(224,224))
            load_image_array = img_to_array(load_image)
            #We will normalize the image by dividing with maximum number ie. 255( max no for 8 bit images) and the process is called normalization(Min-Max Scaler).
            normalize_load_image_arr = load_image_array/255.0

            #We also need to normalize our labels too because for DL model output range should be between 0 to 1. For normalizing labels we need to divide the diagonal points with the width and height of image.
            xmin,xmax,ymin,ymax = labels[index]
            normalised_xmin, normalized_xmax = xmin/width, xmax/width
            normalised_ymin, normalized_ymax = ymin/height, ymax/height
            label_normalized = (normalised_xmin,normalized_xmax,normalised_ymin,normalized_ymax)
            data.append(normalize_load_image_arr)
            output.append(label_normalized)
        return data, output

    def get_filename_from_XML(self,filename):
            """
            Method Name :   get_filename_from_XML
            Description :   This method will extract the respective image filename of the XML File
            """
            image_filename = xet.parse(filename).getroot().find('filename').text
            image_filepath= os.path.join(self.data_ingestion_artifact.image_data_dir,image_filename)
            return image_filepath

    def initiate_data_transformation(self):
        try:
            logging.info("Entered the initiate_data_transformation method of Data transformation class")

            
            os.makedirs(self.data_transformation_config.DATA_TRANSFORMATION_ARTIFACTS_DIR,exist_ok=True)

            labels_dataframe = self.get_bounding_box_coordinates()
            logging.info("successfully extracted the diagonal position of each image and convert the data from an unstructured to a structured format")

            image_path_list = list(labels_dataframe['filepath'].apply(self.get_filename_from_XML))

            data, output = self.data_preprocessing(labels_dataframe, image_path_list)

            # Generating X and y variables 
            X = np.array(data, dtype= np.float32)
            y = np.array(output, dtype= np.float32)

            #Save Numpy arrays
            save_numpy_array_data(file_path=self.data_transformation_config.DATA_TRANSFORMATION_DATA,array=X)
            save_numpy_array_data(file_path=self.data_transformation_config.DATA_TRANSFORMATION_OUTPUT,array=y)
           
            data_transformation_artifact = DataTransformationArtifacts(
                transformed_data_file_path=self.data_transformation_config.DATA_TRANSFORMATION_DATA,
                transformed_output_file_path=self.data_transformation_config.DATA_TRANSFORMATION_OUTPUT
            )
            logging.info("Exited the initiate_data_transformation method of Data transformation class")
            return data_transformation_artifact

        except Exception as e:
            raise CustomException(e, sys)