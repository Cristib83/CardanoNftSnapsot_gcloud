import csv
import os
import requests
from flask import Flask, render_template, request, send_file
from io import StringIO

app = Flask(__name__, static_url_path='/static')

# Get the Blockfrost API key from the environment variable
blockfrost_api_key = os.environ.get("BLOCKFROST_API_KEY")
# Base API URL
base_api = "https://cardano-mainnet.blockfrost.io/api/v0"

def generate_csv(policy_id):
    try:
        all_assets = []
        page = 1

        while True:
            response = requests.get(f'{base_api}/assets/policy/{policy_id}?page={page}')
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
            response = requests.get(f'{base_api}/assets/{asset["asset"]}/addresses')
            for item in response.json():
                address = item['address']
                if address not in address_assets:
                    address_assets[address] = 1
                else:
                    address_assets[address] += 1

        data = []
        for address, num_assets in address_assets.items():
            data.append([address, num_assets])

        # Create a CSV file in memory using StringIO
        csv_file = StringIO()
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Address', 'Number of Assets'])
        csv_writer.writerows(data)
        csv_file.seek(0)  # Move the file pointer to the beginning of the file

        return csv_file.getvalue()

    except Exception as e:
        # Handle the exception appropriately
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_file', methods=['POST'])
def generate_file():
    policy_id = request.form['policy_id']
    csv_data = generate_csv(policy_id)

    # Send the CSV data as a download attachment
    return send_file(
        StringIO(csv_data),
        as_attachment=True,
        attachment_filename='data.csv',
        mimetype='text/csv'
    )

if __name__ == '__main__':
    # Run the Flask app
    app.run(debug=True, port=os.environ.get('PORT', 5000), host='0.0.0.0', threaded=True)
