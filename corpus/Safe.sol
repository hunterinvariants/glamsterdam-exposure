// SPDX-License-Identifier: MIT
pragma solidity >=0.6.2 <0.9.0;

interface IERC20 {
    function transfer(address to, uint256 amount) external returns (bool);
}

// No gas-reprice-fragile paths. The detector flags nothing here.
contract Safe {
    // forwards all remaining gas -- not stipend-bound
    function payCall(address to, uint256 amount) external {
        (bool ok, ) = to.call{value: amount}("");
        require(ok, "send failed");
    }

    // an ERC-20 transfer is a contract call, not an ETH stipend send -- must not be flagged
    function payToken(IERC20 token, address to, uint256 amount) external {
        require(token.transfer(to, amount), "token transfer failed");
    }
}
