from setuptools import setup, find_packages

setup(
    name="JancoAPI",  # Your package name
    version="0.1.0",  # Version of your package
    description="A Python library with random and niche functions",
    author="Janco Nel",
    url="https://github.com/JancoNel/JancoAPI",  # GitHub repo URL
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
