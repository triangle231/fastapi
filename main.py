from fastapi import FastAPI, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import json
import random

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://port-0-fastapi-4fju66f2clmmw02om.sel5.cloudtype.app/"],  # 실제 웹 페이지의 도메인으로 변경해야 합니다.
    allow_methods=["POST"],  # POST 요청만 허용합니다.
    allow_headers=["*"],
)

class UserInput(BaseModel):
    system: str
    user: str

@app.post("/makeGPT/")
def make_gpt(input_data: UserInput):
    data = {
        "messages": [
            {
                "role": "system",
                "content": input_data.system
            },
            {
                "role": "user",
                "content": input_data.user
            }
        ],
        "stream": True,
        "model": "gpt-3.5-turbo",
        "temperature": 0.7,
        "presence_penalty": 0,
        "frequency_penalty": 0,
        "top_p": 1 
    }

    while True:
        urls = ["https://dongsiqie-gpt35.hf.space/api/openai/v1/chat/completions", "https://mikunakanoyyds-gptnextweb.hf.space/api/openai/v1/chat/completions"]
        url = random.choice(urls)

        response = requests.post(url, data=json.dumps(data), stream=True)

        all_result = ""

        json_buffer = ''
        for line in response.iter_lines():
            if line:
                decoded_line = line.decode('utf-8')
                if decoded_line.startswith('data:'):
                    json_buffer += decoded_line[6:]
                    try:
                        json_line = json.loads(json_buffer)
                        content = json_line.get('choices', [{}])[0].get('delta', {}).get('content')
                        if content:
                            all_result = all_result + content
                        json_buffer = ''
                    except json.JSONDecodeError:
                        pass
        if len(all_result) < 1:
            continue
        break
    return {"response": all_result}
