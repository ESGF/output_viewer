from setuptools import setup, find_packages
import os


setup(
    name="output_viewer",
    version="1.0.0",
    description="Framework for building web pages to examine output.",
    author="Sam Fries",
    author_email="fries2@llnl.gov",
    install_requires=["requests"],
    packages=find_packages(),
    include_package_data=True,
    scripts=["scripts/view_output", "scripts/view_output.py", "scripts/upload_output", "scripts/upload_output.py"]
)
