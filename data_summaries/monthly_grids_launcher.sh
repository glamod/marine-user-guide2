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
script_config_file=$2

pyscript=$mug_code_directory/data_summaries/monthly_grids.py
log_dir=$data_directory"/marine-user-guide/"$mug_version"/log/monthly_grids"
if [ ! -d $log_dir ]; then mkdir -p $log_dir; fi
echo "LOG DIR IS $log_dir"

job_time_hhmm=16:00
job_memo_mbi=5000
for table in header observations-sst observations-at observations-dpt observations-wd observations-ws observations-slp
do

   jobid=$(nk_jobid bsub -J $table -oo $log_dir/$table".log" -eo $log_dir/$table".log" -q short-serial -W $job_time_hhmm -M $job_memo_mbi -R "rusage[mem=$job_memo_mbi]" python $pyscript $table $script_config_file )
done
