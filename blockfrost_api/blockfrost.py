import requests
import csv
import string
import os


blockfrost_api_key = "mainnetrrIj9ITzGOUadlPSyj1D700VwSQhAmle"
#os.environ.get("BLOCKFROST_API_KEY")
project_policy_id = input('policy_id: ')

base_api = "https://cardano-mainnet.blockfrost.io/api/v0"
headers = {'project_id': blockfrost_api_key}

# Retrieve all assets for the given policy
all_assets = []
page = 1

while True:
    response = requests.get(f'{base_api}/assets/policy/{project_policy_id}?page={page}', headers=headers)

    if len(response.json()) == 0:
        break

    for asset in response.json():
        temp = {}
        asset_hex_name = asset["asset"][len(project_policy_id):]
        if all(c in "0123456789abcdefABCDEF" for c in asset_hex_name):
            temp['name'] = bytearray.fromhex(asset_hex_name).decode()
        else:
            temp['name'] = 'INVALID HEX STRING'
        temp['asset'] = asset['asset']
        all_assets.append(temp)

    page += 1

# Retrieve all addresses for each asset
address_assets = {}
for asset in all_assets:
    response = requests.get(f'{base_api}/assets/{asset["asset"]}/addresses', headers=headers)
    for item in response.json():
        address = item['address']
        if address not in address_assets:
            address_assets[address] = 1
        else:
            address_assets[address] += 1

# Write data to File1.csv
data1 = []
for address, num_assets in address_assets.items():
    data1.append([address, num_assets])

with open('File1.csv', 'w', newline='') as file:
    csv_writer = csv.writer(file)
    csv_writer.writerow(['Address', 'Number of Assets'])
    csv_writer.writerows(data1)
