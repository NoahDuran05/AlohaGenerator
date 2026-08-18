from setuptools import setup, find_packages

setup(
    name="aloha_api",  # The name of your package
    version="1.1.0",  # Initial version
    packages=find_packages(), install_requires=['aloha-blog', 'pydantic', 'typing']  # Automatically find all packages/subpackages
)
