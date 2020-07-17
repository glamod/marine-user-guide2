#!/bin/bash
# Runs the pyscript that links the release data files to the marine user guide
# directory
#
# Calling sequence:
# ./merge_release_data.slurm version script_config_file process_list

# ------------------------------------------------------------------------------
queue=short-serial
t=01:00:00
mem=100
om=truncate
# ------------------------------------------------------------------------------
source ../setpaths.sh
source ../setenv.sh

# Here make sure we are using fully expanded paths, as some may be passed to a config file
version=$1
script_config_file=$(readlink --canonicalize $2)
process_list=$(readlink --canonicalize $3)

pyscript="$mug_code_directory/init_version/merge_release_data.py $data_directory $mug_data_directory/$version $script_config_file"
log_dir=$mug_data_directory/$version/level2/log
if [ ! -d $log_dir ]
  echo "LOG dir does not exist: $log_dir"
  exit
fi


for sid_dck in $(awk '{print $1}' $process_list)
do
  log_dir_sd=$log_dir/$sid_dck
  if [ ! -d $log_dir_sd ]
  then
    echo "Source-deck LOG dir does not exist: $log_dir_sd"
    exit
  fi
  J=$sid_dck
  log_file=$log_dir_sd/merge_release_data.ok
  failed_file=$log_dir_sd/merge_release_data.failed
  jid=$(sbatch -J $J -o $log_file -e $log_file -p $queue -t $t --mem $mem --open-mode $om --wrap="python $pyscript $sid_dck")
  sbatch --dependency=afternotok:${jid##* } --kill-on-invalid-dep=yes -p $queue -t 00:05:00 --mem 1 --open-mode $om --wrap="mv $log_file $failed_file"
done
