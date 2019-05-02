from setuptools import setup, find_packages

with open('requirements.txt') as file:
    INSTALL_REQUIRES = file.read().rstrip().split('\n')

setup(
    name='ctabus',
    version='2.1.3',
    description='Python package for tracking cta bus times',
    install_requires=INSTALL_REQUIRES,
    author='rlbr',
    author_email='raphael.roberts48@gmail.com',
    packages=find_packages(),
    entry_points={
        'console_scripts': ['ctabus=ctabus:main']
    },
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',

    ]

)
