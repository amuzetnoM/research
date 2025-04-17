// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC721/extensions/ERC721URIStorage.sol";
import "@openzeppelin/contracts/metatx/ERC2771Context.sol";

contract MemoryNFT is ERC721URIStorage, ERC2771Context {
    uint256 public nextTokenId;
    mapping(uint256 => string) public memoryHashes;
    mapping(uint256 => string) public prevHashes;
    mapping(uint256 => string) public embeddedDataURIs; // e.g., pointer to code, script, or computation
    mapping(uint256 => mapping(string => string)) private metadata; // arbitrary key-value metadata

    constructor(address trustedForwarder)
        ERC721("MemoryNFT", "MEM")
        ERC2771Context(trustedForwarder)
    {}

    function mintMemoryNFT(
        address to,
        string memory memoryHash,
        string memory metadataURI,
        string memory prevHash
    ) public {
        uint256 tokenId = nextTokenId++;
        _safeMint(to, tokenId);
        _setTokenURI(tokenId, metadataURI);
        memoryHashes[tokenId] = memoryHash;
        prevHashes[tokenId] = prevHash;
    }

    // Set embedded data URI (e.g., code, script, or computation pointer)
    function setEmbeddedDataURI(uint256 tokenId, string memory dataURI) public {
        require(_isApprovedOrOwner(_msgSender(), tokenId), "Not owner nor approved");
        embeddedDataURIs[tokenId] = dataURI;
    }

    // Set arbitrary metadata key-value for a token
    function setMetadata(uint256 tokenId, string memory key, string memory value) public {
        require(_isApprovedOrOwner(_msgSender(), tokenId), "Not owner nor approved");
        metadata[tokenId][key] = value;
    }

    // Get arbitrary metadata value for a token
    function getMetadata(uint256 tokenId, string memory key) public view returns (string memory) {
        return metadata[tokenId][key];
    }

    // Get all core info for a token (for off-chain display/processing)
    function getTokenInfo(uint256 tokenId)
        public
        view
        returns (
            string memory memoryHash,
            string memory prevHash,
            string memory uri,
            string memory embeddedData
        )
    {
        memoryHash = memoryHashes[tokenId];
        prevHash = prevHashes[tokenId];
        uri = tokenURI(tokenId);
        embeddedData = embeddedDataURIs[tokenId];
    }

    function _msgSender() internal view override(Context, ERC2771Context) returns (address sender) {
        sender = ERC2771Context._msgSender();
    }

    function _msgData() internal view override(Context, ERC2771Context) returns (bytes calldata) {
        return ERC2771Context._msgData();
    }
}
