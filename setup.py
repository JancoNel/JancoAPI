from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="JancoAPI",
    version="0.1.0",
    description="A Python library with random and niche functions",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Explicitly set to Markdown
    author="Janco Nel",
    author_email="your_email@example.com",
    url="https://github.com/JancoNel/JancoAPI",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
