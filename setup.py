from setuptools import setup

setup(
    name="sec",
    version="0.2.0",
    description=(
        "Simple library for working with secrets in both files and "
        "environment variables."
    ),
    py_modules=["sec"],
    url="https://github.com/sourcelair/sec",
    author="Antonis Kalipetis, Paris Kasidiaris",
    author_email="accounts@sourcelair.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Secrets",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    keywords='secrets development',
)
