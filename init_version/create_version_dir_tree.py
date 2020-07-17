#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Marine User Guide data merger

This script creates a the directory tree to hold the data links for a marine 
user guide version.

Input arguments to this script are:

    * mug_version: tag for Marine User Guide version (ie.'v4')
    * mug_config_file: path to the Marine User Guide data configuration file
    * sd: source-deck id (sss-ddd)
"""

import sys
import os
import json
import logging
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
        self.mug_path = inargs[1]
        self.mug_version = inargs[2]
        self.mug_config_file = inargs[3]
        
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
    
    sid_list = list(mug_config['sid_dck'].keys())
    
    # Create the directory structure
    mug_version_path = os.path.join(params.mug_path,params.mug_version)
    logging.info('Creating dir {}'.format(mug_version_path))
    create_subdir(params.mug_path,params.mug_version)
    
    logging.info('Adding levels: {}'.format(','.join(LEVELS)))
    create_subdir(mug_version_path,LEVELS)
    
    for level in LEVELS:
        logging.info('Level {}, adding source-deck directories and subdirectories'.format(level))
        level_subdir = os.path.join(mug_version_path,level)
        create_subdir(level_subdir,sid_list)
        create_subdir(level_subdir,level_subdirs[level])

        for sublevel in level_subdirs.get(level):
            create_subdir(os.path.join(level_subdir,sublevel),sid_list)

if __name__ == "__main__":
    main()
