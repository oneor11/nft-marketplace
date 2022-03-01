import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

json_headers = {
    "Content-Type": "application/json",
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY")
}

file_headers = {
    "pinata_api_key": os.getenv("PINATA_API_KEY"),
    "pinata_secret_api_key": os.getenv("PINATA_SECRET_API_KEY")
}

def pin_artwork(artwork_file):
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(artwork_file.getvalue())
    ipfs_file_hash = f"ipfs://{ipfs_file_hash}"
    return ipfs_file_hash

def convert_data_to_json(content):
    data = {"pinataOptions": {"cidVersion": 1}, "pinataContent": content}
    return json.dumps(data)

def pin_file_to_ipfs(data):
    r = requests.post(
        "https://api.pinata.cloud/pinning/pinFileToIPFS",
        files={"file": data},
        headers=file_headers
    )
    print(r.json())
    ipfs_hash = r.json()["IpfsHash"]
    return ipfs_hash

def pin_json_to_ipfs(json):
    r = requests.post(
        "https://api.pinata.cloud/pinning/pinJSONToIPFS",
        data=json,
        headers=json_headers
    )
    print(r.json())
    ipfs_hash = r.json()["IpfsHash"]
    return ipfs_hash

def get_pins():
    r = requests.get(
        "https://api.pinata.cloud/data/pinList",
        headers=json_headers
    )
    pin_hashes = r.json()["rows"]
    my_list = []
    for row in pin_hashes:
        if(row['ipfs_pin_hash'].startswith('Qm')):
            my_list.append(f"https://gateway.pinata.cloud/ipfs/{row['ipfs_pin_hash']}")
    return my_list
