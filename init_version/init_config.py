# -*- coding: utf-8 -*-
""" Marine User Guide configuration setup

This script creates the data configuration of the Marine User Guide by
merging the level2 configuration files of the marine data releases that 
together are a snapshot of the marine data available in the CDS.

The user is prompted to input the following information for every data release:
    
    * Release name: directory name for the release in the marine file system
    * Dataset name: directory of the original dataset within the release
    * Release level2 file: the path to the release level2 file


On merging releases, this script will:
    
    * Raise a warning if the exclude tag for a source-deck differs 
    between data releases
    * Ignore a source-deck if it has been excluded from delivery in the data 
    releases
    * Compute the merged initial and final year.
    
This script outputs a file with the information merged to the path 
indicated by the user.
    
This file can also be imported as a module and contains the following
functions:
    * get_releases - prompts the user to give release information and returns
    it
    * main - the main function of the script
"""

import sys
import json

def get_releases():
    """Gets from user release information


    Returns
    -------
    list
        a list of strings with the release names
    dict
        a dictionary with the release names as keys and the corresponding 
        dataset names as values
    dict
        a dictionary with the release names as keys and the paths to the 
        corresponding level2 configuration files as values
    """
    
    release_name_list = []
    dataset_name_dict = {}
    release_level2_dict = {}
    while True:
        release_name = input('Input name for release: ')
        if release_name == '':
            break
        release_name_list.append(release_name)
        dataset_name  = input('Input dataset name: ')
        dataset_name_dict[release_name] = dataset_name
        release_level2  = input('Input path to level2 configuration file: ')
        release_level2_dict[release_name] = release_level2

    print('Release and dataset names and level2 configuration paths are:')
    print(release_name_list)
    print(dataset_name_dict)
    print(release_level2_dict)
    i = input('Is this correct? Continue? (y/n)')
    if i == 'y':
        return release_name_list, dataset_name_dict, release_level2_dict
    else:
        return sys.exit(1)


def main():  
    # GET INPUT ARGUMENTS
    release_names,dataset_names_dict,release_level2_dict = get_releases()
    
    # GET OUTPUT PATH
    out_path = input('Input filename and path for output: ')
    
    merge_dicts = {}
    for release_name in release_names:
        level2_path = release_level2_dict[release_name]
        with open(level2_path,'r') as f0:
            merge_dicts[release_name] = json.load(f0)
    
    merged_dict = {"release_names" : release_names,"dataset_names" : dataset_names_dict}
    global_init = min([ int(v.get('year_init')) for v in merge_dicts.values() ])
    global_end = max([ int(v.get('year_end')) for v in merge_dicts.values() ])
    
    merged_dict['year_init'] = global_init
    merged_dict['year_end'] = global_end
    
    params_exclude = []
    for k,v in merge_dicts.items():
        params_exclude.extend(v.get('params_exclude',[]))
    params_exclude = list(set(params_exclude))
    merged_dict['params_exclude'] =  params_exclude
    
    for k,v in merge_dicts.items():
        v.pop('year_init',None)
        v.pop('year_end',None)
        v.pop('params_exclude',None)
    
    global_sd_list = []
    for k,v in merge_dicts.items():
        global_sd_list.extend(v.keys())   
        
    global_sd = list(set(global_sd_list))
    
    merged_dict['sid_dck'] = {}
    
    for sd in global_sd:
        merged_dict['sid_dck'][sd] = {}
        release_in = [ x for x in release_names if merge_dicts[x].get(sd) ]
        merged_dict['sid_dck'][sd]['year_init'] = { release:int(merge_dicts[release][sd]['year_init']) for release in release_in }
        merged_dict['sid_dck'][sd]['year_end'] = { release:int(merge_dicts[release][sd]['year_end']) for release in release_in }
        merged_dict['sid_dck'][sd]['exclude'] = { release:merge_dicts[release][sd]['exclude'] for release in release_in }
        merged_dict['sid_dck'][sd]['params_exclude'] = []
        for release in release_in:
            merged_dict['sid_dck'][sd]['params_exclude'].extend(merge_dicts[release][sd].get('params_exclude',[]))    
        merged_dict['sid_dck'][sd]['params_exclude'] = list(set(merged_dict['sid_dck'][sd]['params_exclude']))
        if len(list(set(merged_dict['sid_dck'][sd]['exclude'].values()))) > 1:
            print('WARNING, EXCLUDE OPTION DIFFERS BETWEEN DATA RELEASES SID-DCK {}'.format(sd))
            print('SOLVE MANUALLY ON OUTPUT FILE')
        else:
            merged_dict['sid_dck'][sd]['exclude'] = list(merged_dict['sid_dck'][sd]['exclude'].values())[0]
        if merged_dict['sid_dck'][sd]['exclude']:
            print('Removing from config file excluded source-deck excluded from data release(s): {}'.format(sd))
            merged_dict.pop(sd)
      
    with open(out_path,'w') as fO:
        json.dump(merged_dict,fO,indent=4)

    
if __name__ == "__main__":
    main()