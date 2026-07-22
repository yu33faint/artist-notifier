import os

from fastapi import Header, HTTPException


def verify_api_key(x_api_key: str = Header(...)):
    expected_key = os.getenv("API_KEY")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="APIキーが正しくありません。")
