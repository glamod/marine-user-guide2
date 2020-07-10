.. Marine user manual documentation master file, created by
   sphinx-quickstart on Mon Jun 22 22:10:11 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Marine user guide's documentation!
==============================================

.. toctree::
   :maxdepth: 3
   :caption: Contents:




Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`


Introduction
============

This project contains the necessary code to produce the data summaries that are
included in the Marine User Guide. These help document the status of the marine
in situ data in the CDS after every new data release.

The marine data available in the CDS is the result of a series of data releases
that are stored in the marine data file system in different directories. This
project uses the data in the marine file system, rather than accessing to the
CDS data.

Every new data release can potentially be created with a different version of
the marine processing software. The current version of this project is
compatible with the glamod-marine-processing code up to version v1.2.

Additionally, the tools employed to create the individual source deck reports
are also available in this project. These can be created for a single data
release or for the combination of releases included in a Marine User Guide
version.

Tool set-up
===========

Code set up
-----------

Clone the remote repository:

.. code-block:: bash

  git clone git@git.noc.ac.uk:iregon/marine-user-guide.git

Build the python environment using the requirements.txt file in marine-user-guide/env. This
step system dependent. The following code block described the steps to
follow in CEDA JASMIN, using the Jaspy toolkit.

.. code-block:: bash

  cd marine-user-guide/env
  module load jaspy/3.7
  virtualenv -–system-site-packages mug_env
  source mug_env/bin/activate
  pip install -r requirements.txt


Data directory setup
--------------------

The data that the tools in this project use and the products created are all
stored in the marine-user-guide data directory, which is organized in separate
directories to host the different versions of the Marine User Guide.

.. figure:: ../pics/in_data_space.pdf
  :width: 150
  :align: center

This general directory needs to be created before starting using the tool.

.. code-block:: bash

  cd <parent_data_directory>
  mkdir marine-user-guide


Paths setup
-----------

Edit file marine-user-guide/setpaths.sh and modify as needed the following fields:

* code_directory: parent path of the repository installation.
* data_directory: parent path of the Marine User Guide data directory.


Marine User Guide
=================

Initialize a new user guide
---------------------------

Every new version of the Marine User Guide (MUG) needs to be initialised in the
tools' data directory (:ref:`file_links`). This means:

* Creating the appropriate data configuration files to reflect the combination \
  of individual data releases that generate the version.
* Creating a subdirectory for the version in the data directory.
* Create a view of the merged data releases: rather than copying all the \
  files to a common location, this is done by linking the level2 data from the \
  different releases to the marine-user-guide data directory.

.. _file_links:

.. figure:: ../pics/file_links.png
  :width: 300
  :align: center

  Marine User Guide data directory and its relation to the data releases directories.

These steps initialize a new user guide:

1. Create the data configuration file (*mug_file*,:ref:`mug_config`) by merging the level2 \
(:ref:`level2`) configuration files of the different data releases included in the new version.

.. code-block:: bash

  python marine-user-guide/init_version/init_config.py

2. Use the sid-dck keys of the *mug_config* file to create a simple ascii file \
with the full list source-deck IDs of the release merge (*mug_list*).

3. Create a view of the merged data releases. The launcher script also \
initialises the subdirectory for the new version.

.. code-block:: bash

  ./marine-user-guide/init_version/merge_release_data_launcher.sh version mug_config mug_list


Check that the copies really reflect the merge of the releases. \
Edit the following script to add the corresponding paths and run. If any does \
not match, it will prompt an error.

.. code-block:: bash

  ./marine-user-guide/init_version/merge_release_data_check.sh


Data summaries
--------------

The data summaries are monthly aggregations of all the source-deck ID partitions
in the data.

Monthly grids
^^^^^^^^^^^^^

These are monthly aggregations in a lat-lon grid which are stored in nc files:

  * header table: number of reports per grid cell per month
  * observations tables: number of observations and observed_value mean per grid \
    cell per month.

All the aggregations are configured in a common configuration file, \
monthly_grids.json (:ref:`mon_grids_config`). The current configuration excludes
reports not passing all the quality checks, but this can be configured in the
configuration file.

A launcher bash script configures the LSF job for each table and logs to \
/log/monthly_grids/*table*.log in the data directory.

.. code-block:: bash

   ./marine-user-guide/data_summaries/monthly_grids_launcher.sh version monthly_grids.json


Monthly time series of selected quality indicators
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Monthly summaries of categorical counts of quality indicators aggregated over
all the source-deck IDs. These are additionally, split in counts by main
platform types (ships and buoys) and include the total number of reports. They
are stored in ascii pipe separated files.

The configuration file, qi_counts_ts.json (:ref:`qi_counts_config`), includes \
very limited parameterization, with the platform type segregation pending to be \
parameterized.

A launcher bash script configures the LSF job for each quality indicator \
(currently only report_quality and duplicate_status) and logs to \
/logqi_counts_ts/*quality_indicator*.log in the data directory.

.. code-block:: bash

   ./marine-user-guide/data_summaries/qi_counts_ts_launcher.sh version qi_counts_ts.json


Figures
-------

The data summaries generated are used to generatd a series of maps and time series
plots. The following sections give the necessary directives to create them, with
references to the configuration files used.

Number of reports time series plot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Data summary used: report_quality quality indicators time series.
* Configuration file: nreports_ts.json (:ref:`nreports_ts_config`)
* Command:

  .. code-block:: bash

    source /marine-user-guide/setpaths.sh
    source /marine-user-guide/setenv.sh
    python /marine-user-guide/figures/nreports_ts.py nreports_ts.json

Duplicate status time series plot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    * Data summary used: duplicate_status quality indicators time series.
    * Configuration file: nreports_dup_ts.json (:ref:`nreports_dup_ts_config`)
    * Command:

      .. code-block:: bash

        source /marine-user-guide/setpaths.sh
        source /marine-user-guide/setenv.sh
        python /marine-user-guide/figures/nreports_dup_ts.py nreports_dup_ts.json


Report quality time series plot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    * Data summary used: report_quality quality indicators time series.
    * Configuration file: nreports_qc_ts.json (:ref:`nreports_qc_ts_config`)
    * Command:

      .. code-block:: bash

        source /marine-user-guide/setpaths.sh
        source /marine-user-guide/setenv.sh
        python /marine-user-guide/figures/nreports_qc_ts.py nreports_qc_ts.json

Seasonal and monthly Hovmöller plots
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    * Data summary used: monthly grids (counts, header and observation tables)
    * Configuration file: nreports_hovmoller.json (:ref:`nreports_hovmoller_config`)
    * Command:

      .. code-block:: bash

        source /marine-user-guide/setpaths.sh
        source /marine-user-guide/setenv.sh
        python /marine-user-guide/figures/nreports_hovmoller.py nreports_hovmoller.json


ECV nreports and converge time series
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    * Data summary used: monthly grids (counts, header and observation tables)
    * Configuration file: ecv_coverage_ts_grid.json (:ref:`ecv_coverage_config`)
    * Command:

      .. code-block:: bash

        source /marine-user-guide/setpaths.sh
        source /marine-user-guide/setenv.sh
        python /marine-user-guide/figures/ecv_coverage_ts_grid.py ecv_coverage_ts_grid.json

Maps with number of observations and number of months observed
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  * Data summary used: monthly grids (counts, header and observation tables)
  * Configuration file: map_nobs_from_monthly_nc.json (:ref:`map_nobs_config`)
  * Command:

    .. code-block:: bash

      source /marine-user-guide/setpaths.sh
      source /marine-user-guide/setenv.sh
      python /marine-user-guide/figures/map_nobs_from_monthly_nc.py map_nobs_from_monthly_nc.json

Maps with ECVs mean observations value
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

  * Data summary used: monthly grids (mean, observation tables only)
  * Configuration file: map_mean_from_monthly_nc.json (:ref:`map_mean_config`)
  * Command:

    .. code-block:: bash

      source /marine-user-guide/setpaths.sh
      source /marine-user-guide/setenv.sh
      python /marine-user-guide/figures/map_mean_from_monthly_nc.py map_mean_from_monthly_nc.json


Individual source-deck reports
==============================

The source_deck_list is a simple ascii file with the list of source ID - deck ID
pairs to process by the launcher script.

Reports on a release merge
--------------------------

TBC

Data data summaries
-------------------
The data summaries are monthly aggregations of the individual source-deck's
table files.

Monthly grids
^^^^^^^^^^^^^

These are monthly aggregations in a lat-lon grid which are stored in nc files:

  * header table: number of reports per grid cell per month
  * observations tables: number of observations and observed_value mean, max \
    and min per grid cell per month.

The aggregations for all the tables are configured in a common configuration
file. There are currently two configurations that need to be run to create
the data summaries needed: full dataset and optimal (all quality control
checks passed) dataset. The corresponding configuration files are:

  * Full dataset: monthly_grids_all.json (:ref:`monthly_grids_sd_all`)
  * Optimal dataset: monthly_grids_optimal.json (:ref:`monthly_grids_sd_optimal`)

A launcher bash script configures the SLURM job for each table and logs to \
/log/sid-dck/*config_file*-*table*.log in the log directory.

.. code-block:: bash

   ./marine-user-guide/data_summaries_sd/monthly_grids_sd_launcher.sh log_dir config_file source_deck_list



.. _appendix:

Appendix 1. Marine User Guide configuration files
=================================================

.. _level2:

level2 file format
------------------

.. literalinclude:: ../config_files/release_20_level2.json
  :caption: Release_2.0 level2 file extract

.. literalinclude:: ../config_files/r092019_level2.json
  :caption: r092019 level2 file extract


.. _mug_config:

Marine user guide data configuration file
-----------------------------------------

.. literalinclude:: ../config_files/mug_v4_config.json
  :caption: Marine User Guide v4 configuration file extract



.. _mon_grids_config:

monthly_grids configuration
---------------------------

.. literalinclude:: ../config_files/monthly_grids.json


.. _qi_counts_config:

qi_counts configuration
-----------------------

.. literalinclude:: ../config_files/qi_counts_ts.json

.. _nreports_ts_config:

nreports_ts configuration
-------------------------

.. literalinclude:: ../config_files/nreports_ts.json

.. _nreports_dup_ts_config:

nreports_dup_ts configuration
-----------------------------

.. literalinclude:: ../config_files/nreports_dup_ts.json

.. _nreports_qc_ts_config:

nreports_qc_ts configuration
----------------------------

.. literalinclude:: ../config_files/nreports_qc_ts.json

.. _nreports_hovmoller_config:

nreports_hovmoller configuration
--------------------------------

.. literalinclude:: ../config_files/nreports_hovmoller.json


.. _ecv_coverage_config:

ecv_coverage configuration
--------------------------

.. literalinclude:: ../config_files/ecv_coverage_ts_grid.json


.. _map_mean_config:

map_mean configuration
--------------------------

.. literalinclude:: ../config_files/map_mean_from_monthly_nc.json

.. _map_nobs_config:

map_nobs configuration
----------------------

.. literalinclude:: ../config_files/map_nobs_from_monthly_nc.json


.. _appendix_sd:

Appendix 2. Individual source-deck reports configuration files
==============================================================

.. _monthly_grids_sd_optimal:

monthly grids optimal dataset
-----------------------------

.. literalinclude:: ../config_files_sd/monthly_grids_optimal.json


.. _monthly_grids_sd_all:

monthly grids full dataset
--------------------------

.. literalinclude:: ../config_files_sd/monthly_grids_all.json
