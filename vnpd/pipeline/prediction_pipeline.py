import os, sys, shutil
import cv2
import numpy as np
from vnpd.logger import logging
from vnpd.exception import CustomException
from vnpd.entity.config_entity import *

import tensorflow as tf
from keras.utils.image_utils import load_img, img_to_array
from vnpd.entity.artifacts_entity import *
from paddleocr import PaddleOCR,draw_ocr
from PIL import Image
from vnpd.config.s3_operations import S3Operation

def object_detection(path, filename,model):
    logging.info("Entered the object_detection method")
    # Read image
    image = load_img(path)  # PIL object
    image = np.array(image, dtype=np.uint8)  # 8 bit array (0,255)
    image1 = load_img(path, target_size=(224, 224))
    # Data preprocessing
    # Convert into array and get the normalized output
    image_arr_224 = img_to_array(image1)/255.0
    h, w, d = image.shape
    test_arr = image_arr_224.reshape(1, 224, 224, 3)
    # Make predictions
    coords = model.predict(test_arr)
    logging.info("Model prediction successfull")
    # Denormalize the values
    denorm = np.array([w, w, h, h])
    coords = coords * denorm
    coords = coords.astype(np.int32)
    # Draw bounding on top the image
    xmin, xmax, ymin, ymax = coords[0]
    pt1 = (xmin, ymin)
    pt2 = (xmax, ymax)
    print(pt1, pt2)
    cv2.rectangle(image, pt1, pt2, (0, 255, 0), 3)
    # Convert into bgr
    image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    prediction_img_path = os.path.join(os.getcwd(), STATIC_DIR, PREDICT_SUB_DIR)
    shutil.rmtree(prediction_img_path)
    os.makedirs(prediction_img_path, exist_ok=True)
    logging.info(f"Created {os.path.basename(prediction_img_path)} directory.")
    prediction_img_path = os.path.join(os.getcwd(), STATIC_DIR, PREDICT_SUB_DIR, filename)
    cv2.imwrite(prediction_img_path, image_bgr)
    return coords

def Optical_character_recognition(path, filename):
    model_path = os.path.join(os.getcwd(), STATIC_DIR, 'model')
    #shutil.rmtree(model_path)
    os.makedirs(model_path, exist_ok=True)
    model_path = os.path.join(os.getcwd(), STATIC_DIR, 'model', 'model.h5')
    s3_operation = S3Operation()
    fetch_model = s3_operation.load_h5_model(bucket_name=BUCKET_NAME,object_file_name=TRAINED_MODEL,local_file_name=model_path)
    #fetch_model = tf.keras.models.load_model(fetch_model)
    logging.info(f"Loaded {fetch_model} model from S3 bucket.")
    #model_path = os.path.join(os.getcwd(), STATIC_DIR, 'model', 'model.h5')
    
    cods = object_detection(path=path, filename=filename, model=fetch_model)
    print(cods)
    
    img = np.array(load_img(path))
    xmin, xmax, ymin, ymax = cods[0]
    roi = img[ymin:ymax, xmin:xmax]
    roi_bgr = cv2.cvtColor(roi, cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(roi_bgr, cv2.COLOR_BGR2GRAY)
    
    roi_img_path = os.path.join(os.getcwd(), STATIC_DIR, ROI_SUB_DIR)
    shutil.rmtree(roi_img_path)
    os.makedirs(roi_img_path, exist_ok=True)
    roi_img_path = os.path.join(os.getcwd(), STATIC_DIR, ROI_SUB_DIR, filename)
    cv2.imwrite(roi_img_path, roi_bgr)
    #magic_color = apply_brightness_contrast(gray, brightness=40, contrast=70)
    ocr = PaddleOCR(use_angle_cls=True, lang='en') # need to run only once to download and load model into memory
    result = ocr.ocr(roi_img_path, cls=True)
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            print(line)
    result = result[0]
    image = Image.open(roi_img_path).convert('RGB')
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    font_path = os.path.join(os.getcwd(), 'simfang.ttf')
    im_show = draw_ocr(image, boxes, txts, scores, font_path=font_path)
    im_show = Image.fromarray(im_show)
    ocr_result_img_path = os.path.join(os.getcwd(), STATIC_DIR, OCR_SUB_DIR)
    shutil.rmtree(ocr_result_img_path)
    os.makedirs(ocr_result_img_path, exist_ok=True)
    
    
    ocr_result_img_path = os.path.join(os.getcwd(), STATIC_DIR, OCR_SUB_DIR, filename)
    im_show.save(ocr_result_img_path)
    
    return ''