import requests

# Define the endpoints to test
endpoints = [
    "/",
    "/api/standings/basquet",
    "/api/standings/voley/tira-a",
    "/api/standings/voley/tira-b",
    "/api/standings/voley/primera",
    "/api/fixtures/voley/primera"
]

def test_endpoints():
    base_url = "http://localhost:8000"
    
    print("Testing API endpoints:")
    print("-" * 50)
    
    for endpoint in endpoints:
        url = base_url + endpoint
        print(f"Testing: {url}")
        
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print(f"✓ SUCCESS ({response.status_code})")
                # Print a brief sample of the response if it's valid JSON
                try:
                    data = response.json()
                    if isinstance(data, dict) and "error" in data:
                        print(f"  Error message: {data['error']}")
                    else:
                        print(f"  Response: {str(data)[:100]}...")
                except Exception:
                    print(f"  Response is not JSON or is empty")
            else:
                print(f"✗ FAILED ({response.status_code})")
                print(f"  Response: {response.text[:100]}...")
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_endpoints()
