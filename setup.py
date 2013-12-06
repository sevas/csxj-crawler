from setuptools import setup, find_packages
import csxj

setup(
    name='csxj',

    packages=find_packages(),
    scripts=[
        'scripts/csxj_update_all_queues.py',
        'scripts/csxj_download_queued_articles.py',
        'scripts/csxj_cleanup_cached_metainfo.py',
        'scripts/csxj_update_metainfo.py',
        'scripts/csxj_list_errors.py',
        'scripts/csxj_queue_troubleshooting.py',
        'scripts/csxj_process_errors.py'],

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
