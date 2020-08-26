from pathlib import Path

from setuptools import find_packages, setup

source_root = Path(".")
with (source_root / "README.rst").open(encoding="utf-8") as f:
    long_description = f.read()

# Read the requirements
with (source_root / "requirements.txt").open(encoding="utf8") as f:
    requirements = f.readlines()

version = "0.0.2"

setup(
    name="pandas-visual-analysis",
    version=version,
    packages=find_packages("src"),
    package_dir={"": "src"},
    url="https://github.com/meffmadd/pandas-visual-analysis",
    license="MIT License",
    author="Matthias Matt",
    author_email="matthias.matt@student.tuwien.ac.at",
    description="A package for interactive visual analysis in Jupyter notebooks.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={
        "notebook": ["jupyter-client>=6.0.0", "jupyter-core>=4.6.3"],
    },
    keywords="pandas data-science visualization data-analysis brushing linked-brushing python jupyter ipython",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering :: Visualization",
        "License :: OSI Approved :: MIT License",
        "Environment :: Console",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Intended Audience :: Healthcare Industry",
        "Framework :: IPython",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
)
