import os, sys, time
from vnpd.entity.config_entity import *
from vnpd.entity.artifacts_entity import *
from vnpd.logger import logging
from vnpd.exception import CustomException
from vnpd.constant import *
from vnpd.utils.utils import *
from pathlib import Path
import tensorflow as tf
from sklearn.model_selection import train_test_split

class ModelTraining:
    def __init__(self, training_config :TrainingConfig,
        prepare_callbacks_config :PrepareCallbacksConfig,
        data_ingestion_artifact : DataIngestionArtifacts,
        data_transformation_artifact : DataTransformationArtifacts,
        prepare_base_model_artifact : PrepareBaseModelArtifacts):

        self.training_config = training_config
        self.prepare_callbacks_config = prepare_callbacks_config
        self.data_ingestion_artifact = data_ingestion_artifact
        self.data_transformation_artifact = data_transformation_artifact
        self.prepare_base_model_artifact = prepare_base_model_artifact

    @property
    def _create_tb_callbacks(self):
        timestamp = time.strftime("%Y-%m-%d-%H-%M-%S")
        tb_running_log_dir = os.path.join(self.prepare_callbacks_config.TENSORBOARD_ROOT_LOG_DIR,f"tb_logs_at_{timestamp}") 
        return tf.keras.callbacks.TensorBoard(log_dir=tb_running_log_dir)

    @property
    def _create_ckpt_callbacks(self):
        return tf.keras.callbacks.ModelCheckpoint(
            filepath= self.prepare_callbacks_config.CHECKPOINT_MODEL_FILEPATH,
            save_best_only=True
        )

    def get_tensorboard_checkpoints_callbacks(self):
        return [
            self._create_tb_callbacks,
            self._create_ckpt_callbacks
        ]
    
    def get_model(self):
        self.model = tf.keras.models.load_model(self.prepare_base_model_artifact.updated_model_filr_path)

    def split_train_test(self):
        X = load_numpy_array_data(file_path = self.data_transformation_artifact.transformed_data_file_path)
        y = load_numpy_array_data(file_path = self.data_transformation_artifact.transformed_output_file_path)

        # Split the data into training and testing set using sklearn.
        x_train,x_test,y_train,y_test = train_test_split(X,y,train_size=0.8,random_state=0)
        print(x_train.shape,x_test.shape,y_train.shape,y_test.shape)
        return x_train,x_test,y_train,y_test
    
    @staticmethod
    def save_model(path : Path, model : tf.keras.Model):
        model.save(path)

    def train(self,x_train,x_test,y_train,y_test,callback_list):
        
        self.model.fit(
            x_train,
            y_train,
            batch_size= BATCH_SIZE,
            epochs = EPOCHS,
            validation_data=(x_test,y_test),
            callbacks = callback_list
        )

        self.save_model(path=self.training_config.TRAINED_MODEL_PATH,model=self.model)

    def initiate_model_training(self):
        try:
            logging.info("Entered the initiate_model_training method of ModelTraining class")

            model_ckpt_dir = os.path.dirname(self.prepare_callbacks_config.CHECKPOINT_MODEL_FILEPATH)

            model_dir = os.path.dirname(self.training_config.TRAINED_MODEL_PATH)

            logging.info("Exited the initiate_model_training method of ModelTraining class")
            
            callback_list = self.get_tensorboard_checkpoints_callbacks()

            create_directories([model_ckpt_dir, self.prepare_callbacks_config.TENSORBOARD_ROOT_LOG_DIR,self.training_config.MODEL_TRAINING_ARTIFACTS_DIR,model_dir])

            self.get_model()

            x_train,x_test,y_train,y_test = self.split_train_test()

            self.train(x_train,x_test,y_train,y_test,callback_list=callback_list)

            model_trainer_artifact = ModelTrainerArtifacts(trained_model_path= self.training_config.TRAINED_MODEL_PATH)

            logging.info("Exited the initiate_model_training method of ModelTraining class")

            return model_trainer_artifact

            
        except Exception as e:
            raise CustomException