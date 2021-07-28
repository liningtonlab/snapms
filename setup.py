from setuptools import setup, find_packages

# Don't worry about including data correctly since this is intended
# to include be installed as a symbolic link for easier
# imports in notebooks
setup(
    name="snapms",
    version="1.0.0",
    packages=find_packages(),
    include_package_data=True,
)
