import os
import json
from hexbytes import HexBytes
from web3 import Web3
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

from pinata import get_pins, pin_file_to_ipfs, pin_json_to_ipfs, convert_data_to_json

load_dotenv()

# Define and connect a new Web3 provider
w3 = Web3(Web3.HTTPProvider(os.getenv("WEB3_PROVIDER_URI")))

###################################################################################################
# Contract Helper Function:
# 1. Loads the contract once using cache
# 2. Connects to the contract using the contract address and ABI
###################################################################################################

def load_contract(abi_file_path, contract_address):

    # Load the contract ABI
    with open(Path(abi_file_path)) as f:
        contract_abi = json.load(f)

    # Get the contract
    contract = w3.eth.contract(
        address=contract_address,
        abi=contract_abi
    )

    return contract


def pin_artwork(artwork_file):
    # Pin the file to IPFS with Pinata
    ipfs_file_hash = pin_file_to_ipfs(artwork_file.getvalue())

    return ipfs_file_hash


# Load the contracts
nft_contract = load_contract("./Contracts/Compiled/nft_abi.json", os.getenv("NFT_CONTRACT_ADDRESS"))
marketplace_contract = load_contract("./Contracts/Compiled/nft_marketplace_abi.json", os.getenv("NFT_MARKET_CONTRACT_ADDRESS"))

st.title("Art Registry Appraisal System")
st.write("Choose an account to get started")
accounts = w3.eth.accounts
address = st.selectbox("Select Account", options=accounts)
st.markdown("---")


st.markdown("## Register New Artwork")
file = st.file_uploader("Upload Artwork", type=["jpg", "jpeg", "png"])
if st.button("Register Artwork"):
    try: # to upload the file
        artwork_ipfs_hash = pin_artwork(file)
        artwork_uri = f"ipfs://{artwork_ipfs_hash}"
    except:
        st.write("File upload failed.")
    else:
        try: # to mint the nft
            transaction = nft_contract.functions.createToken(artwork_uri)
            tx_hash = transaction.transact({"from": address, "gas": 1000000})
            receipt = w3.eth.waitForTransactionReceipt(tx_hash)
        except:
            st.write("")
        finally:
            st.write("Transaction Receipt Mined:")
            st.write(dict(receipt))
            st.markdown(f"You can view the pinned metadata file with the following IPFS Gateway Link: [Artwork IPFS Gateway Link](https://gateway.pinata.cloud/ipfs/{artwork_ipfs_hash})")
            st.markdown("---")