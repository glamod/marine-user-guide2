.. Marine user manual documentation master file, created by
   sphinx-quickstart on Mon Jun 22 22:10:11 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Marine user guide's documentation!
==============================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Introduction
============

This project contains the necessary code to produce the data summaries that are
included in the Marine User Guide. These help to document the status of the
marine in situ data in the CDS after every new data release.

The marine data available in the CDS is the result of a series of data releases
that are stored in the marine data file system in different directories. This
project uses the data in the marine file system, rather than accessing to the
CDS data.

Every new data release can potentially be created with a different version of
the marine processing software. The current version of this project is
compatible with the glamod-marine-processing code up to version v1.2.


Initialize a new user guide
===========================

To initialise a new version of the Marine User Guide:

1. Create the data configuration (*mug_file*) file by merging the level2  \
configuration files of the different data releases in the current User Guide  \
version.

 .. code-block:: bash

    python <mug>/init_version/init_config.py

2. Use the sid-dck keys of the *mug_config* file to create a simple ascii file  \
with the list of sid-dcks to process (*mug_list*).

3. Create a view of the merged data releases in the User Guide data subspace:  \
this is done by linking the level2 data from the releases to the same level2  \
subdirectory in user manual subspace. The launcher script also initialises the \
subdirectory for the user guide version in the data user guide space.

  .. code-block:: bash

    ./<mug>/init_version/merge_release_data_launcher.sh *version* *mug_config* *mug_list*

  .. figure:: ../pics/file_links.png
    :width: 300
    :align: center

Data summaries
==============

1. Monthly grids

.. code-block:: bash

   ./<mug>/data_summaries/monthly_grids_launcher.sh *version* \
   <glamod-marine-config>/marine-user-guide/*version*/monthly_grids.json

2. Quality indicators time series summaries

.. code-block:: bash

   ./<mug>/data_summaries/qi_counts_ts_launcher.sh *version* \
   <glamod-marine-config>/marine-user-guide/*version*/qi_counts_ts.json
