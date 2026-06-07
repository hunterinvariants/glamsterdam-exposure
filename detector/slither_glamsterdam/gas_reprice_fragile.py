"""Slither detector: gas-reprice-fragile.

Flags ETH-value sends and external calls that forward a fixed gas budget the EVM may reprice --
the class a Glamsterdam gas repricing can break:

  - address.transfer(...)   forwards a fixed 2300-gas stipend
  - address.send(...)       forwards a fixed 2300-gas stipend
  - x.call{gas: K}(...)      hardcodes a gas budget on an external call

Scope: scans every contract in the target, including base/abstract contracts reached only through
inheritance, so a fragile value-send declared in a base is not missed. Each function is visited in the
contract that declares it, so there is no double-reporting. Hardcoded-gas detection is literal-only
(a gas budget passed as a named constant is not resolved to its value).

EIP-1884 (Istanbul, 2019) already made the 2300-gas stipend insufficient once; a Glamsterdam gas
repricing can do it again. The detector is type-aware: Slither models an ETH `.transfer` as the
Transfer operation, so an ERC-20 token `.transfer(to, amount)` -- an ordinary contract call -- is
not flagged.
"""
from slither.detectors.abstract_detector import AbstractDetector, DetectorClassification
from slither.slithir.operations import Transfer, Send, HighLevelCall, LowLevelCall

try:
    from slither.slithir.variables.constant import Constant
except Exception:  # defensive across slither versions
    Constant = None


class GasRepriceFragile(AbstractDetector):
    ARGUMENT = "gas-reprice-fragile"
    HELP = "Patterns that can break under an EVM gas repricing (Glamsterdam-sensitive)"
    IMPACT = DetectorClassification.MEDIUM
    CONFIDENCE = DetectorClassification.MEDIUM

    WIKI = "https://github.com/hunterinvariants/glamsterdam-exposure"
    WIKI_TITLE = "Gas-reprice fragile"
    WIKI_DESCRIPTION = (
        "An ETH send or external call that forwards a fixed gas budget can break when the EVM "
        "reprices the opcodes that budget covers. address.transfer / address.send forward a fixed "
        "2300-gas stipend; EIP-1884 made that stipend insufficient once in 2019, and a Glamsterdam "
        "gas repricing can do it again."
    )
    WIKI_EXPLOIT_SCENARIO = (
        "A contract pays ETH out with recipient.transfer(amount). After a repricing the recipient's "
        "fallback costs more than 2300 gas, the send reverts, and the path is bricked."
    )
    WIKI_RECOMMENDATION = (
        "Send ETH with (bool ok, ) = recipient.call{value: amount}(\"\") and check ok, guarded by a "
        "reentrancy guard or checks-effects-interactions. Do not hardcode gas: on external calls."
    )

    _TAIL = "; an EVM gas repricing (e.g. Glamsterdam) can make it insufficient and break this path."

    @staticmethod
    def _hardcoded_gas(ir):
        gas = getattr(ir, "call_gas", None)
        if gas is None:
            return None
        if Constant is not None and isinstance(gas, Constant):
            return gas.value
        val = getattr(gas, "value", None)
        return val if isinstance(val, int) else None

    def _detect(self):
        results = []
        seen = set()
        # all contracts (not just leaves) so a fragile send in an inherited base is caught;
        # functions_and_modifiers_declared visits each function in its declaring contract -> no dupes.
        for contract in self.compilation_unit.contracts:
            for function in contract.functions_and_modifiers_declared:
                for node in function.nodes:
                    for ir in node.irs:
                        reason = None
                        if isinstance(ir, Transfer):
                            reason = "uses address.transfer() -- forwards a fixed 2300-gas stipend" + self._TAIL
                        elif isinstance(ir, Send):
                            reason = "uses address.send() -- forwards a fixed 2300-gas stipend" + self._TAIL
                        elif isinstance(ir, (HighLevelCall, LowLevelCall)):
                            g = self._hardcoded_gas(ir)
                            if g is not None:
                                reason = ("hardcodes gas ({}) on an external call -- a gas repricing "
                                          "can make it insufficient and break this path.".format(g))
                        if reason is not None:
                            key = (function.canonical_name, node.node_id)
                            if key in seen:
                                continue
                            seen.add(key)
                            results.append(self.generate_result([function, "  ", reason, "\n"]))
        return results
