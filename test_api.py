import requests
import json
from datetime import datetime

class APITester:
    def __init__(self, base_url="http://localhost:8080"):
        self.base_url = base_url
        self.token = None
        self.test_results = []
    
    def log_result(self, test_name, success, message, response=None):
        result = {
            'test_name': test_name,
            'success': success,
            'message': message,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'response': response.json() if response else None
        }
        self.test_results.append(result)
        status = "✅" if success else "❌"
        print(f"{status} {test_name}: {message}")

    def register_user(self, username, password):
        try:
            response = requests.post(
                f"{self.base_url}/register",
                json={
                    "username": username,
                    "password": password
                }
            )
            success = response.status_code == 200
            self.log_result(
                "User Registration",
                success,
                "Registration successful" if success else f"Failed: {response.text}",
                response
            )
            return success
        except Exception as e:
            self.log_result("User Registration", False, f"Error: {str(e)}")
            return False

    def login_user(self, username, password):
        try:
            # Login now uses form data
            response = requests.post(
                f"{self.base_url}/token",
                data={
                    "username": username,
                    "password": password,
                    "grant_type": "password"
                }
            )
            success = response.status_code == 200
            if success:
                self.token = response.json()["access_token"]
                self.log_result("User Login", True, "Login successful", response)
                return True
            else:
                self.log_result("User Login", False, f"Failed: {response.text}", response)
                return False
        except Exception as e:
            self.log_result("User Login", False, f"Error: {str(e)}")
            return False

    def test_chat(self, message):
        if not self.token:
            self.log_result("Chat Test", False, "No authentication token available")
            return False

        try:
            headers = {
                'Authorization': f'Bearer {self.token}',
                'Content-Type': 'application/json'
            }
            response = requests.post(
                f"{self.base_url}/chat",
                params={"message": message},  # Changed to params for query parameter
                headers=headers
            )
            success = response.status_code == 200
            self.log_result(
                "Chat Test",
                success,
                "Chat response received" if success else f"Failed: {response.text}",
                response
            )
            return success
        except Exception as e:
            self.log_result("Chat Test", False, f"Error: {str(e)}")
            return False

    def run_all_tests(self):
        print("\n🔍 Starting API Tests...\n")
        
        # Test user registration
        username = "testuser"
        password = "testpass123"
        self.register_user(username, password)
        
        # Test login
        self.login_user(username, password)
        
        # Test chat functionality
        self.test_chat("What are the environmental guidelines for waste management?")
        
        # Print summary
        print("\n📊 Test Summary:")
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results if result['success'])
        print(f"Total Tests: {total_tests}")
        print(f"Successful: {successful_tests}")
        print(f"Failed: {total_tests - successful_tests}")

def main():
    tester = APITester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()