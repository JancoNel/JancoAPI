from setuptools import setup, find_packages

setup(
    name="JancoAPI",
    version="0.1.0",
    description="A Python library with random and niche functions",
    long_description="This is a Python package that offers various utilities.",  # Hardcoded vague description
    long_description_content_type="text/plain",  # Set content type to plain text
    author="Janco Nel",
    url="https://github.com/JancoNel/JancoAPI",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
