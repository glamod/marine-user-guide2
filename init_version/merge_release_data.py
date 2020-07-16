#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Marine User Guide data merger

This script creates a view of a source-deck data in a Marine User Guide version
by linking the level2 files in the data releases directories to a common
directory in the User Guide directory in the data space.

Input arguments to this script are:
    
    * data_path: path to the general marine data directory
    * mug_version: tag for Marine User Guide version (ie.'v4')
    * mug_config_file: path to the Marine User Guide data configuration file
    * sd: source-deck id (sss-ddd)
"""
import sys
import os
import json
import logging
import shutil
from subprocess import call
from imp import reload
reload(logging)  # This is to override potential previous config of logging

# PARAMS ----------------------------------------------------------------------
LEVELS = ['level1a','level1c','level2']
level_subdirs = {}
level_subdirs['level1a'] = ['quicklooks']
level_subdirs['level1c'] = ['quicklooks']
level_subdirs['level2'] = ['log','reports']

# FUNCTIONS -------------------------------------------------------------------
class script_setup:
    def __init__(self, inargs):
        self.data_path = inargs[1]
        self.mug_path = inargs[2]
        self.mug_version = inargs[3]
        self.mug_config_file = inargs[4]
        
def create_subdir(lpath,subdir_list):
    subdir_list = [subdir_list] if isinstance(subdir_list,str) else subdir_list
    for subdir in subdir_list:
        subdir_dir = os.path.join(lpath,subdir)
        if not os.path.isdir(subdir_dir):
            os.mkdir(subdir_dir,0o774)
# MAIN ------------------------------------------------------------------------
def main():
    # Process input and set up some things and make sure we can do something---
    logging.basicConfig(format='%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s',
                        level=logging.INFO,datefmt='%Y%m%d %H:%M:%S',filename=None)
    if len(sys.argv)>1:
        logging.info('Reading command line arguments')
        args = sys.argv
    else:
        logging.error('Need arguments to run!')
        sys.exit(1)
    
    params = script_setup(args)
    
    
    with open(params.mug_config_file,'r') as fO:
        mug_config = json.load(fO)
    
    dataset_dict = mug_config.get('dataset_names')
    
    sid_list = list(mug_config['sid_dck'].keys())
    
    # Create the directory structure

    mug_version_path = os.path.join(params.mug_path,params.mug_version)
    logging.info('Creating dir {}'.path(mug_version_path))
    create_subdir(params.mug_path,params.mug_version)
    
    logging.info('Adding levels: {}'.path(','.join(LEVELS)))
    create_subdir(mug_version_path,LEVELS)
    
    for level in LEVELS:
        logging.info('Level {}, adding source-deck directories and subdirectories'.path(level))
        level_subdir = os.path.join(mug_version_path,level)
        create_subdir(level_subdir,sid_list)
        create_subdir(level_subdir,level_subdirs[level])

        for sublevel in level_subdirs.get(level):
            create_subdir(os.path.join(level_subdir,sublevel),sid_list)
    
    # Now link the data files from the release directories
    for sd in sid_list:
        
        sd_release_list = list(mug_config[sd].get('year_init').keys())
        sd_dataset_dict = { rel:dataset_dict[rel] for rel in sd_release_list }
         
        # merge level2 data
        sd_paths = { k:os.path.join(params.data_path,k,v,'level2',sd,'*.psv') for k,v in sd_dataset_dict.items() }
        sd_path_um = os.path.join(params.data_path,'marine-user-guide',params.mug_version,'level2',sd)
        for release in sd_release_list:
            call(' '.join(['cp -s',sd_paths.get(release),sd_path_um]),shell=True)  
            
        # merge level1a json quicklooks 
        sd_paths = { k:os.path.join(params.data_path,k,v,'level1a','quicklooks',sd,'*.json') for k,v in sd_dataset_dict.items() }
        sd_path_um = os.path.join(params.data_path,'marine-user-guide',params.mug_version,'level1a','quicklooks',sd)
        for release in sd_release_list:
            call(' '.join(['cp -s',sd_paths.get(release),sd_path_um]),shell=True)  
            
        # merge level1c json quicklooks 
        sd_paths = { k:os.path.join(params.data_path,k,v,'level1c','quicklooks',sd,'*.json') for k,v in sd_dataset_dict.items() }
        sd_path_um = os.path.join(params.data_path,'marine-user-guide',params.mug_version,'level1c','quicklooks',sd)
        for release in sd_release_list:
            call(' '.join(['cp -s',sd_paths.get(release),sd_path_um]),shell=True)  
    
    sys.exit(0)

if __name__ == "__main__":
    main()