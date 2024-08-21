from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import os
import random

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        try:
            df = pd.read_excel(file)
            if 'Contact' not in df.columns:
                return jsonify({'error': 'The Excel file must contain a "Contact" column.'}), 400
            contacts = df['Contact'].tolist()
            return jsonify(contacts)
        except Exception as e:
            return jsonify({'error': str(e)}), 400

@app.route('/send', methods=['POST'])
def send_message():
    data = request.json
    contacts = data['contacts']
    message = data['message']
    media_filename = data.get('media_path')
    
    media_path = None
    if media_filename:
        media_path = os.path.abspath(os.path.join(UPLOAD_FOLDER, media_filename))
    
    chrome_driver_path = r'C:\Users\sales\.wdm\drivers\chromedriver\win64\127.0.6533.119\chromedriver-win64\chromedriver.exe'
    chrome_service = Service(chrome_driver_path)
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=chrome_service, options=chrome_options)
    
    driver.get('https://web.whatsapp.com')
    
    input("Press Enter after scanning QR code")
    
    for contact in contacts:
        try:
            search_box = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="3"]'))
            )
            search_box.clear()
            search_box.send_keys(contact)
            search_box.send_keys(Keys.RETURN)
            
            time.sleep(random.uniform(2, 4))
            
            if message:
                message_box = WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"][@data-tab="10"]'))
                )
                words = message.split()
                for word in words:
                    message_box.send_keys(word + " ")
                    time.sleep(random.uniform(0.1, 0.3))
                message_box.send_keys(Keys.RETURN)
            
            if media_path:
                try:
                    send_media(driver, media_path, contact)
                except Exception as e:
                    print(f"Error sending media to {contact}: {str(e)}")
                    continue  # Continue to next contact on error
            
            time.sleep(random.uniform(5, 10))
        
        except Exception as e:
            print(f"Error processing contact {contact}: {str(e)}")
            continue  # Continue to next contact on error
    
    driver.quit()
    return jsonify({'status': 'success'})

def send_media(driver, media_path, contact):
    retry_attempts = 3
    for attempt in range(retry_attempts):
        try:
            # Wait for the chat to load
            WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//div[@data-tab="10"]'))
            )

            # Click the attach button (paper clip icon)
            parent_div_xpath = '//*[@id="main"]/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/div'
            attach_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, parent_div_xpath))
            )
            driver.execute_script("arguments[0].click();", attach_btn)

            # Wait for the hidden input to be available and send the media path
            hidden_input_xpath = '/html/body/div[1]/div/div/div[2]/div[4]/div/footer/div[1]/div/span[2]/div/div[1]/div[2]/div/span/div/ul/div/div[2]/li/div/input'
            file_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, hidden_input_xpath))
            )
            file_input.send_keys(media_path)

            # Wait for the media to be uploaded and the send button to be clickable
            send_button_selector = 'span[data-icon="send"]'
            send_btn = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, send_button_selector))
            )

            # Use JavaScript to click the send button
            driver.execute_script("arguments[0].click();", send_btn)

            # Wait for the message to be sent
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//span[@data-icon="msg-time"] | //span[contains(@aria-label, "Sent")]'))
            )

            print(f"Media sent successfully to {contact}")
            break  # Exit the loop if successful
        except Exception as e:
            print(f"Failed to send media to {contact}, attempt {attempt + 1} of {retry_attempts}: {str(e)}")
            if attempt == retry_attempts - 1:  # Last attempt
                raise

    # Add a delay after sending to avoid rate limiting
    time.sleep(random.uniform(3, 5))



@app.route('/upload_media', methods=['POST'])
def upload_media():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        return jsonify({'filename': file.filename}), 200
    return jsonify({'error': 'File upload failed'}), 400

if __name__ == '__main__':
    app.run(debug=True)
