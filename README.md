# Glamsterdam exposure

[![two-way proof](https://github.com/hunterinvariants/glamsterdam-exposure/actions/workflows/ci.yml/badge.svg)](https://github.com/hunterinvariants/glamsterdam-exposure/actions/workflows/ci.yml)

A tool that measures how exposed deployed Ethereum contracts are to a Glamsterdam gas repricing. It
pulls verified source from Etherscan by address, follows proxies to their implementation, compiles
each contract with its original solc, runs a Slither detector for gas-reprice-fragile patterns, and
aggregates the hits into a dataset of which deployed contracts forward a fixed gas budget a repricing
can underfund.

Current scan: 55 deployed contracts compiled, 16 carry the pattern across 23 sites. Among them are
WETH9, Compound cETH, the ENS registrar, the Gnosis Safe singleton, the 1inch v5 router, and older NFT
contracts (CryptoPunks, Art Blocks, Meebits). Modern routers (Uniswap, Sushi, 0x, Balancer) come back
clean. Full per-contract results in GLAMSTERDAM_IMPACT.md.

## The pattern

`address.transfer` and `address.send` forward a fixed 2300-gas stipend to the recipient. EIP-1884
(Istanbul, 2019) repriced SLOAD from 200 to 800 gas and made that stipend insufficient for any
recipient whose fallback touches storage. A class of contracts began reverting on every ETH send.
The Glamsterdam meta (EIP-7773) lists a comprehensive gas repricing package, so the same failure mode
can recur. The detector flags the three ways a contract pins a gas budget:

  - `to.transfer(amount)`   -- 2300-gas stipend
  - `to.send(amount)`       -- 2300-gas stipend
  - `to.call{gas: K}(...)`  -- a hardcoded gas budget on an external call

It is type-aware: Slither models an ETH `.transfer` as a distinct operation, so an ERC-20 token
`.transfer(to, amount)` (an ordinary contract call) is not flagged. That keeps the false-positive
rate low. The `Safe.sol` corpus case, which pays with `.call` and moves a token with `.transfer`,
produces zero findings; `Fragile.sol` produces three.

## What's here

  - `detector/`             -- the Slither plugin (`gas-reprice-fragile`)
  - `corpus/`               -- Fragile.sol (3 sites) and Safe.sol (0 sites), the two-way proof
  - `scan_protocols.py`     -- fetch verified source by address, compile with its solc, scan, aggregate
  - `targets.json`          -- the deployed contracts scanned
  - `GLAMSTERDAM_IMPACT.md` -- the generated dataset

## Run

    pip install -e detector/                                  # registers the detector
    slither corpus/Fragile.sol --detect gas-reprice-fragile   # 3 findings
    slither corpus/Safe.sol    --detect gas-reprice-fragile   # 0 findings

    export ETHERSCAN_API_KEY=...                              # read from env, never hardcoded
    python scan_protocols.py targets.json
    cat GLAMSTERDAM_IMPACT.md

The scanner follows proxies to their implementation, compiles each contract with the solc it was
verified under (via solc-select), and records the per-contract status (compiled / clean / build-failed)
rather than dropping anything silently.

## The dataset

`GLAMSTERDAM_IMPACT.md` is the current scan. The fragile pattern is narrow by design: it bites raw
ETH sends rather than ERC-20 transfers, and most post-2019 code moved to `.call`. What remains is the
older, foundational layer. WETH9 (`withdraw`), Compound cETH (`doTransferOut`), the ENS registrar,
CryptoPunks, and CryptoKitties all forward the 2300-gas stipend, and WETH9 sits under most of DeFi. The
pattern is not only legacy. The Gnosis Safe singleton forwards the stipend in a `.send` refund path, and
the 1inch v5 router hardcodes a 20000-gas external call. The stipend hazard has been known since
EIP-1884; what did not exist is a reproducible, ecosystem-wide measurement of it, refreshed against the
actual Glamsterdam repricing.

## Roadmap

  - v1 (here) -- detector for the historically-precedented stipend / hardcoded-gas pattern, plus a
                 dataset over a set of high-value deployed contracts.
  - v2        -- track the gas-reprice EIPs as they firm up (EIP-7773, forkcast.org), extend the
                 detector to the specific opcodes being repriced, and re-scan to publish an updated
                 exposure set for the ecosystem.

## License

MIT.
