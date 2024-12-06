from setuptools import setup, find_packages

setup(
    name="crewai_langchain",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        "sqlalchemy",
        "aiohttp",
        "pyjwt",
        "fastapi",
        "python-dotenv"
    ]
) 