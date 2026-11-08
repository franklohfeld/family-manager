"""
Setup-Datei für den Familienkalender.
"""

from setuptools import setup, find_packages

setup(
    name="family-calendar",
    version="1.0.0",
    description="Familienkalender auf dem Raspberry Pi mit Touchscreen",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.11",
    install_requires=[
        "PyQt5==5.15.10",
        "google-api-python-client==2.108.0",
        "google-auth-httplib2==0.2.0",
        "google-auth-oauthlib==1.1.0",
        "holidays==0.42",
        "python-dotenv==1.0.0",
        "PyYAML==6.0.1",
    ],
    entry_points={
        "console_scripts": [
            "family-calendar=src.main:main",
        ],
    },
)
