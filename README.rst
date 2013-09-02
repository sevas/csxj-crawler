What is this ?
--------------

This software crawls articles published on the frontpage of various online news
outlets. For every article, it extracts its title, category, content, links and
links to embedded medias. The extracted data is stored in a plaintext database,
as a series of JSON files.


3rd party Dependencies
----------------------

- `scrapy <http://scrapy.org/>`_'s `HtmlXPathSelector <http://doc.scrapy.org/en/
  latest/topics/selectors.html#scrapy.selector.HtmlXPathSelector>`_ : because
  any BeautifulSoup-based app is an half-assed implementation of XPath anyway.
- `BeautifulSoup <http://www.crummy.com/software/BeautifulSoup/>`_. This project
  currently uses a mix of version 3 and 4 of BeautifulSoup. It's not pretty but
  porting the old code was not a priority. They use different namespaces so
  there are no confusions.
- `nose <http://nose.readthedocs.org/en/latest/>`_ for unit testing.

Licence
-------

This project is licensed under the MIT open-source license.
See LICENSE.txt for details.


Notes
-----

This project was tested with python 2.6 and python 2.7.