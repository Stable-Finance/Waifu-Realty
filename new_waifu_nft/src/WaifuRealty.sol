// SPDX-License-Identifier: MIT
// pragma solidity ^0.8.19;
pragma solidity ^0.8.13;
import "@openzeppelin/contracts/token/ERC721/ERC721.sol";
import "@openzeppelin/contracts/access/Ownable.sol";


contract WaifuRealty is ERC721, Ownable {
    uint256 private _nextTokenId;

    constructor() ERC721("Waifu Realty", "WAIFU") Ownable(msg.sender) {}

    function mint(address to) external onlyOwner {
        uint256 tokenId = _nextTokenId++;
        _safeMint(to, tokenId);
    }

    function _baseURI() internal pure override returns (string memory) {
        return "https://your-metadata-url.com/";
    }
}
