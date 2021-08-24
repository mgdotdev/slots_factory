import os.path

from setuptools import setup, find_packages, Extension

extensions = [
    Extension(
        "slots_factory.tools.SlotsFactoryTools",
        [os.path.join("src", "slots_factory", "tools", "slots_factory_tools.c")],
    )
]


with open("README.md", "r") as f:
    long_description = f.read()


setup(
    author="Michael Green",
    author_email="michael@michaelgreen.dev",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    ext_modules=extensions,
    extras_require={"test": ["pytest"]},
    include_package_data=True,
    license="LGPLv3",
    long_description_content_type="text/markdown",
    long_description=long_description,
    name="slots_factory",
    packages=find_packages(where="src"),
    package_data={"": ["*.txt"]},
    package_dir={"": "src"},
    python_requires=">=3.6",
    tests_require=["pytest"],
    url="https://github.com/1mikegrn/slots_factory",
    version="0.1.2",
)
