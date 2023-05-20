import csv
import os
import requests
from tempfile import NamedTemporaryFile
from flask import Flask, render_template, request, send_file, jsonify
from my_celery import celery_app


app = Flask(__name__, static_url_path='/static')

blockfrost_api_key = os.environ.get('BLOCKFROST_API_KEY')
base_api = "https://cardano-mainnet.blockfrost.io/api/v0"

@celery_app.task
def get_csv_files(policy_id):
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

    with NamedTemporaryFile(mode='w', delete=False, newline='') as temp_file:
        csv_writer = csv.writer(temp_file)
        csv_writer.writerow(['Address', 'Number of Assets'])
        csv_writer.writerows(data)

    return temp_file.name


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_file', methods=['POST'])
def generate_file():
    policy_id = request.form['policy_id']
    result = get_csv_files.delay(policy_id)
    return jsonify({'task_id': result.id})

@app.route('/download_file/<task_id>')
def download_file(task_id):
    result = get_csv_files.AsyncResult(task_id)
    if result.ready():
        temp_file_path = result.get()
        filename = f"{task_id}.csv"
        return send_file(temp_file_path, as_attachment=True, attachment_filename=filename)
    else:
        return "Processing...", 202


if __name__ == '__main__':
    app.run(debug=True, port=os.environ.get('PORT', 5000), host='0.0.0.0', threaded=True)
