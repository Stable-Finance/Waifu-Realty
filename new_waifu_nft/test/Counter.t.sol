// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.13;

import {Test, console} from "forge-std/Test.sol";
import {WaifuRealty} from "../src/WaifuRealty.sol";

contract WaifuRealtyTest is Test {
    WaifuRealty public waifuRealty;
    address public owner = address(this);
    address public recipient = address(0xBEEF);

    function setUp() public {
        waifuRealty = new WaifuRealty();
    }

    function test_Mint() public {
        waifuRealty.mint(recipient);
        assertEq(waifuRealty.ownerOf(0), recipient);
    }

    function testFuzz_Mint(address to) public {
        vm.assume(to != address(0)); // Avoid minting to zero address
        waifuRealty.mint(to);
        assertEq(waifuRealty.ownerOf(0), to);
    }
}
