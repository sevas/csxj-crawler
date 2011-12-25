from setuptools import setup
import sys
import csxj

setup(name='csxj',
      package_dir={'': '.'},
      packages=['csxj', 'csxj.common',
                'csxj.datasources', 'csxj.datasources.common',
                'csxj.db'],
      scripts=['scripts/csxj_update_all_queues.py',
               'scripts/csxj_download_queued_articles.py'],
      version=csxj.__version__,

      #PyPI metadata
      url=['http://bitbucket.org/sevas/csxj-crawler'],
      zip_safe=False,
      keywords=[''],
      platforms='All',
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Programming Language :: Python",
        "Topic :: Software Development",
        "Topic :: Utilities"])
