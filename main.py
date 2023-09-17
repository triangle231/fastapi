from fastapi import FastAPI
from pydantic import BaseModel
import requests
import random
import json

app = FastAPI()

class Item(BaseModel):
    system: str
    user: str

@app.post("/api/gpt")
def makeGPT(item: Item):
    data = {
        "messages": [
            {
                "role": "system",
                "content": item.system
            },
            {
                "role": "user",
                "content": item.user
            }
        ],
        "stream": True,
        "model": "gpt-3.5-turbo",
        "temperature" :0.7,
        "presence_penalty" :0,
        "frequency_penalty" :0,
        'top_p': 1 
    }

    while True:
        urls = ["https://dongsiqie-gpt35.hf.space/api/openai/v1/chat/completions", 
                'https://mikunakanoyyds-gptnextweb.hf.space/api/openai/v1/chat/completions']
                
        url = random.choice(urls)

        response = requests.post(url, data=json.dumps(data), stream=True)

        allResult = ""

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
                            allResult += content
                        
                        json_buffer = ''
                        
                    except json.JSONDecodeError:
                        pass
        
                    
        
       if len(allResult) > 0:
           break
    
    return {"response": allResult}
