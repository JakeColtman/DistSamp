from setuptools import setup

setup(name='distsamp',
      version='1.0',
      packages=["distsamp"],
      description='Distributed Sampling library',
      install_requires=[
            "redis",
            "emcee",
            "pandas",
            "seaborn",
            "scipy"
      ])
