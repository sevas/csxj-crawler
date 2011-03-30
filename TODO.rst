Parsers
-------

Equivalent of lesoir.py for the following sites:

- started 
  - lalibre.be
- todo
  - dhnet.be
  - lavenir.net
  - sudpresse.be
- maybe 
  - lecho.be



JSON export
-----------

But first be sure to unify the data from data sources.



Actual crawler
--------------

- Ping every every frontpage every hour or so
- Detects new stuff since last ping
- Parse and save new stuff

Probably a script to launch from cron.



Error detection
---------------

So maybe one day someone will upgrade their CMS.
This would be nice to detect it quickly so we can modify the data
extractors accordingly.
