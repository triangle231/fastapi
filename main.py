from selenium import webdriver
from selenium.webdriver.common.by import By
import time
from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
import re
import threading
import os
import requests
import json
import time
from PIL import Image
from io import BytesIO

name = ""

id = "painto"
password = "vpdlsxh123"

driver = ""
element = ""
elements2 = ""
elements3 = ""

headers = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "ko,en;q=0.9,en-US;q=0.8",
    "Content-Type": "application/json",
    "Origin": "https://www.miricanvas.com",
    "Referer": "https://www.miricanvas.com/",
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
}

def send_image(image_url):
    # Download the image from the url
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    
    # Get original image format
    img_format = img.format

    # Reduce image size until it's less than 1MB
    while len(img.tobytes()) > 1024 * 1024:
        width, height = img.size
        img = img.resize((int(width * 0.9), int(height * 0.9)))

    # Save the reduced image to a BytesIO object with original format 
    reduced_image_data = BytesIO()
    img.save(reduced_image_data, format=img_format)
    reduced_image_data.seek(0)   # Move cursor to start of file

    # Define the upload url and headers
    upload_url= "https://playentry.org/rest/picture"
    
	# Create a tuple for the file data (filename, bytes content, MIME type)
    file_tuple = ("image.jpg", reduced_image_data.getvalue(), f"image/{img_format.lower()}")
	
	# Create files dictionary for requests.post method 
    files={"file": file_tuple}
	
    data={"type": "notcompress"}

	# Send a POST request to upload the image
    response_upload=requests.post(upload_url, files=files, data=data)

    try:
        if response_upload.status_code == 201:
            res_json = response_upload.json()
            return f"https://playentry.org/uploads/{res_json['filename'][:2]}/{res_json['filename'][2:4]}/{res_json['filename']}.{res_json['imageType']}"
        else:
            return None
    except Exception as e:
        return None

def makeAi_image(prompt):
    # 데이터 설정
    data = {
    "prompt1": prompt,
    "presetKey": "normal",
    'auth': 9111150,
    }

    url = "https://aicreation.miricanvas.com/api/text-to-image"

    # POST 요청 전송
    response = requests.post(url, data=json.dumps(data), headers=headers)

    uuid = response.json()['uuid']

    url_count = 0

    url = f"https://aicreation.miricanvas.com/api/text-to-image/polling?id={uuid}"

    all_result = ""
    while True:
        # GET 요청 전송
        response = requests.get(url, headers=headers)

        data = response.json()

        # URL 개수 확인 
        try:
            url_count = sum('result' in task and 'url' in task['result'] for item in data['list'] for task in item['taskList'])
        except TypeError:
            url_count = 0  # or whatever default value you want to use

        if url_count == 4: 
            # 변경된 부분: URL이 정확히 4개일 때 각각의 URL을 출력하고 send_image 함수를 호출합니다.
            urls = [task['result']['url'] for item in data['list'] for task in item['taskList'] if 'result' in task and 'url' in task['result']]
            for url in urls:
                all_result = all_result + send_image(url) + " "
            break

        time.sleep(1)

    return all_result

#아래 코드수정으로 명령어 추가, 제거
def question():
    global name
    if element.text == name + "안녕":
        makeComments(driver, "안녕하세요!")
    if element.text.startswith(name + "test"):
        expression = element.text[len(name + "test"):].strip()
        makeLike(driver)
        makeComments(driver, elements2[0].text.split('\n')[0] + expression)
    # 봇 호출 반응
    #if "봇" in element.text:
    #    makeComments(0, driver, "누구인가 누가 내이름을 불렀는가👂")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#만약 글을 쓰고 싶으면 아래 함수를 쓰세요.
def makeCommunity(driver, content):
    textarea_element = driver.find_element(By.ID, "Write")
    textarea_element[0].clear()
    textarea_element[0].send_keys(content)
    a_elements = driver.find_elements(By.CSS_SELECTOR, ".css-10xvtsb.e1h77j9v8")
    a_elements[0].click()

def makeComments(driver, content):
    reply_elements = driver.find_elements(By.CSS_SELECTOR, "a.reply")
    reply_elements[0].click()

    textarea_element = driver.find_elements(By.ID, "Write")
    textarea_element[1].clear()
    textarea_element[1].send_keys(content)
    a_elements = driver.find_elements(By.CSS_SELECTOR, ".css-10xvtsb.e1h77j9v8")
    a_elements[1].click()
    print("ㄴ " + content)
    reply_elements = driver.find_elements(By.CSS_SELECTOR, "a.reply")
    reply_elements[0].click()

def makeLike(driver):
    like_elements = driver.find_elements(By.CSS_SELECTOR, "a.like")
    like_elements[0].click()

running = False

@app.get("/")
def main():
    global running

    if not running:
        running = True
        thread = threading.Thread(target=main_func)
        thread.start()
        return "봇 동작중..."
    else:
        return "이미 봇이 동작중입니다."

def main_func():
    global id
    global password
    global driver
    global element
    global elements2
    global elements3

    print("시작")
    
    driver = webdriver.Chrome()
    driver.implicitly_wait(10)
    
    print("로그인중...")
    
    driver.get("https://playentry.org/signin")
    
    username_field = driver.find_element(By.ID, "username")
    username_field.send_keys(id)
    password_field = driver.find_element(By.ID, "password")
    password_field.send_keys(password)

    login_button = driver.find_element(By.CSS_SELECTOR, ".css-1cooiky.e13821ld0")
    login_button.click()
    
    time.sleep(2)
    
    print("로그인 완료!")
    
    driver.get("https://playentry.org/community/entrystory/list?sort=created&term=all")

    last = "3asef!@#"

    while True:
        try:
            driver.refresh()
    
            elements = driver.find_elements(By.CSS_SELECTOR, ".css-sy8ihv")
            elements2 = driver.find_elements(By.CSS_SELECTOR, ".css-1t19ptn")
            elements3 = driver.find_elements(By.CSS_SELECTOR, ".css-18bdrlk")

            if True:
                element = elements[0]
                if not last == elements2[0].text + " + " + elements[0].text + " + " + elements3[0].text:
                    print("")
                    print(element.text + "\n" + elements2[0].text)
                    if element.text.startswith("페인토 그려줘 "):
                        _, next_string = element.text.split("페인토 그려줘 ", 1)
                        makeLike(driver)
                        Images = makeAi_image(next_string)
                        makeComments(driver, elements2[0].text.split('\n')[0] + "님, 요청하신 그림입니다. " + Images)
                last = elements2[0].text + " + " + elements[0].text + " + " + elements3[0].text
            time.sleep(0.2)
        except Exception as e:
            print(f"에러가 발생했습니다: {str(e)}")
    driver.quit()
    pass
