Ship logs at NARA
=================

The `National Archives and Records Administration <https://www.archives.gov>`_ (NARA, in the USA) hold an enormous number of historical records of value to climate research. Those holdings include many ship's logbooks - many of which are available online as scanned images. I'd like to get a good picture of what logbook records are available from NARA.

The NARA catalog is available online through a `web interface <https://www.archives.gov/research/catalog/help/using.html>`_ and this works well for finding and browsing individual logs (e.g. `USS Jeannette in 1880 <https://catalog.archives.gov/id/6919193>`_) but to look at records in bulk we need to go beyond a point-and-click interface. NARA support such advanced use by making their entire catalog database `available to download. <https://registry.opendata.aws/nara-national-archives-catalog/>`_

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Download the full catalog <get_catalog>

To use the catalog data we have to understand its structure, and it's easy to study as each record is a single line of JSON (a text format) so we can read it directly. But it's much easier if we pretty-print selected records to show the record structure explicitly.

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Pretty-printer script <pretty_print>
   Pretty-printer sample output<pretty_printed/Yantic>

With a clear idea of the record structure, we can then write code to make summaries of the records we are interested in, as spreadsheet (CSV) tables.

.. toctree::
   :titlesonly:
   :maxdepth: 1

   Logbook record summariser script <to_csv>



.. toctree::
   :titlesonly:
   :maxdepth: 1

   How to reproduce or extend this work <how_to>
   Authors and acknowledgements <credits>

This document is crown copyright (2021). It is published under the terms of the `Open Government Licence <https://www.nationalarchives.gov.uk/doc/open-government-licence/version/2/>`_. Source code included is published under the terms of the `BSD licence <https://opensource.org/licenses/BSD-2-Clause>`_. Catalog data used are taken from NARA and `licensed as US Government work. <https://registry.opendata.aws/nara-national-archives-catalog/>`_
