import os
from flask import Flask, request, send_file, render_template
from cryptography.fernet import Fernet

app = Flask(__name__)

# Path to store encryption key
KEY_PATH = 'secret.key'

# Generate or load the encryption key
def load_key():
    if os.path.exists(KEY_PATH):
        with open(KEY_PATH, 'rb') as key_file:
            return key_file.read()
    else:
        key = Fernet.generate_key()
        with open(KEY_PATH, 'wb') as key_file:
            key_file.write(key)
        return key

# Encrypt file
def encrypt_file(file_path):
    key = load_key()
    fernet = Fernet(key)

    with open(file_path, 'rb') as file:
        original_data = file.read()

    encrypted_data = fernet.encrypt(original_data)

    encrypted_file_path = file_path + '.enc'
    with open(encrypted_file_path, 'wb') as enc_file:
        enc_file.write(encrypted_data)

    return encrypted_file_path

# Decrypt file
def decrypt_file(file_path):
    key = load_key()
    fernet = Fernet(key)

    with open(file_path, 'rb') as enc_file:
        encrypted_data = enc_file.read()

    decrypted_data = fernet.decrypt(encrypted_data)

    decrypted_file_path = file_path.replace('.enc', '')
    
    with open(decrypted_file_path, 'wb') as dec_file:
        dec_file.write(decrypted_data)

    return decrypted_file_path

# Route for uploading and processing the file
@app.route('/upload', methods=['POST'])
def upload_file():
    action = request.form['action']
    user = request.form['user']
    file = request.files['file']

    if not file:
        return "No file uploaded", 400

    # Set up directory for each user
    file_path = os.path.join('uploads', user, file.filename)
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    file.save(file_path)

    # Encrypt or decrypt based on action
    if action == 'encrypt':
        result_file_path = encrypt_file(file_path)
    elif action == 'decrypt':
        if file.filename.endswith('.enc'):
            result_file_path = decrypt_file(file_path)
        else:
            return "Invalid file format for decryption", 400

    return send_file(result_file_path, as_attachment=True)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
