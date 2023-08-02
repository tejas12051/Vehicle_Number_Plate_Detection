import os, shutil
from flask import Flask, render_template,request
from vnpd.constant import *
from vnpd.pipeline.prediction_pipeline import Optical_character_recognition

app = Flask(__name__)

@app.route('/',methods= ['GET'])
def land():
    return render_template("landing_page.html")

@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'POST':
        upload_file =request.files['fileup']
        filename = upload_file.filename
        #model_path = os.path.join(os.getcwd(), STATIC_DIR, 'model')
        #shutil.rmtree(model_path)
        #os.makedirs(model_path, exist_ok=True)
        #model_path = os.path.join(os.getcwd(), STATIC_DIR, 'model', 'model.h5')
        #fetch_model = tf.keras.models.load_model(model_path)

        upload_img_path = os.path.join(os.getcwd(),STATIC_DIR,UPLOAD_SUB_DIR)
        shutil.rmtree(upload_img_path)
        os.makedirs(upload_img_path,exist_ok=True)
        upload_img_path = os.path.join(os.getcwd(),STATIC_DIR,UPLOAD_SUB_DIR,filename)
        upload_file.save(upload_img_path)
        text = Optical_character_recognition(upload_img_path, filename)
        
        return render_template('index.html', upload=True, upload_image=filename, text=text)

    return render_template("index.html")

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
