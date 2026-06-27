from setuptools import setup, find_packages

setup(
    name="kore-agent",
    version="1.0.0",
    description="Zero-knowledge autonomous reflex agent that searches, caches, synthesizes, and self-improves",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Kashish",
    url="https://github.com/kashish/kore",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["requests>=2.25.0"],
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "kore=kore:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Education",
    ],
)
