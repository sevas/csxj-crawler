from setuptools import setup
import sys
import csxj

setup(name='csxj',
      package_dir={'': '.'},
      packages=['csxj', 'csxj.datasources', 'csxj.db'],
      version=csxj.__version__,

      #PyPI metadata
      url=['http://bitbucket.org/sevas/csxj-crawler'],
      keywords=[''],
      platforms='All',
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Utilities"])
