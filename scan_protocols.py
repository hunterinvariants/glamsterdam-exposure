#!/usr/bin/env python3
"""Gas-reprice exposure scan over Etherscan-verified source.

For each deployed contract in targets.json: fetch its Etherscan-verified source (the actual deployed
code -- self-contained, deps inlined, so no repo build is needed), follow a proxy to its implementation
if necessary, compile with the matching solc (pulled on demand via solc-select), and run the
`gas-reprice-fragile` detector. Aggregate the hits into GLAMSTERDAM_IMPACT.md. Every flagged site is a
real line in deployed code.

targets.json:  [{"name": "WETH9", "address": "0xC02a..."}, ...]
Needs ETHERSCAN_API_KEY in the environment (read from env, never hardcoded) and solc-select on PATH.

Usage:  python scan_protocols.py targets.json
"""
import json
import os
import re
import shutil
import subprocess
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
SCRATCH = os.path.join(HERE, "_scan")
API = "https://api.etherscan.io/v2/api"
KEY = os.environ.get("ETHERSCAN_API_KEY", "")
ADDR = re.compile(r"^0x[0-9a-fA-F]{40}$")


def get_raw(address):
    """One getsourcecode call -> the result dict (or None)."""
    q = urllib.parse.urlencode({
        "chainid": "1", "module": "contract", "action": "getsourcecode",
        "address": address, "apikey": KEY,
    })
    try:
        with urllib.request.urlopen(API + "?" + q, timeout=60) as r:
            data = json.loads(r.read().decode())
    except Exception:
        return None
    if str(data.get("status")) != "1" or not data.get("result"):
        return None
    return data["result"][0]


def write_file(dest, relpath, content):
    fp = os.path.join(dest, relpath.lstrip("/"))
    os.makedirs(os.path.dirname(fp), exist_ok=True)
    open(fp, "w", encoding="utf-8").write(content)


def pick_entry(dest, paths, name):
    paths = list(paths)
    for p in paths:
        if os.path.basename(p) == name + ".sol":
            return os.path.join(dest, p.lstrip("/"))
    for p in paths:
        fp = os.path.join(dest, p.lstrip("/"))
        try:
            if re.search(r"\b(contract|library)\s+" + re.escape(name) + r"\b",
                         open(fp, encoding="utf-8").read()):
                return fp
        except Exception:
            pass
    return dest


def lay_down(dest, res):
    """Write res's SourceCode under dest. Returns (entry_path, remaps)."""
    src = (res.get("SourceCode") or "").strip()
    name = (res.get("ContractName") or "Contract").strip()
    if not src:
        return None, []
    if src.startswith("{{") and src.endswith("}}"):
        sj = json.loads(src[1:-1])
        sources = sj.get("sources", {}) or {}
        remaps = (sj.get("settings", {}) or {}).get("remappings", []) or []
        for path, obj in sources.items():
            write_file(dest, path, obj.get("content", "") if isinstance(obj, dict) else str(obj))
        return pick_entry(dest, sources.keys(), name), remaps
    if src.startswith("{"):
        sources = json.loads(src)
        for path, obj in sources.items():
            write_file(dest, path, obj.get("content", "") if isinstance(obj, dict) else str(obj))
        return pick_entry(dest, sources.keys(), name), []
    os.makedirs(dest, exist_ok=True)
    fp = os.path.join(dest, name + ".sol")
    open(fp, "w", encoding="utf-8").write(src)
    return fp, []


def fetch(address):
    """Returns (status, root, entry, solc, remaps, impl_addr)."""
    res = get_raw(address)
    if res is None:
        return "api-error", None, None, None, [], None
    impl_addr = None
    impl = (res.get("Implementation") or "").strip()
    if str(res.get("Proxy")) == "1" and ADDR.match(impl) and impl.lower() != address.lower():
        res2 = get_raw(impl)
        if res2 and (res2.get("SourceCode") or "").strip():
            res, impl_addr = res2, impl
    m = re.search(r"(\d+\.\d+\.\d+)", res.get("CompilerVersion") or "")
    solc = m.group(1) if m else None
    if not (res.get("SourceCode") or "").strip():
        return "not-verified", None, None, solc, [], impl_addr
    root = os.path.join(SCRATCH, address)
    os.makedirs(root, exist_ok=True)
    try:
        entry, remaps = lay_down(root, res)
    except Exception:
        return "parse-error", None, None, solc, [], impl_addr
    if not entry:
        return "not-verified", None, None, solc, [], impl_addr
    return "ok", root, entry, solc, remaps, impl_addr


def ensure_solc(version):
    """Install the requested solc via solc-select. Returns True if a usable solc is in place
    (already-installed is idempotent and returns 0), False if the install failed."""
    if not version:
        return True
    try:
        p = subprocess.run(["solc-select", "install", version],
                           capture_output=True, text=True, timeout=300)
        return p.returncode == 0
    except Exception:
        return False


def scan(root, entry, solc, remaps):
    env = dict(os.environ)
    if solc:
        env["SOLC_VERSION"] = solc
    # run from the contract's source root so its embedded remappings resolve
    target = os.path.relpath(entry, root) if entry and entry != root else "."
    cmd = ["slither", target, "--detect", "gas-reprice-fragile", "--json", "-"]
    if remaps:
        cmd += ["--solc-remaps", " ".join(remaps)]
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=600, env=env, cwd=root)
    except subprocess.TimeoutExpired:
        return "timeout", []
    try:
        data = json.loads(p.stdout)
    except Exception:
        return "build-failed", []
    seen, findings = set(), []
    for d in (data.get("results") or {}).get("detectors", []):
        if d.get("check") != "gas-reprice-fragile":
            continue
        desc = (d.get("description") or "").strip().splitlines()[0].strip()
        sm = ((d.get("elements") or [{}])[0]).get("source_mapping") or {}
        fl, lines = sm.get("filename_short"), (sm.get("lines") or [])
        loc = "{}:{}".format(fl, lines[0]) if fl and lines else (fl or "")
        if desc in seen:
            continue
        seen.add(desc)
        findings.append({"desc": desc, "loc": loc})
    return ("ok" if findings else "clean"), findings


def write_report(rows):
    built = [r for r in rows if r["status"] in ("ok", "clean")]
    exposed = [r for r in rows if r["findings"]]
    total = sum(len(r["findings"]) for r in rows)

    o = ["# Glamsterdam exposure report\n"]
    o += ["Deployed contracts that use a pattern a Glamsterdam gas repricing can break -- the fixed",
          "2300-gas `.transfer` / `.send` stipend and hardcoded call gas (the class EIP-1884 broke in",
          "2019). Source is pulled from Etherscan (verified = the deployed bytecode), proxies are",
          "followed to their implementation, each contract is compiled with its original solc, and",
          "scanned with the `gas-reprice-fragile` detector. Every site is a real line in deployed code.\n",
          "## Summary\n",
          "- contracts scanned (compiled): {}".format(len(built)),
          "- contracts with fragile sites: {}".format(len(exposed)),
          "- total flagged sites: {}\n".format(total),
          "| Contract | Address | solc | Status | Sites |",
          "|---|---|---|---|:--:|"]
    for r in rows:
        sites = len(r["findings"]) if r["status"] in ("ok", "clean") else "--"
        o.append("| {} | `{}` | {} | {} | {} |".format(
            r["name"], r["address"], r["solc"] or "?", r["status"], sites))
    o.append("\n## Sites\n")
    if exposed:
        for r in exposed:
            head = "### {}  (`{}`)".format(r["name"], r["address"])
            if r.get("impl"):
                head += "  -- via implementation `{}`".format(r["impl"])
            o.append(head)
            for f in r["findings"]:
                o.append("- {}  ({})".format(f["desc"], f["loc"]))
            o.append("")
    else:
        o.append("No fragile sites in the scanned set.\n")
    o += ["## Reading this\n",
          "The risk is narrow by design: the 2300-gas stipend only bites raw-ETH `.transfer` / `.send`.",
          "Contracts that pay ETH with `.call{value: ...}(\"\")` are unaffected, and most post-2019 code",
          "moved to `.call`. A `clean` row is a real result -- that contract is not gas-reprice-fragile.",
          "A flagged row is a deployed contract whose ETH path forwards a fixed gas budget a repricing",
          "can underfund. `build-failed` is a source whose compile did not resolve cold; it is recorded,",
          "not dropped.\n",
          "## Reproduce\n", "```",
          "ETHERSCAN_API_KEY=... python scan_protocols.py targets.json", "```"]

    open(os.path.join(HERE, "GLAMSTERDAM_IMPACT.md"), "w", encoding="utf-8").write("\n".join(o) + "\n")
    sys.stderr.write("\nwrote GLAMSTERDAM_IMPACT.md  ({} compiled, {} exposed, {} sites)\n".format(
        len(built), len(exposed), total))


def main():
    if not KEY:
        sys.exit("set ETHERSCAN_API_KEY in the environment first")
    if shutil.which("solc-select") is None:
        sys.exit("solc-select not on PATH -- install it first:  pipx install solc-select  "
                 "(or pip install solc-select). Each contract is compiled with its original solc, "
                 "pulled on demand; without solc-select every non-default-solc source build-fails "
                 "silently, which understates the result.")
    targets = json.load(open(sys.argv[1] if len(sys.argv) > 1 else "targets.json"))
    rows = []
    for t in targets:
        status, root, entry, solc, remaps, impl = fetch(t["address"])
        if status == "ok":
            if ensure_solc(solc):
                status, findings = scan(root, entry, solc, remaps)
            else:
                status, findings = "solc-failed", []
        else:
            findings = []
        sys.stderr.write("{:<26} {:<13} {} site(s)  [solc {}]{}\n".format(
            t["name"], status, len(findings), solc or "?", "  (proxy)" if impl else ""))
        rows.append({"name": t["name"], "address": t["address"], "status": status,
                     "solc": solc, "findings": findings, "impl": impl})
        time.sleep(0.25)
    write_report(rows)


if __name__ == "__main__":
    main()
