#!/usr/bin/env python3

from distutils.core import setup

setup(name='bk_ssm_secrets',
      version='0.2.8',
      description='BuildKite AWS SSM Paramterstore Secrets plugin',
      author='Michaek Knox',
      author_email='mike@hfnix.net',
      url='https://hfnix.net/bk',
      packages=['shared', 'bksecrets'],
     )