#!/usr/bin/env python3
import setuptools


if __name__ == "__main__":
    setuptools.setup(
        name='bk_ssm_secrets',
        version='0.5.0',
        description='BuildKite AWS SSM Paramterstore Secrets plugin',
        author='Michaek Knox',
        author_email='mike@hfnix.net',
        url='https://hfnix.net/bk',
        packages=setuptools.find_packages(),
        install_requires=["boto3"],
        entry_points={
            'console_scripts': ['bk-ssm-secrets = bk_ssm_secrets.__main__:main']
        },
    )