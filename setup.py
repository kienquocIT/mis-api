# Description define in here
# https://github.com/pypa/sampleproject/blob/db5806e0a3204034c51b1c00dde7d5eb3fa2532e/setup.py

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

long_description = (here / "README.md").read_text(encoding="utf-8")
requirements = (here / "req.txt").read_text(encoding="utf-8").splitlines()

setup(
    name='MIS-API',
    version='1.0.0',
    # long_description=long_description,
    # long_description_content_type="text/markdown",
    # author="Dev Team of Minh Tam Solution",
    # author_email="dev@mtsolution.com.vn",
    # classifiers=[  # Optional
    #     # How mature is this project? Common values are
    #     #   3 - Alpha
    #     #   4 - Beta
    #     #   5 - Production/Stable
    #     "Development Status :: 3 - Alpha",
    #     # Indicate who your project is intended for
    #     "Intended Audience :: Developers",
    #     "Topic :: Software Development :: Build Tools",
    #     # Pick your license as you wish
    #     "License :: OSI Approved :: MIT License",
    #     # Specify the Python versions you support here. In particular, ensure
    #     # that you indicate you support Python 3. These classifiers are *not*
    #     # checked by 'pip install'. See instead 'python_requires' below.
    #     "Programming Language :: Python :: 3",
    #     "Programming Language :: Python :: 3.10",
    #     "Programming Language :: Python :: 3 :: Only",
    # ],
    # python_requires=">=3.11",
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    extras_require={
        ':sys_platform == "win32"': [
            'python-magic-bin==0.4.14',
        ],
        ':sys_platform == "linux"': [
            'python-magic==0.4.27',
        ],
    }
)
