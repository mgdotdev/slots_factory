import os.path

from setuptools import setup, find_packages, Extension

HERE = os.path.dirname(os.path.abspath(__file__))

extensions = [
    Extension(
        "slots_factory.tools.SlotsFactoryTools",
        [os.path.join('src', 'slots_factory', 'tools', 'slots_factory_tools.c')]
    )
]

setup(
    ext_modules = extensions,
    include_package_data=True,
    name='slots_factory',
    packages=find_packages(where="src"),
    package_dir={"": "src"},  
    zip_safe=False,
)