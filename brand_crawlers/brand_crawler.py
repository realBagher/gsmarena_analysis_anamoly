import random
import requests
from bs4 import BeautifulSoup
import time
from fake_useragent import UserAgent
import csv
import json

BRAND_NAME = 'Alcatel'

with open('proxies.csv', 'r') as f:
    csv_reader = csv.reader(f)
    ips = list(csv_reader)

ip_addresses = [ip[0] for ip in ips]

session = requests.Session()


def proxy_request(url, ip_addresses):
    while True:
        try:
            ua = UserAgent()
            headers = {"Accept-Language": "en-US,en;q=0.5",
                       'User-Agent': ua.random}
            proxy = random.randint(0, len(ip_addresses) - 1)
            proxies = {"http": ip_addresses[proxy]}
            response = session.get(url, proxies=proxies,
                                   timeout=5, headers=headers)
            if response.status_code == 200:
                break
            elif response.status_code == 429:
                print(f"Rate limit exceeded. Waiting before retrying...")
                time.sleep(10)
            else:
                print(
                    f"Request failed with status code: {response.status_code}")
                time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"Error: {e}")

    return response


file_path = 'urls.json'

brand_list = [
    # 'Apple118',  ##--> Done
    # 'Samsung1383',  ##--> Done
    # 'Xiaomi377',  ##--> Done
    # 'Huawei441',  ##--> Done
    'alcatel409',
    # 'Sony',
    # 'Sony158',
    # 'LG667',
    # 'Lenovo246',
    # 'ZTE369',
    # 'Nokia576',
    # 'BLU369',
    # 'Infinix125',
    # 'HTC287',
    # 'Asus203',
]

maker_brands = {}

with open(file_path, 'r') as json_file:
    maker_brands = json.load(json_file)


info_dict_with_headers = {}

for brand in maker_brands:
    if brand in brand_list:
        info_dict_with_headers[brand] = {}
        for device in maker_brands[brand]:
            print(device)
            url = maker_brands[brand][device]
            # url = url.replace('https://www.gsmarena.com/makers.php3', 'https://www.gsmarena.com/makers.php3/')
            time.sleep(3)
            response = proxy_request(url, ip_addresses)
            soup = BeautifulSoup(response.content, 'html.parser')
            table_list = soup.find_all('table')
            info_dict_with_headers[brand][device] = {}

            for table in table_list:
                # Attempt to find the table header
                header = table.find('th')
                if header:
                    header_text = header.get_text(strip=True)
                else:
                    # If no <th> is found, or there is a need to identify the header differently, adjust here
                    header_text = "Unknown"  # Placeholder if no header is found or defined differently

                # Initialize the dictionary for this header if not already present
                if header_text not in info_dict_with_headers:
                    info_dict_with_headers[brand][device][header_text] = []

                last_key = None  # Keep track of the last non-empty key for rows without a 'ttl'

                # Iterate through each row in the table
                for row in table.find_all('tr'):
                    ttl_element = row.find("td", class_="ttl")
                    nfo_element = row.find("td", class_="nfo")

                    if ttl_element and ttl_element.get_text(strip=True):
                        # If ttl_element has text, update last_key
                        key = ttl_element.get_text(strip=True)
                        last_key = key
                    else:
                        # If ttl_element is empty, use the last_key
                        key = last_key

                    if nfo_element:
                        value = nfo_element.get_text(strip=True)
                        # Append the key-value pair under the current header
                        if key:
                            info_dict_with_headers[brand][device][header_text].append({
                                                                                      key: value})
                        else:
                            # Handle case where there's a value without a key (could append to last key's value or handle as needed)
                            pass

            print(f'{device} Done!')
        print(f'{brand} Done!')
    else:
        continue

file_path = f'{BRAND_NAME}_data.json'
with open(file_path, 'w') as json_file:
    json.dump(info_dict_with_headers, json_file)
