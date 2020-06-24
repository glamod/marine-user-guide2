data_directory=/group_workspaces/jasmin2/glamod_marine/data
code_directory=/gws/smf/j04/c3s311a_lot2/code/marine_code

mug_code_directory=$code_directory/marine-user-guide

echo 'Data directory is '$data_directory
echo 'User guide code directory is '$mug_code_directory

# Create the scratch directory for the user
scratch_directory=/work/scratch-nopw/$(whoami)/user-manual
if [ ! -d $scratch_directory ]
then
  echo "Creating user $(whoami) scratch directory $scratch_directory"
  mkdir $scratch_directory
else
  echo "Scratch directory is $scratch_directory"
fi
