import os
import time
import hmac
import hashlib
import requests
import json
from dotenv import load_dotenv

load_dotenv()

ACCESS_KEY = os.getenv("COUPANG_API_ACCESS_KEY")
SECRET_KEY = os.getenv("COUPANG_API_SECRET_KEY")

def generate_hmac(method, url, secret_key, access_key):
    datetime = time.strftime('%y%m%d') + 'T' + time.strftime('%H%M%S') + 'Z'
    message = datetime + method + url
    signature = hmac.new(bytes(secret_key, "utf-8"), message.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"CEA algorithm=HmacSHA256, access-key={access_key}, signed-date={datetime}, signature={signature}"

def get_coupang_deeplink(coupang_urls):
    if not isinstance(coupang_urls, list):
        coupang_urls = [coupang_urls]
        
    if not ACCESS_KEY or not SECRET_KEY:
        print("Error: COUPANG_API_ACCESS_KEY or COUPANG_API_SECRET_KEY not set")
        return None

    method = "POST"
    url = "/v2/providers/affiliate_open_api/apis/openapi/v1/deeplink"
    domain = "https://api-gateway.coupang.com"
    API_URL = domain + url
    
    authorization = generate_hmac(method, url, SECRET_KEY, ACCESS_KEY)
    headers = {
        "Authorization": authorization,
        "Content-Type": "application/json"
    }
    
    body = {
        "coupangUrls": coupang_urls
    }
    
    response = requests.post(API_URL, headers=headers, data=json.dumps(body))
    if response.status_code == 200:
        return response.json().get('data', [])
    else:
        print(f"Coupang API Error: {response.status_code} - {response.text}")
        return None
