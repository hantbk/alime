import requests
import time

def find_max_page(base_url, headers):
    low, high = 0, 100000
    while low <= high:
        mid = (low + high) // 2
        response = requests.get(base_url + str(mid * 50), headers=headers, timeout=10)
        if response.status_code == 200:
            low = mid + 1
        else:
            high = mid - 1
        time.sleep(1)
    return high * 50