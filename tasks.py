import csv
import os
import requests
from tempfile import NamedTemporaryFile
from my_celery import celery_app
import logging


# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

blockfrost_api_key = os.environ.get("BLOCKFROST_API_KEY")
base_api = "https://cardano-mainnet.blockfrost.io/api/v0"

@celery_app.task
def generate_csv(policy_id):
    try:
        all_assets = []
        page = 1

        while True:
            response = requests.get(f'{base_api}/assets/policy/{policy_id}?page={page}', headers={"project_id": blockfrost_api_key})
            response.raise_for_status()  # Raise an exception for non-2xx response codes

            if len(response.json()) == 0:
                break

            for asset in response.json():
                temp = {}
                asset_hex_name = asset["asset"][int(len(str(policy_id))):]
                if all(c in "0123456789abcdefABCDEF" for c in asset_hex_name):
                    temp['name'] = bytearray.fromhex(asset_hex_name).decode()
                else:
                    temp['name'] = 'INVALID HEX STRING'
                temp['asset'] = asset['asset']
                all_assets.append(temp)
            page += 1

        address_assets = {}
        for asset in all_assets:
            response = requests.get(f'{base_api}/assets/{asset["asset"]}/addresses', headers={"project_id": blockfrost_api_key})
            response.raise_for_status()  # Raise an exception for non-2xx response codes

            for item in response.json():
                address = item['address']
                if address not in address_assets:
                    address_assets[address] = 1
                else:
                    address_assets[address] += 1

        data = []
        for address, num_assets in address_assets.items():
            data.append([address, num_assets])

        with NamedTemporaryFile(mode='w', delete=False, newline='') as temp_file:
            csv_writer = csv.writer(temp_file)
            csv_writer.writerow(['Address', 'Number of Assets'])
            csv_writer.writerows(data)

        return temp_file.name

    except Exception as e:
        logging.error(f'Error generating CSV: {str(e)}')
        raise
