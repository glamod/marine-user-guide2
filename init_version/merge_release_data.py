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

# FUNCTIONS -------------------------------------------------------------------
class script_setup:
    def __init__(self, inargs):
        self.data_path = inargs[1]
        self.mug_version = inargs[2]
        self.mug_config_file = inargs[3]
        self.sd = inargs[4]

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
    
    sd_release_list = list(mug_config[params.sd].get('year_init').keys())
    sd_dataset_dict = { rel:dataset_dict[rel] for rel in sd_release_list }
    
    sd_level2_paths = { k:os.path.join(params.data_path,k,v,'level2',params.sd,'*.psv') for k,v in sd_dataset_dict.items() }
    
    # Make a clean level2 version in user manual
    sd_level2_path_um = os.path.join(params.data_path,'marine-user-guide',params.mug_version,params.sd)
    if os.path.isdir(sd_level2_path_um):
        shutil.rmtree(sd_level2_path_um)
        
    os.makedirs(sd_level2_path_um, exist_ok=True)
    # Now link from all releases there
    for release in sd_release_list:
        call(' '.join(['cp -s',sd_level2_paths.get(release),sd_level2_path_um]),shell=True)    
    
    sys.exit(0)

if __name__ == "__main__":
    main()