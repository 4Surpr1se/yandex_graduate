import time
import requests
from settings import test_settings

if __name__ == '__main__':
    max_wait_time = 60
    start_time = time.time()

    while True:
        try:
            response = requests.get(test_settings.auth_service_url)
            if response.status_code == 200:
                print("Auth service is up and running.")
                break
        except requests.ConnectionError:
            pass
        
        if time.time() - start_time > max_wait_time:
            print("Timeout: Could not connect to auth service within the allowed time.")
            break
        
        time.sleep(1)
