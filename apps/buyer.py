import streamlit as st
import os
from dotenv import load_dotenv
from blockhead.contract_api import BlockheadMarketPlace
from pinata import pin_artwork

def buyer():
  load_dotenv()

  # Define and connect a new Web3 provider
  web3_provider_uri = os.getenv("WEB3_PROVIDER_URI")
  mp = BlockheadMarketPlace(web3_provider_uri)

  st.title("Blockheads' NFT MarketPlace")
  st.write("Choose an account to get started")
  accounts = mp.w3.eth.accounts
  address = st.selectbox("Select Account", options=accounts)
  st.markdown("---")
  st.markdown("## BUYER SECTION")

  st.markdown("### Items for sale in the Blockheads' MarketPlace")
  items_for_sale_df = mp.get_nfts_for_sale()
  st.table(items_for_sale_df)

  st.markdown("### Buy an item")
  blockhead_id = st.text_input("Enter the Blockhead id for the item you like")
  purchase_price = st.text_input("Enter the purchase price.")
  if(st.button("Purchase")):
      receipt = mp.buy_nft(address, blockhead_id, purchase_price)
      st.write(receipt)

  st.markdown("### Items you bought")
  account_bought_items_df = mp.get_bought_items_for_account(address)
  st.table(account_bought_items_df)