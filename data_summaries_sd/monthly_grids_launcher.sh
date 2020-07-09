#!/bin/bash
# Runs the pyscript that aggregates the monthly partitions in a time series
# of monthly grids on every source-deck and table
#
# Calling sequence:
# ./monthly_grids_launcher.sh log_dir script_config_file process_list

# ------------------------------------------------------------------------------
function sbatch_run {
  #SBATCH -p short-serial
  #SBATCH -t 02:00:00
  #SBATCH --mem 5000
  #SBATCH --open-mode truncate
  python $pyscript $1 $2 $script_config_file
}
# ------------------------------------------------------------------------------
source ../setpaths.sh
source ../setenv.sh

# Here make sure we are using fully expanded paths, as some may be passed to a config file
log_dir=$(readlink --canonicalize  $1)
script_config_file=$(readlink --canonicalize  $2)
process_list=$(readlink --canonicalize  $3)

pyscript=$mug_code_directory/data_summaries_sd/monthly_grids.py
if [ ! -d $log_dir ]; then mkdir -p $log_dir; fi
echo "LOG DIR IS $log_dir"

for sid_dck in $(awk '{print $1}' $process_list)
  log_dir_sd=$log_dir/$sid_dck
  for table in header observations-sst observations-at observations-dpt observations-wd observations-ws observations-slp
  do
    jid1=$(sbatch -J $table"_"$sid_dck -o $log_dir_sd/$table".log" -e $log_dir_sd/$table".log" --wrap="$(sbatch_run $sid_dck $table)")
  done
done
