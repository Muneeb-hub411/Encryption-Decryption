from flask import Flask, render_template, request, redirect, url_for
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import scrypt
from PIL import Image
import stepic
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
         

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        
        text = request.form['text']
        password = request.form['password']
        image = request.files['image']
        action = request.form['action']
        
        
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(image_path)
        
        
        if action == 'encrypt':
            print(f"Text: {text}")
            
            result = f"Encrypted text: {text}, password: {password}, image saved at: {image_path}"
            print(result)
        elif action == 'decrypt':
            
            result = f"Decrypted text: {text}, password: {password}, image saved at: {image_path}"
            print(result)
        else:
            result = "Reset the form"
            print(result)
        
        return render_template('index.html', result=result)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
