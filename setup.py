

from setuptools import find_packages
from setuptools import setup

setup(
    name="simple_auth_service",
    version="0.0.1",
    license="MIT",
    maintainer="peter popov",
    description="Example om using auth features in python.",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask"]
)