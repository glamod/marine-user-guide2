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
project uses the data in the marine file system, rather than accessing the CDS
data.

Every new data release can potentially be created with a different version of
the marine processing software. The current version of this project is
compatible with the glamod-marine-processing code up to version v1.1.

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

The data the tools in this project use and the products created are stored
in the marine-user-guide data directory [#fDDS]_. This directory does not contain
the actual data files of the individual data releases, but links to the files in
the directories of the data releases included in a version of the Marine User Guide. This approach
greatly simplifies the configuration of the different scripts and is followed
even if a given version is made up of a single data release.

The marine-user-guide data directory is then split in directories to host
subsequent versions of the Marine User Guide.

.. figure:: ../pics/in_data_space.pdf
  :width: 150
  :align: center

This general directory needs to be created before starting using the tool.

.. code-block:: bash

  cd <parent_data_directory>
  mkdir marine-user-guide



.. rubric:: Footnotes

.. [#fDDS] When producing data summaries and figures of individual source-decks \
  of a single release, the data would normally be accessed directly from the \
  release data directory.


Paths setup
-----------

Edit file marine-user-guide/setpaths.sh and modify as needed the following fields:

* code_directory: parent path of the repository installation.
* data_directory: parent path to the data release directories.
* mug_code_directory: marine user guide code directory installation.
* mug_data_directory: marine user guide data directory path.



Marine User Guide
=================

Every C3S Marine User Guide version includes a series of figures that describe
the marine in situ data holdings in the CDS. The following sections explain how
these figures are created for every new version of the Marine User Guide.

Initializing a new user guide
-----------------------------

Every new version of the Marine User Guide (MUG) needs to be initialised in the
tools' data directory as shown in the figure.

.. _file_links:

.. figure:: ../pics/file_links.png
  :width: 300
  :align: center

  Marine User Guide data directory and its relation to the individual data \
  releases' directories.


These steps initialize a new version:

1. Create the data configuration file (*mug_file*, :ref:`mug_config`) by merging \
the level2 configuration files of the different data releases \
included in the new version ( :ref:`level2`).

  .. code-block:: bash

    source marine-user-guide/setpaths.sh
    source marine-user-guide/setenv.sh
    python marine-user-guide/init_version/init_config.py

2. Use the sid-dck keys of the *mug_config* file to create a simple ascii file \
with the full list of source-deck IDs of the release merge (*mug_list*).

3. Create the directory tree for the version in the  in the marine-user-guide \
data directory.

  .. code-block:: bash

    source marine-user-guide/setpaths.sh
    source marine-user-guide/setenv.sh
    python /marine-user-guide/init_version/create_version_dir_tree.py mug_path version mug_config

  where:

  * mug_path: full path to the marine-user-guide data directory
  * version: tag to use for Marine User Guide version
  * mug_config: path to *mug_config* file

4. Populate it with a view of the merged data releases: rather than copying all \
the files, this is done by linking the corresponding files from the releases' \
directories to the marine-user-guide data directory. Data linked is the level2 \
data files and level1a and level1c quicklook json files.

A launcher bash script configures the SLURM job for each *sid-dck* data partition
and logs to level2/log/*sid-dck*/merge_release_data.*ext*, with *ext* being *ok* or
*failed* depending on job termination status.

  .. code-block:: bash

    ./marine-user-guide/init_version/merge_release_data.slurm version mug_config mug_list

  where:

  * version: tag to use for Marine User Guide version
  * mug_config: path to *mug_config* file
  * mug_list: path to *mug_list* file.

5. Check that the copies really reflect the merge of the releases. \
Edit the following script to add the corresponding paths and run. If any does \
not match, it will prompt an error.

.. code-block:: bash

  ./marine-user-guide/init_version/merge_release_data_check.sh


Data summaries
--------------

The data summaries are monthly aggregations over all the source-deck ID partitions
in the data. These aggregations are on the data counts and observation values
and on some relevant quality indicators and are the basis to then create the
time series plots and maps included in the MUG.

Monthly grids
^^^^^^^^^^^^^

Aggregations in a monthly lat-lon grids. The CDM table determines what
aggregations are applied:

  * header table: number of reports per grid cell per month.
  * observations tables: number of observations and mean observed_value per grid \
    cell per month.

Each aggregation is stored in an individual netcdf file.

All the aggregations are configured in a common configuration file,
:ref:`mon_grids_um`. The current configuration for the MUG excludes reports
not passing all the quality checks. The same tool can be used to produce
data summaries with different filter criteria, but modifying the filter values
in the configuration file.

A launcher bash script configures the SLURM job for each CDM table and logs
to level2/log/*sid-dck*/*config_file*-*table*.*ext*, with *ext* being *ok* or
*failed* depending on job termination status.

.. code-block:: bash

   ./marine-user-guide/data_summaries/monthly_grids.slurm version config_file

where:

* version: tag to use for Marine User Guide version
* config_file: path to the monthly grids configuration file


Selected quality indicators time series
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Monthly summaries of categorical counts of quality indicators in the header table
aggregated over all the source-deck IDs. These are additionally, split in counts by main
platform types (ships and buoys) and include the total number of reports. They
are stored in ascii pipe separated files.

The configuration file, qi_counts_ts.json (:ref:`qi_counts_um`), includes \
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


ECV nreports and coverage time series
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

To create reports on a merge of data releases, bla,bla, with the quicklooks!


Data data summaries
-------------------

The data summaries are monthly aggregations of report counts, observation values
and additional CDM fields of the individual source-deck's table files.

Monthly grids
^^^^^^^^^^^^^

Monthly aggregations in a latitude-longitude grid, stored in nc files. The
aggregations depend on the CDM table:

  * header table: number of reports.
  * observations tables: number of observations and observed_value mean, max \
    and min.

The aggregations for all the tables are configured in a common configuration
file. There are currently two configurations that need to be run to create
the data summaries needed: full dataset and optimal (all quality control
checks passed) dataset.

A launcher bash script configures the SLURM job for each *sid-dck* data partition
and each table and logs to *log_dir*/*sid-dck*/*config_file*-*table*.*ext*, with
*ext* being *ok* or *failed* depending on job termination status.

.. code-block:: bash

   ./marine-user-guide/data_summaries_sd/monthly_grids_sd.slurm log_dir config_file source_deck_list

where:

  * log_dir: is created by the launcher script if does not exist
  * config_file:

    * Full dataset: monthly_grids_all.json (:ref:`monthly_grids_sd_all`)
    * Optimal dataset: monthly_grids_optimal.json (:ref:`monthly_grids_sd_optimal`)

  * source_deck_list: ascii file with a list of the *sid-dck* partitions to process


Monthly time series of selected quality indicators
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Monthly summaries of categorical counts of quality indicators in the header table
for every *sid-dck* data partition. These are additionally, split in counts by
main platform types (ships and buoys) and include the total number of reports.
They are stored in ascii pipe separated files.

The configuration file, :ref:`qi_counts_config_sd`, includes very limited
parameterization, with the platform type segregation pending to be \
parameterized.

A launcher bash script configures the SLURM job for each *sid-dck* data partition
and each quality indicator (currently only report_quality and duplicate_status)
and logs to *log_dir*/*sid-dck/*config_file*-*qi*.*ext*, with *ext* being *ok*
or *failed* depending on job termination status.

.. code-block:: bash

   ./marine-user-guide/data_summaries_sd/qi_counts_ts.slurm log_dir config_file source_deck_list

where:

  * log_dir: is created by the launcher script if does not exist
  * config_file: :ref:`qi_counts_config_sd`
  * source_deck_list: ascii file with a list of the *sid-dck* partitions to process


Monthly time series with source to C3S IO flow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Collection of monthly time series with the initial reports in source, selected,
invalid and delivered to C3S for every *sid-dck* data partition.

A launcher bash script configures the SLURM job for each *sid-dck* data partition
and logs to *log_dir*/*sid-dck/*config_file*.*ext*, with *ext* being *ok* or
*failed* depending on job termination status.

.. code-block:: bash

  ./marine-user-guide/data_summaries_sd/report_io.slurm log_dir config_file source_deck_list

where:

* log_dir: is created by the launcher script if does not exist
* config_file: :ref:`report_io_sd`
* source_deck_list: ascii file with a list of the *sid-dck* partitions to process

Figures
-------

ECV number of reports time series
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    * Data summary used: monthly grids (counts, header and observation tables)
    * Launcher script: configures the SLURM job for each *sid-dck* data partition \
      and logs to *log_dir*/*sid-dck/*config_file*.*ext*, with *ext* being *ok* \
      or *failed* depending on job termination status.

      .. code-block:: bash

        ./marine-user-guide/figures_sd/ecv_noreports_ts_grid_sd.slurm log_dir config_file source_deck_list

      where:

      * log_dir: is created by the launcher script if does not exist
      * config_file: :ref:`ecv_noreports_config_sd_all`, :ref:`ecv_noreports_config_sd_optimal`
      * source_deck_list: ascii file with a list of the *sid-dck* partitions to process


Observed parameters latitudinal time series
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    * Data summary used: monthly grids (counts, min, max, counts from observation tables). \
      All data and optimal dataset summaries.
    * Launcher script: configures the SLURM job for each *sid-dck* data partition \
      and each *mode* (all data and optimal dataset) logs to *log_dir*/*sid-dck/*config_file*-*mode*.*ext*, with *ext* being *ok* \
      or *failed* depending on job termination status.

      .. code-block:: bash

        ./marine-user-guide/figures_sd/param_lat_bands_ts.slurm log_dir config_file source_deck_list

      where:

      * log_dir: is created by the launcher script if does not exist
      * config_file: :ref:`param_lat_bands_ts`
      * source_deck_list: ascii file with a list of the *sid-dck* partitions to process


Duplicate status time series plot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Data summary used: duplicate_status quality indicators time series.
* Command:

  .. code-block:: bash

    ./marine-user-guide/figures_sd/nreports_dup_ts_sd.slurm log_dir config_file source_deck_list

  where:

  * log_dir: is created by the launcher script if does not exist
  * config_file: :ref:`nreports_dup_ts_sd`
  * source_deck_list: ascii file with a list of the *sid-dck* partitions to process


Report quality time series plot
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Data summary used: report_quality quality indicators time series.
* Command:

.. code-block:: bash

  ./marine-user-guide/figures_sd/nreports_qc_ts_sd.slurm log_dir config_file source_deck_list

where:

* log_dir: is created by the launcher script if does not exist
* config_file: :ref:`nreports_qc_ts_sd`
* source_deck_list: ascii file with a list of the *sid-dck* partitions to process


Monthly time series with source to C3S IO flow
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

* Data summary used: monthly time series with IO flow
* Command:

  .. code-block:: bash

    ./marine-user-guide/figures_sd/report_io.slurm log_dir config_file source_deck_list

where:

* log_dir: is created by the launcher script if does not exist
* config_file: :ref:`report_io_plot_sd`
* source_deck_list: ascii file with a list of the *sid-dck* partitions to process

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



.. _mon_grids_um:

Monthly grids
-------------

.. literalinclude:: ../config_files/monthly_grids.json


.. _qi_counts_um:

Quality indicators time series
------------------------------

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


.. _qi_counts_config_sd:

qi_counts
---------

.. literalinclude:: ../config_files_sd/qi_counts_ts.json


.. _report_io_sd:

Data IO flow
------------

.. literalinclude:: ../config_files_sd/report_io.json


.. _ecv_noreports_config_sd_all:

ecv_noreports_ts_grid plot (all data)
-------------------------------------

.. literalinclude:: ../config_files_sd/ecv_noreports_ts_grid_sd-all.json



.. _ecv_noreports_config_sd_optimal:

ecv_noreports_ts_grid plot (optimal dataset)
--------------------------------------------

.. literalinclude:: ../config_files_sd/ecv_noreports_ts_grid_sd-optimal.json



.. _param_lat_bands_ts:

Observed parameters latitudinal time series plot
------------------------------------------------

.. literalinclude:: ../config_files_sd/param_lat_bands_ts.json


.. _nreports_dup_ts_sd:

Duplicate status time series plot
---------------------------------

.. literalinclude:: ../config_files_sd/nreports_dup_ts_sd.json


.. _nreports_qc_ts_sd:

Report quality time series plot
-------------------------------

.. literalinclude:: ../config_files_sd/nreports_qc_ts_sd.json


.. _report_io_plot_sd:

Data IO flow plot
-----------------

.. literalinclude:: ../config_files_sd/report_io_plot.json
