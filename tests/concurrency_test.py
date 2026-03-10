import requests
import concurrent.futures

TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlNTM3ZGFjZC1kOTYxLTQ3ZjYtOTA1Mi0zOWQ3Yzc0ZjMwNjQiLCJleHAiOjE3NzMxNDE2NDR9.vusMCgGJ35zsOLfK7WYvad0AYSy1Ie3OTVdPAC1Lrxc"

URL = "http://127.0.0.1:8000/wallet/debit"

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