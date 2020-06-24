#!/bin/bash

#. FUNCTIONS -------------------------------------------------------------------
# Get JOB
function nk_jobid {
    output=$($*)
    echo $output | head -n1 | cut -d'<' -f2 | cut -d'>' -f1
}
# ------------------------------------------------------------------------------
source ../setpaths.sh
source ../setenv.sh

# Here make sure we are using fully expanded paths, as some may be passed to a config file
mug_version=$1
config_file=$(readlink --canonicalize  $2)
process_list_file=$(readlink --canonicalize  $3)

mug_version_dir=$data_directory"/marine-user-guide/"$mug_version
if [ ! -d $mug_version_dir ]
then
  mkdir -p $mug_version_dir
  mkdir $data_directory"/marine-user-guide/"$mug_version"/log"
  mkdir $data_directory"/marine-user-guide/"$mug_version"/quicklooks"
fi

pyscript="$mug_code_directory/init_version/merge_release_data.py $data_directory $mug_version $config_file"
pyhdlr=$mug_code_directory/common/process_output_hdlr.py
run_id=$(basename $0 .sh)

log_dir=$data_directory"/marine-user-guide/"$mug_version"/log/merge_release_data"
if [ ! -d $log_dir ]; then mkdir $log_dir; fi

echo "LOG DIR IS $log_dir"

job_time_hhmm=00:30
job_memo_mbi=500

for sid_dck in $(awk '{print $1}' $process_list_file)
do
   sid_dck_log_dir=$log_dir/$sid_dck
   if [ ! -d $sid_dck_log_dir ]; then mkdir -p $sid_dck_log_dir; fi

   echo $sid_dck
   jobid=$(nk_jobid bsub -J $sid_dck -oo $sid_dck_log_dir/$run_id".o" -eo $sid_dck_log_dir/$run_id".o" -q short-serial -W $job_time_hhmm -M $job_memo_mbi -R "rusage[mem=$job_memo_mbi]" python $pyscript $sid_dck)

   bsub -J OK -w "done($jobid)" -oo $sid_dck_log_dir/$run_id".ho" -eo $sid_dck_log_dir/$run_id".ho" -q short-serial -W 00:01 -M 10 -R "rusage[mem=10]" \
   python $pyhdlr $sid_dck_log_dir/$run_id".o" 0

   bsub -J ER -w "exit($jobid)" -oo $sid_dck_log_dir/$run_id".ho" -eo $sid_dck_log_dir/$run_id".ho" -q short-serial -W 00:01 -M 10 -R "rusage[mem=10]" \
   python $pyhdlr $sid_dck_log_dir/$run_id".o" 1
done
