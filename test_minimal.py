# test_minimal.py
import requests

def test_connection():
    try:
        response = requests.get("http://localhost:8080")
        print(f"Connection successful! Status code: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Connection failed: {str(e)}")

if __name__ == "__main__":
    test_connection()