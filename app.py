from flask import Flask, render_template, request
import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
import base64
from PIL import Image
import stepic

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['STEG_FOLDER'] = 'stenography/'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['STEG_FOLDER'], exist_ok=True)

def derive_key(password):
    salt = b'salt_'  # This should be random and saved securely
    key = PBKDF2(password, salt, dkLen=32, count=1000000)
    return key

def encrypt(msg, key):
    cipher = AES.new(key, AES.MODE_EAX)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(msg.encode('ascii'))
    return base64.b64encode(nonce + tag + ciphertext).decode('utf-8')

def decrypt(encrypted_text, key):
    encrypted_data = base64.b64decode(encrypted_text)
    nonce = encrypted_data[:16]
    tag = encrypted_data[16:32]
    ciphertext = encrypted_data[32:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    try:
        cipher.verify(tag)
        return plaintext.decode('ascii')
    except ValueError:
        return "Key incorrect or message corrupted"

@app.route('/', methods=['GET', 'POST'])
def index():
    result = None
    if request.method == 'POST':
        password = request.form['password']
        image = request.files['image']
        action = request.form['action']
        key = derive_key(password)

        image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
        image.save(image_path)
        
        if action == 'encrypt':
            text = request.form['text']
            encrypted_text = encrypt(text, key)
            img = Image.open(image_path)
            steg_img = stepic.encode(img, encrypted_text.encode('utf-8'))
            steg_image_path = os.path.join(app.config['STEG_FOLDER'], image.filename)
            steg_img.save(steg_image_path, 'PNG')
            result = f"Encrypted text embedded in image, saved at: {steg_image_path}"
        
        elif action == 'decrypt':
            img = Image.open(image_path)
            encrypted_text = stepic.decode(img)
            decrypted_text = decrypt(encrypted_text, key)
            result = f"Decrypted text: {decrypted_text}, image saved at: {image_path}"
        
        else:
            result = "Reset the form"
        
        return render_template('index.html', result=result)
    
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
