#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Marine User Guide data merger

This script creates a view of a source-deck data in a Marine User Guide version
by linking the level2 files in the data releases directories to a common
directory in the User Guide directory in the data space.

Input arguments to this script are:
    
    * sd: source-deck id (sss-ddd)
    * data_path: path to the general marine data directory
    * mug_path: path to the data directory of the marine user guide version
    * mug_config_file: path to the Marine User Guide data configuration file
    
"""
import sys
import os
import json
import logging
from subprocess import call
from imp import reload
reload(logging)  # This is to override potential previous config of logging


# FUNCTIONS -------------------------------------------------------------------
class script_setup:
    def __init__(self, inargs):
        self.data_path = inargs[1]
        self.mug_path = inargs[2]
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

    sd_release_list = list(mug_config['sid_dck'][params.sd].get('year_init').keys())
    sd_dataset_dict = { rel:dataset_dict[rel] for rel in sd_release_list }
     
    # merge level2 data
    logging.info('Linking level2 files')
    sd_paths = { k:os.path.join(params.data_path,k,v,'level2',params.sd,'*.psv') for k,v in sd_dataset_dict.items() }
    sd_path_um = os.path.join(params.data_path,'marine-user-guide',params.mug_version,'level2',params.sd)
    for release in sd_release_list:
        logging.info('...release {}'.format(release))
        call(' '.join(['cp -s',sd_paths.get(release),sd_path_um]),shell=True)  
        
    # merge level1a json quicklooks 
    logging.info('Linking level1a ql files')
    sd_paths = { k:os.path.join(params.data_path,k,v,'level1a','quicklooks',params.sd,'*.json') for k,v in sd_dataset_dict.items() }
    sd_path_um = os.path.join(params.data_path,'marine-user-guide',params.mug_version,'level1a','quicklooks',params.sd)
    for release in sd_release_list:
        logging.info('...release {}'.format(release))
        call(' '.join(['cp -s',sd_paths.get(release),sd_path_um]),shell=True)  
        
    # merge level1c json quicklooks 
    logging.info('Linking level1c ql files')
    sd_paths = { k:os.path.join(params.data_path,k,v,'level1c','quicklooks',params.sd,'*.json') for k,v in sd_dataset_dict.items() }
    sd_path_um = os.path.join(params.data_path,'marine-user-guide',params.mug_version,'level1c','quicklooks',params.sd)
    for release in sd_release_list:
        logging.info('...release {}'.format(release))
        call(' '.join(['cp -s',sd_paths.get(release),sd_path_um]),shell=True)  
    
    sys.exit(0)

if __name__ == "__main__":
    main()
