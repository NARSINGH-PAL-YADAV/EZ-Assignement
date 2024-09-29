from fastapi import FastAPI, HTTPException
import requests
import redis
import json

app = FastAPI()


redis_client = redis.StrictRedis(host="redis", port=6379, db=0, decode_responses=True)


TF_SERVING_URL = "http://llm-service/v1/models/my-llm-model:predict"

@app.post("/chat")
async def chat(request: dict):
    user_input = request.get("input")
    if not user_input:
        raise HTTPException(status_code=400, detail="Input not provided")

   
    cached_response = redis_client.get(user_input)
    if cached_response:
        return {"response": cached_response}

   
    payload = {"instances": [{"input": user_input}]}
    response = requests.post(TF_SERVING_URL, json=payload)

    if response.status_code == 200:
        prediction = response.json()["predictions"][0]
        redis_client.set(user_input, prediction, ex=3600) 
        return {"response": prediction}
    else:
        raise HTTPException(status_code=500, detail="Model inference failed")
