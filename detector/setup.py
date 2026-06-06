from setuptools import setup, find_packages

setup(
    name="slither-glamsterdam",
    version="0.1.0",
    description="Slither detector for gas-reprice-fragile patterns (Glamsterdam upgrade readiness)",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=["slither-analyzer"],
    entry_points={"slither_analyzer.plugin": ["slither-glamsterdam=slither_glamsterdam:make_plugin"]},
)
