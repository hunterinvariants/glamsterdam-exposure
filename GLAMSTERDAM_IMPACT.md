# Glamsterdam exposure report

Deployed contracts that use a pattern a Glamsterdam gas repricing can break -- the fixed
2300-gas `.transfer` / `.send` stipend and hardcoded call gas (the class EIP-1884 broke in
2019). Source is pulled from Etherscan (verified = the deployed bytecode), proxies are
followed to their implementation, each contract is compiled with its original solc, and
scanned with the `gas-reprice-fragile` detector. Every site is a real line in deployed code.

## Summary

- contracts scanned (compiled): 47
- contracts with fragile sites: 9
- total flagged sites: 12

| Contract | Address | solc | Status | Sites |
|---|---|---|---|:--:|
| WETH9 | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` | 0.4.19 | ok | 1 |
| Compound cETH | `0x4Ddc2D193948926D02f9B1fE9e1daa0718270ED5` | 0.5.8 | ok | 1 |
| Compound cDAI | `0x5d3a536E4D6DbD6114cc1Ead35777bAB948E3643` | 0.8.10 | clean | 0 |
| CryptoPunks | `0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB` | 0.4.11 | ok | 2 |
| CryptoKitties Core | `0x06012c8cf97BEaD5deAe237070F9587f8E7A266d` | 0.4.18 | ok | 1 |
| CryptoKitties SaleAuc | `0xb1690C08E213a35Ed9bAb7B318DE14420FB57d8C` | 0.4.18 | clean | 0 |
| ENS ETHRegistrarCtrl | `0x283Af0B28c62C092C9727F1Ee09c02CA627EB7F5` | 0.5.16 | ok | 3 |
| ENS Registry | `0x00000000000C2E074eC69A0dFb2997BA6C7d2e1e` | 0.5.16 | clean | 0 |
| Disperse | `0xD152f549545093347A162Dce210e7293f1452150` | 0.4.25 | ok | 1 |
| Uniswap V2 Router02 | `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D` | 0.6.6 | clean | 0 |
| Uniswap V2 Factory | `0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f` | 0.5.16 | clean | 0 |
| Uniswap V3 SwapRouter | `0xE592427A0AEce92De3Edee1F18E0157C05861564` | 0.7.6 | clean | 0 |
| SushiSwap Router | `0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F` | 0.6.12 | clean | 0 |
| SushiSwap MasterChef | `0xc2EdaD668740f1aA35E4D8f227fB8E17dcA888Cd` | 0.6.12 | clean | 0 |
| 0x Exchange v2 | `0x080bf510FCbF18b91105470639e9561022937712` | 0.4.24 | clean | 0 |
| 0x Exchange v1 | `0x12459C951127e0c374FF9105DdA097662A027093` | 0.4.14 | clean | 0 |
| Balancer Vault | `0xBA12222222228d8Ba445958a75a0704d566BF2C8` | 0.7.1 | clean | 0 |
| 1inch v5 Router | `0x1111111254EEB25477B68fb85Ed929f73A960582` | 0.8.17 | ok | 1 |
| KyberNetworkProxy | `0x818E6FECD516Ecc3849DAf6845e3EC868087B755` | 0.4.18 | clean | 0 |
| Gnosis Safe Singleton | `0xd9Db270c1B5E3Bd161E8c8503c55cEABeE709552` | 0.7.6 | ok | 1 |
| OpenSea Wyvern v2 | `0x7f268357A8c2552623316e2562D90e642bB538E5` | 0.4.26 | clean | 0 |
| OpenSea Seaport 1.5 | `0x00000000000000ADc04C56Bf30aC9d3c0aAF14dC` | 0.8.17 | clean | 0 |
| ETH2 Deposit Contract | `0x00000000219ab540356cBB839Cbe05303d7705Fa` | 0.6.11 | clean | 0 |
| Lido stETH | `0xae7ab96520DE3A18E5e111B5EaAb095312D7fE84` | 0.4.24 | clean | 0 |
| RocketPool Storage | `0x1d8f8f00cfa6758d7bE78336684788Fb0ee0Fa46` | 0.7.6 | clean | 0 |
| DAI | `0x6B175474E89094C44Da98b954EedeAC495271d0F` | 0.5.12 | clean | 0 |
| MKR | `0x9f8F72aA9304c8B593d555F12eF6589cC3A579A2` | 0.4.18 | clean | 0 |
| Synthetix ProxyERC20 | `0xC011a73ee8576Fb46F5E1c5751cA3B9Fe0af2a6F` | 0.4.25 | clean | 0 |
| Uniswap V3 Factory | `0x1F98431c8aD98523631AE4a59f267346ea31F984` | 0.7.6 | clean | 0 |
| Uniswap V3 PositionMgr | `0xC36442b4a4522E871399CD717aBDD847Ab11FE88` | 0.7.6 | clean | 0 |
| Uniswap V4 PoolManager | `0x000000000004444c5dc75cB358380D2e3dE08A90` | 0.8.26 | clean | 0 |
| Aave V3 Pool | `0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2` | 0.8.27 | clean | 0 |
| Morpho Blue | `0xBBBBBbbBBb9cC5e90e3b3Af64bdAF62C37EEFFCb` | 0.8.19 | clean | 0 |
| MakerDAO Vat | `0x35D1b3F3D7966A1DFe207aa4514C12a259A0492B` | 0.5.12 | clean | 0 |
| Liquity BorrowerOps | `0x24179CD81c9e782A4096035f7eC97fB8B783e007` | 0.6.11 | clean | 0 |
| USDC | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` | 0.6.12 | clean | 0 |
| USDT | `0xdAC17F958D2ee523a2206206994597C13D831ec7` | 0.4.18 | clean | 0 |
| FRAX | `0x853d955aCEf822Db058eb8505911ED77F175b99e` | 0.6.11 | clean | 0 |
| WBTC | `0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599` | 0.4.24 | clean | 0 |
| LUSD | `0x5f98805A4E8be255a32880FDeC7F6728C6568bA0` | 0.6.11 | clean | 0 |
| wstETH | `0x7f39C581F595B53c5cb19bD0b3f8dA6c935E2Ca0` | 0.6.12 | clean | 0 |
| rETH | `0xae78736Cd615f374D3085123A210448E74Fc6393` | 0.7.6 | ok | 1 |
| EigenLayer StrategyMgr | `0x858646372CC42E1A627fcE94aa7A7033e7CF075A` | 0.8.30 | clean | 0 |
| EigenLayer Delegation | `0x39053D51B77DC0d36036Fc1fCc8Cb819df8Ef37A` | 0.8.30 | clean | 0 |
| Lido WithdrawalQueue | `0x889edC2eDab5f40e902b864aD4d7AdE8E412F9B1` | 0.8.9 | clean | 0 |
| Frax frxETH Minter | `0xbAFA44EFE7901E04E39Dad13167D089C559c1138` | 0.8.16 | clean | 0 |
| Convex Booster | `0xF403C135812408BFbE8713b5A23a04b3D48AAE31` | 0.6.12 | clean | 0 |

## Sites

### WETH9  (`0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2`)
- WETH9.withdraw(uint256) (WETH9.sol#38-43)  uses address.transfer() -- forwards a fixed 2300-gas stipend; an EVM gas repricing (e.g. Glamsterdam) can make it insufficient and break this path.  (WETH9.sol:38)

### Compound cETH  (`0x4Ddc2D193948926D02f9B1fE9e1daa0718270ED5`)
- CEther.doTransferOut(address,uint256) (CEther.sol#2513-2517)  uses address.transfer() -- forwards a fixed 2300-gas stipend; an EVM gas repricing (e.g. Glamsterdam) can make it insufficient and break this path.  (CEther.sol:2513)

### CryptoPunks  (`0xb47e3cd837dDF8e4c57F05d70Ab865de6e193BBB`)
- CryptoPunksMarket.withdraw() (CryptoPunksMarket.sol#186-193)  uses address.transfer() -- forwards a fixed 2300-gas stipend; an EVM gas repricing (e.g. Glamsterdam) can make it insufficient and break this path.  (CryptoPunksMarket.sol:186)
- CryptoPunksMarket.withdrawBidForPunk(uint256) (CryptoPunksMarket.sol#232-244)  uses address.transfer() -- forwards a fixed 2300-gas stipend; an EVM gas repricing (e.g. Glamsterdam) can make it insufficient and break this path.  (CryptoPunksMarket.sol:232)

### CryptoKitties Core  (`0x06012c8cf97BEaD5deAe237070F9587f8E7A266d`)
- KittyCore.withdrawBalance() (KittyCore.sol#2000-2008)  uses address.send() -- forwards a fixed 2300-gas stipend; an EVM gas repricing (e.g. Glamsterdam) can make it insufficient and break this path.  (KittyCore.sol:2000)

### ENS ETHRegistrarCtrl  (`0x283Af0B28c62C092C9727F1Ee09c02CA627EB7F5`)
- ETHRegistrarController.registerWithConfig(string,address,uint256,bytes32,address,address) (ETHRegistrarController.sol#396-434)  uses address.transfer() -- forwards a fixed 2300-gas stipend; an EVM gas repricing (e.g. Glamsterdam) can make it insufficient and break this path.  (ETHRegistrarController.sol:396)
- ETHRegistrarController.renew(string,uint256) (ETHRegistrarController.sol#436-448)  uses address.transfer() -- forwards a fixed 2300-gas stipend; an EVM gas repricing (e.g. Glamsterdam) can make it insufficient and break this path.  (ETHRegistrarController.sol:436)
- ETHRegistrarController.withdraw() (ETHRegistrarController.sol#460-462)  uses address.transfer() -- forwards a fixed 2300-gas stipend; an EVM gas repricing (e.g. Glamsterdam) can make it insufficient and break this path.  (ETHRegistrarController.sol:460)

### Disperse  (`0xD152f549545093347A162Dce210e7293f1452150`)
- Disperse.disperseEther(address[],uint256[]) (Disperse.sol#11-17)  uses address.transfer() -- forwards a fixed 2300-gas stipend; an EVM gas repricing (e.g. Glamsterdam) can make it insufficient and break this path.  (Disperse.sol:11)

### 1inch v5 Router  (`0x1111111254EEB25477B68fb85Ed929f73A960582`)
- UniERC20._uniDecode(IERC20,bytes4,bytes4) (AggregationRouterV5.sol#889-932)  hardcodes gas (20000) on an external call -- a gas repricing can make it insufficient and break this path.  (AggregationRouterV5.sol:889)

### Gnosis Safe Singleton  (`0xd9Db270c1B5E3Bd161E8c8503c55cEABeE709552`)
- GnosisSafe.handlePayment(uint256,uint256,uint256,address,address) (contracts/GnosisSafe.sol#196-213)  uses address.send() -- forwards a fixed 2300-gas stipend; an EVM gas repricing (e.g. Glamsterdam) can make it insufficient and break this path.  (contracts/GnosisSafe.sol:196)

### rETH  (`0xae78736Cd615f374D3085123A210448E74Fc6393`)
- RocketTokenRETH.burn(uint256) (contracts/contract/token/RocketTokenRETH.sol#132-149)  uses address.transfer() -- forwards a fixed 2300-gas stipend; an EVM gas repricing (e.g. Glamsterdam) can make it insufficient and break this path.  (contracts/contract/token/RocketTokenRETH.sol:132)

## Reading this

The risk is narrow by design: the 2300-gas stipend only bites raw-ETH `.transfer` / `.send`.
Contracts that pay ETH with `.call{value: ...}("")` are unaffected, and most post-2019 code
moved to `.call`. A `clean` row is a real result -- that contract is not gas-reprice-fragile.
A flagged row is a deployed contract whose ETH path forwards a fixed gas budget a repricing
can underfund. `build-failed` is a source whose compile did not resolve cold; it is recorded,
not dropped.

## Reproduce

```
ETHERSCAN_API_KEY=... python scan_protocols.py targets.json
```
