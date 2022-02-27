pragma solidity ^0.8.0;  //SPDX-License-Identifier: GPL-3.0

import "@openzeppelin/contracts/utils/Counters.sol";
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
// prevent re-entrancy attacks
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";


contract nftMarket is ReentrancyGuard {
    using Counters for Counters.Counter;
    Counters.Counter private _itemIds;   // total number of items ever created 
    Counters.Counter private _itemSold;  // total number of items Sold

    address payable owner; // owner of the smart contract
    // people have to pay for their NFT on this marketplace
    uint256 listingPrice = 0.035 ether;

    constructor(){
        owner = payable(msg.sender);
    }

    struct MarketItem {
        uint itemId;
        address nftContract;
        uint256 tokenId;
        address payable seller;
        address payable owner;
        uint256 price;
        bool sold;
    }
    // the struct items looks like an array, can't access it without mapping
    // this is the way to access Market item struc by passing an integer Id
    mapping(uint256 => MarketItem) private idMarketItem;

    // declare event to log activity when item is sold.
    // note that event function does not use semi colon but uses comma.
    event MarketItemCreated (
        uint indexed itemId,
        address indexed nftContract,
        uint256 indexed tokenId,
        address payable seller,
        address payable owner,
        uint256 price,
        bool sold
    );

    // function to get the listing price
    function getListingPrice() public view returns (uint256) {
        return listingPrice;
    }


    function setListingPrice(uint _price) public returns (uint256) {
        listingPrice = _price;
        return listingPrice;
    }


    /// @notice create a function that manages MarketItem
    function createMarketItem(
        address nftContract, 
        uint256 tokenId, 
        uint256 price) public payable nonReentrant {
        require(price > 0, "Price must be above zero");
        require(msg.value == listingPrice, "Price must be equal to listing price");

    //    if (msg.value != listingPrice) {
    //       return "Price must be equal to listing price";

    // Time to use the struc Market data above in line 21 
        _itemIds.increment();  // add 1 to the total number of items ever created 
        uint256 itemId = _itemIds.current();

        // note when you define a struc, you use curly braces to define it and semi colon inside 
        // but when using it you call it as a function with open and close round brackets with commas to seperate the items
         idMarketItem[itemId] = MarketItem(
             itemId,
             nftContract,
             tokenId,
             payable(msg.sender),
             payable (address(0)), // no owner yet hence set as empty address 
             price,
             false);

        // transfering ownership of the NFT to the contract itself until someone wants to buy.
            IERC721(nftContract).transferFrom(msg.sender, address(this), tokenId);
         
         // log this transactions
        emit MarketItemCreated(
            itemId, 
            nftContract, 
            tokenId, 
            payable(msg.sender), 
            payable(address(0)),  // address is zero because it hasn't been sold yet
            price,
            false);
        }


        /// @notice function to create a sale
        function createMarketSale(
            address nftContract,
            uint256 itemId) public payable nonReentrant {
                uint price = idMarketItem[itemId].price;
                uint tokenId = idMarketItem[itemId].tokenId;

                require(msg.value == price, "Please submit the asking price in order to complete the purchase");

                //pay the seller the amount
                idMarketItem[itemId].seller.transfer(msg.value);

                // transfer the ownership from the contract itself to the buyer
                IERC721(nftContract).transferFrom(address(this), msg.sender, tokenId);

                idMarketItem[itemId].owner = payable(msg.sender); // mark new buyer as new owner
                idMarketItem[itemId].sold = true; // mark that it has been sold
                _itemSold.increment(); // increment the total number of item sold by 1
                payable (owner).transfer(listingPrice); // pay owner of the contract the listing price
            }

            
        /// @notice total number of items unsold on our platform
        function fetchMarketItems() public view returns (MarketItem[] memory){
            uint itemCount = _itemIds.current(); // total number of items ever Created

            // total number of items that are unsold  = total number of items created - total number of items ever sold
            uint unsoldItemCount = _itemIds.current() - _itemSold.current();
            uint currentIndex = 0;

          //  Instanciate or Craete an array of MarketItem
            MarketItem[] memory items = new MarketItem[](unsoldItemCount);

            // loop through all items ever created
            for(uint i =0; i < itemCount; i++) {
                // check if the item has not been sold
                // by checking if the owner field is empty
                if(idMarketItem[i+1].owner == address(0)){
                    // yes, this item has never been sold
                    uint currentId = idMarketItem[i+1].itemId;
                    MarketItem storage currentItem = idMarketItem[currentId];
                    items[currentIndex] = currentItem;
                    currentIndex += 1;
                }
            }
            return items; //return array of all unsold items
        }

    /// @notice fetch the list of NFT's bought by the user
        function fetchMyNFTs()public view returns (MarketItem[] memory) {
            // get total number of items ever created
            uint totalItemCount = _itemIds.current();

            uint itemCount = 0;
            uint currentIndex = 0; 

            for (uint i=0; i< totalItemCount; i++){
                // get only the item that this user has bought/ is the owner 
                if (idMarketItem[i+1].owner == msg.sender) {
                    itemCount += 1; // total length of the array
                }
            }


            MarketItem[] memory items = new MarketItem[](itemCount);
            for(uint i = 0; i < totalItemCount; i++){
                if (idMarketItem[i+1].owner == msg.sender){
                    uint currentId = idMarketItem[i+1].itemId;
                    MarketItem storage currentItem = idMarketItem[currentId];
                    items[currentId] = currentItem;
                    currentIndex += 1;

            }
        }
        return items;

        }

         /// @notice fetch the list of NFT's created by the user
        function fetchItemsCreated() public view returns (MarketItem[] memory) {
            // get total number of items ever created
            uint totalItemCount = _itemIds.current();

            uint itemCount = 0;
            uint currentIndex = 0; 

            for (uint i=0; i< totalItemCount; i++){
                // get only the item that this user has bought/ is the owner 
                if (idMarketItem[i+1].seller == msg.sender) {
                    itemCount += 1; // total length of the array
                }

            }
            MarketItem[] memory items = new MarketItem[](itemCount);
            for(uint i = 0; i < totalItemCount; i++){
                if (idMarketItem[i+1].seller == msg.sender){
                    uint currentId = idMarketItem[i+1].itemId;
                    MarketItem storage currentItem = idMarketItem[currentId];
                    items[currentId] = currentItem;
                    currentIndex += 1;

            }
        }
        return items;

        }
}