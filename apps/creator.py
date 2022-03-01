import streamlit as st
import os
from dotenv import load_dotenv
from blockhead.contract_api import BlockheadMarketPlace
from pinata import pin_artwork

def creator():
  
  load_dotenv()

  # Define and connect a new Web3 provider
  web3_provider_uri = os.getenv("WEB3_PROVIDER_URI")
  mp = BlockheadMarketPlace(web3_provider_uri)

  st.title("Blockheads' NFT MarketPlace")
  st.write("Choose an account to get started")
  accounts = mp.w3.eth.accounts
  address = st.selectbox("Select Account", options=accounts)
  st.markdown("---")


  # CREATOR: Upload, mint, and put the item up for sale
  st.markdown("## CREATOR SECTION")

  st.markdown("### Put your artwork up for sale!")
  file = st.file_uploader("Upload Artwork", type=["jpg", "jpeg", "png"])
  price = st.text_input("Set the Price (wei)")

  if st.button("Register artwork and put it up for sale"):
      try: # to upload the file
          artwork_uri = pin_artwork(file)
      except Exception as e:
          st.write("File upload failed.")
          if hasattr(e, 'message'):
              st.write(e.message)
          else:
              st.write(e)
      else:
          try:
              token_id = mp.mint_token(address, artwork_uri)  # mint the nft
              # TODO: replace the following line with the contract call that gets the listing
              listing_price = mp.get_listing_price_wei()
              item_id = mp.create_market_item(address, token_id, price, listing_price)
          except Exception as e:
              st.write("Create token failed.")
              if hasattr(e, 'message'):
                  st.write(e.message)
              else:
                  st.write(e)
          else:
              st.markdown("**Success!**")
              st.write(f"Token Id: {token_id}  Blockhead Id: {item_id}")
              st.markdown(f"You can view the pinned metadata file with the following IPFS Gateway Link: [Artwork IPFS Gateway Link]({mp.convert_ipfs_uri_to_url(artwork_uri)})")
              st.markdown("---")

  st.markdown("### Items you have for sale or have sold")
  show_sold = st.checkbox("Show sold items?")
  account_items_listed_df = mp.get_listed_items_for_account(address, show_sold)
  st.table(account_items_listed_df)

  

