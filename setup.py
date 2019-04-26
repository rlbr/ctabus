from setuptools import setup, find_packages

with open('requirements.txt') as file:
    INSTALL_REQUIRES = file.read().rstrip().split('\n')

setup(
    name='ctabus',
    version='1.0.1',
    description='Python package for tracking cta bus times',
    install_requires=INSTALL_REQUIRES,
    author='rlbr',
    author_email='raphael.roberts48@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['ctabus=ctabus:main']
    }
)
