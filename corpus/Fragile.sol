// SPDX-License-Identifier: MIT
pragma solidity >=0.6.2 <0.9.0;

// Three gas-reprice-fragile ETH paths. The detector flags all three.
contract Fragile {
    function payTransfer(address payable to, uint256 amount) external {
        to.transfer(amount); // 2300-gas stipend
    }

    function paySend(address payable to, uint256 amount) external returns (bool ok) {
        ok = to.send(amount); // 2300-gas stipend
    }

    function payFixedGas(address to, uint256 amount) external {
        (bool ok, ) = to.call{value: amount, gas: 2300}(""); // hardcoded gas budget
        require(ok, "send failed");
    }
}
