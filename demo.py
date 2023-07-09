import sys
from vnpd.exception import CustomException
from vnpd.logger import logging
from vnpd.pipeline.train_pipeline import TrainPipeline

train_obj = TrainPipeline()
train_obj.run_pipeline()