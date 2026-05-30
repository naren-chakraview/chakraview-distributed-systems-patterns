from setuptools import setup, find_packages

setup(
    name="chakraview-edge-agents",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "langgraph==0.0.21",
        "langchain-core==0.1.0",
        "pydantic==2.5.0",
        "grpcio==1.56.0",
        "protobuf==4.25.0",
        "opentelemetry-api==1.19.0",
        "aiohttp==3.9.0",
    ],
    extras_require={
        "test": ["pytest>=7.0", "pytest-asyncio>=0.21.0"],
    },
)
