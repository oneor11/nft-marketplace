import os
import json
from dotenv import load_dotenv
import pandas as pd
from web3 import Web3
from pathlib import Path


class BlockheadMarketPlace:

    """

    Attributes:
        nft_contract: string
            Contract's Application Binary Interface (ABI) represented
            in JSON format for the NFT contract. See Contracts/nft.sol

        marketplace_contract: string
            Contract's Application Binary Inteface (ABI) represented
            in JSON format for the NFT Marketplace contract.  See
            Contracts/nftMarket.sol       
    """

    w3 = None
    nft_address = None
    nft_contract = None
    marketplace_address = None
    marketplace_contract = None
    

    def __init__(self, web3_provider_uri : str): 
        load_dotenv()
        self.w3 = Web3(Web3.HTTPProvider(web3_provider_uri))
        self.nft_contract_address = os.getenv("NFT_CONTRACT_ADDRESS")
        self.marketplace_address =  os.getenv("NFT_MARKET_CONTRACT_ADDRESS")
        self.nft_contract = \
            self.__load_contract("./blockhead/abi/nft_abi.json", self.nft_contract_address)
        self.marketplace_contract = \
            self.__load_contract("./blockhead/abi/nft_marketplace_abi.json", self.marketplace_address)





    def mint_token(self,
            from_address : str, 
            token_uri : str) -> str:

        """Mints a token on the blockhain
        
        Minting entails assigning a unique identifier to the nft located
        at the uri.  This process is governed by an ERC-721 compliant 
        contract. See Contracts/nft.sol.

        Args:
            w3: Web3 Provider
                Web3 Provider object enabling access to the blockchain

            from_address: string
                Blockchain address of the current user

            token_uri:
                Unique Resource Identifier that identifies the digital NFT

        Returns:
            A token id
        """
        transaction = self.nft_contract.functions.createToken(token_uri)
        tx_hash = transaction.transact({"from": from_address, "gas": 1000000})
        receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        rich_logs = self.nft_contract.events.TokenCreated().processReceipt(receipt)
        token_id = rich_logs[0]['args']['itemId']

        return token_id





    def create_market_item(self,
            from_address: str,
            token_id : int, 
            price_wei : int, 
            listing_price_wei : int) -> int:

        """ Establishes an NFT for sale on the Blockhead NFT MarketPlace
        
        Puts an NFT that has been tokenized using the NFT contract
        (Contracts/nft.sol) for sale on the Blockhead NFT Marketplace 
        governed by the Marketplace Contract (Contracts/nftMarket.sol). 
        The Blockhead NFT Marketplace has permissions to access tokens 
        created on the NFT Contract. 

        Putting up for sale requires submitting the listing price, which is the
        cost of putting the NFT up for sale. 

        Args:
            from_address: string
                Blockchain address of the current user, or seller, of the NFT

            token_id: int
                Unique identifier of the minted NFT as governed by the 
                NFT contract (Contracts/nft.sol)

            price_wei: int
                The NFT purchse price, in wei, set by the seller.

            listing_price_wei: int
                The amount being submitted to cover the listing price, which is
                the cost of listing an NFT.  This value is established by the 
                Blockhead NFT Marketplace.  See Contracts/nftMarket.sol

        Returns:
            An item id which represents the unique index of the NFT on the
            Blockhead NFT Marketplace.

        """   
        transaction = self.marketplace_contract.functions.createMarketItem(
            self.nft_contract_address, int(token_id), int(price_wei))
        tx_hash = transaction.transact(
            {
                "from": from_address, 
                "gas": 1000000, 
                "value": int(listing_price_wei)
            })
        receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        rich_logs = self.marketplace_contract.events.MarketItemCreated().processReceipt(receipt)
        item_id  = rich_logs[0]['args']['itemId']

        return item_id




    def get_listed_items_for_account(self, from_address : str, show_sold : bool = True) -> pd.DataFrame:

        """ Retrieves the current account's listed items.

            Args:
                from_address: string
                    Blockchain address of the current user, or seller, of the NFT

            Returns:
                Unsold NFTs returned as an array of MarketItem as a DataFrame
        """       

        transaction = self.marketplace_contract.functions.fetchItemsCreated()
        items = transaction.call(
                    {
                        "from": from_address
                    })
        items_df = pd.DataFrame(items)

        if not items_df.empty:
            items_df.columns = ['Token Id',  'Contract', 'Blockhead Id', 'Minter', 'Owner', 'Cost', 'Sold']
            items_df.drop(['Contract'], axis=1, inplace=True)

            if not show_sold:
                items_df = items_df[items_df["Sold"] == False]
                items_df['Minter'] = items_df.apply(lambda row : self.__simplify_address(row['Minter']), axis=1)
                items_df['Owner'] = items_df.apply(lambda row : self.__simplify_address(row['Owner']), axis=1)

        return items_df


    def get_bought_items_for_account(self, from_address : str) -> pd.DataFrame:
        
        """ Retrieves the current account's bought items.

            Args:
                from_address: string
                    Blockchain address of the current user, or seller, of the NFT

            Returns:
                Bought NFTs returned as an array of MarketItem as a DataFrame
        """       

        transaction = self.marketplace_contract.functions.fetchMyNFTs()
        items = transaction.call(
                    {
                        "from": from_address
                    })
        items_df = pd.DataFrame(items)

        if not items_df.empty:
            items_df.columns = ['Token Id',  'Contract', 'Blockhead Id', 'Minter', 'Owner', 'Cost', 'Sold']
            items_df.drop(['Contract'], axis=1, inplace=True)
            items_df['Minter'] = items_df.apply(lambda row : self.__simplify_address(row['Minter']), axis=1)
            items_df['Owner'] = items_df.apply(lambda row : self.__simplify_address(row['Owner']), axis=1)
        
        return items_df


    def get_nfts_for_sale(self) -> pd.DataFrame:

        """ Retrieves unsold NFTs on the Blockhead MarketPlace

            Returns:
                Unsold NFTs returned as an array of MarketItem in JSON format

        """       

        transaction = self.marketplace_contract.functions.fetchMarketItems()
        data = transaction.call()
        unsold_items_df = pd.DataFrame(data)
        if not unsold_items_df.empty:
            unsold_items_df.columns = ['Token Id',  'Contract', 'Blockhead Id', 'Minter', 'Owner', 'Cost', 'Sold']
            unsold_items_df.drop(['Contract'], axis=1, inplace=True)
            unsold_items_df['Token URI'] = unsold_items_df.apply(self.__apply_token_uri, axis=1)
            unsold_items_df['Minter'] = unsold_items_df.apply(lambda row : self.__simplify_address(row['Minter']), axis=1)
            unsold_items_df['Owner'] = unsold_items_df.apply(lambda row : self.__simplify_address(row['Owner']), axis=1)
            unsold_items_df['IPFS URL'] = unsold_items_df.apply(
                lambda row : self.convert_ipfs_uri_to_url(row['Token URI']), axis=1)

        return unsold_items_df





    def get_listing_price_wei(self):
        """ Gets the listing price set for the Blockhead NFT
            MarketPlace

            The listing price is the cost a seller must pay to list on 
            the Blockhead MarketPlace.
        
        """
        transaction = self.marketplace_contract.functions.getListingPrice()
        listing_price = transaction.call()

        return listing_price





    def buy_nft(self, 
            from_address : str, 
            blockhead_id : int, 
            price_wei : int) -> str:

        """ Enables the purchase of an NFT from the Blockhead 
            Marketplace
        
        Enables the purchsae and transfer of ownership of an NFT as well
        as transfer of payment from the buyer to the seller and the transfer
        of the listing price (cost to list the item) to the contract owner.

        Args:
            from_address: string
                Blockchain address of the current user, or buyer, of the NFT

            blockhead_id: int
                An item id which represents the unique index of the NFT on the
                Blockhead NFT Marketplace. This is the item being purchased.

            price_wei: int
                The NFT purchse price, in wei, set by the seller.

        Returns:
            A transaction receipt

        """   
        from_address = str(from_address)
        blockhead_id = int(blockhead_id)
        price_wei = int(price_wei)

        transaction = self.marketplace_contract.functions.createMarketSale(self.nft_contract_address, blockhead_id)
        tx_hash = transaction.transact(
            {
                "from": from_address, 
                "gas": 1000000, 
                "value": int(price_wei)
            })
        receipt = self.w3.eth.waitForTransactionReceipt(tx_hash)
        return receipt





    def convert_ipfs_uri_to_url(self, uri : str) -> str:
        #TODO This should go in a config file
        ipfs_url = "https://gateway.pinata.cloud/ipfs/"

        if(uri.startswith("ipfs://")):
            uri = uri.replace("ipfs://", ipfs_url)
        else:
            uri = f"{ipfs_url}{uri}"

        return uri





    def __apply_token_uri(self, row):
        token_id = row["Token Id"]
        transaction = self.nft_contract.functions.tokenURI(token_id)
        token_uri = transaction.call()
        return token_uri





    def __load_contract(self, abi_file_path, contract_address):

        # Load the contract ABI
        with open(Path(abi_file_path)) as f:
            contract_abi = json.load(f)

        # Get the contract
        contract = self.w3.eth.contract(
            address=contract_address,
            abi=contract_abi
        )

        return contract

    
    def __simplify_address(self, address):
        """Return the first four and last four of a wallet address"""

        length = len(address)
        if length > 8:
            return f'{address[0:4]}...{address[(length-4):length]}'
        else:
            return address