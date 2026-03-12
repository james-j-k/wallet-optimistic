import requests
import concurrent.futures

#Paste your JWT token here
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYWVjNTU2Yy1lOTk3LTQyNDItOTU5Ni02YjI1OGQyNmI2MzUiLCJleHAiOjE3NzMzMDI3Mjd9.TFpeemqkHNdAliwLA1XaSSwqgJq4wA7-mLBDwRRGtRk"

URL = "http://127.0.0.1:8000/wallet/credit"

headers = {
    "Authorization": f"Bearer {TOKEN}"
}

def make_request():
    try:
        response = requests.post(
            URL,
            json={"amount": 10},
            headers=headers
        )
        return response.status_code
    except Exception as e:
        print("Request error:", e)
        return None


if __name__ == "__main__":
    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(make_request) for _ in range(50)]
        results = [f.result() for f in futures]

    print("All status codes:", results)
    print("Success:", results.count(200))
    print("Failed (400):", results.count(400))
    print("Other errors:", len(results) - results.count(200) - results.count(400))