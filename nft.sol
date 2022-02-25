pragma solidity ^0.8.0; //SPDX-License-Identifier: GPL-3.0

import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/utils/Counters.sol";

contract nft is ERC721URIStorage{
    /// auto increment field for each token
    using Counters for Counters.Counter;
    Counters.Counter private _tokenIds;

    // address of the nft Market place
    address contractAddress;

    constructor(address marketplaceAddress) ERC721("Artwork Token", "ART") {
        contractAddress = marketplaceAddress;
    }


    /// @notice create a new token
    /// @param tokenURI : tokenURI
    function createToken(string memory tokenURI) public returns(uint) {
        // set a new token id for the token to be minted
        _tokenIds.increment();
        uint256 newItemId = _tokenIds.current();

    _mint(msg.sender, newItemId); // Mint the token

    _setTokenURI(newItemId, tokenURI); // generate the URI

    // give approval or grant transaction permission to start
    setApprovalForAll(contractAddress, true);

    // return token Id
    return newItemId;


    }

}