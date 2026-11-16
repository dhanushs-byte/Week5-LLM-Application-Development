
import requests

url = "http://127.0.0.1:8000/chat/stream"

payload = {
    "prompt": "Explain Python in five sentences"
}

response = requests.post(
    url,
    json=payload,
    stream=True
)

print("Status:", response.status_code)

for line in response.iter_lines(decode_unicode=True):
    if line:
        print(line)
