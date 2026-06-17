"""Setup configuration for BiasLens Python SDK."""

from setuptools import setup, find_packages

setup(
    name="biaslense",
    version="1.1.0",
    description="Detect and mitigate sociocultural bias in AI-generated text",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    author="Jaspreet Singh Ahluwalia",
    author_email="jaspreetahluwalia007@gmail.com",
    url="https://github.com/JaspreetSinghA/biaslense",
    license="MIT",
    packages=find_packages(exclude=["tests", "examples", "archive", "docs"]),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.28.0",
        "pydantic>=2.0",
        "mcp>=1.0.0",
    ],
    entry_points={
        "console_scripts": [
            "biaslens-mcp=biaslense.mcp_server:main",
            "biaslens-mcp-local=biaslense.mcp_server_local:main",
        ],
    },
    extras_require={
        "dev": [
            "pytest>=7.0",
            "black>=22.0",
            "mypy>=0.990",
        ],
        "local": [
            "scikit-learn>=1.0",
            "sentence-transformers>=2.2",
            "numpy>=1.24",
            "pandas>=1.5",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Development Status :: 4 - Beta",
        "Operating System :: OS Independent",
    ],
    keywords="bias detection ai fairness nlp machine-learning",
    project_urls={
        "Bug Tracker": "https://github.com/JaspreetSinghA/biaslense/issues",
        "Documentation": "https://github.com/JaspreetSinghA/biaslense#readme",
        "Source Code": "https://github.com/JaspreetSinghA/biaslense",
    },
)
