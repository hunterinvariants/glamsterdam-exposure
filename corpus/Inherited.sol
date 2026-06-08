// SPDX-License-Identifier: MIT
pragma solidity >=0.6.2 <0.9.0;

/// Regression fixture for the inherited-base scan. The fragile value-send is declared in a BASE
/// contract reached only through inheritance. A detector that scans only leaf contracts' own declared
/// functions misses it (returns 0); scanning every contract catches it. Expected: 1 finding
/// (PayoutBase._payout).
contract PayoutBase {
    function _payout(address payable to, uint256 amount) internal {
        to.transfer(amount); // 2300-gas stipend, declared in a base contract
    }
}

contract InheritsFragilePayout is PayoutBase {
    function withdraw(address payable to, uint256 amount) external {
        _payout(to, amount);
    }
}
