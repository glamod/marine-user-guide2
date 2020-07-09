#!/usr/bin/env python3
#
#  Needs to run with py env2: bwcause of pandas to_parquet (different to dask to parquet!)
# -*- coding: utf-8 -*-
"""CDM tables full record counts and mean ECV's values gridded time series.

This script creates gridded monthly time-series with summaries of the input CDM
table. The gridded summaries produced depend on the input CDM table:
    
    * header table: report counts.
    * observations tables: observations counts and mean observed value.

Input arguments to this script are:
    
    * sid_dck: source,deck to summarize
    * table: the CDM table to summarize
    * config_file: aggregation configuration file
    
Arguments from the config_file are:
    
    * dir_data: parent directory to the sid-dck subdirectories where the
    the CDM table files are stored. This directory
    is assumed to be partitioned in source-deck subdirectories with the table
    files within.
    * dir_out: parent directory to the sid-dck subdirectories where the
    the grid is writen to. 
    * id_out: tag to use in output file naming
    * start: first year, optional
    * stop: last year, optional
    * region: 'Global'
    * resolution: 'low'
    * filter_by_values (table specific): filter to apply to the data retrieved
    before inclusion in summaries.
    
"""
import os
import sys
sys.path.append('..')
import glob
import json
import logging

from dask import dataframe as dd
import dask.diagnostics as diag
import datashader as ds
import xarray as xr
import datetime

from data_summaries import properties
from common import query_cdm


LEN_DD = 100000 # DF LEN TO SWAP TO DASK-PARQUET AGGREGATION
# FUNCTIONS -------------------------------------------------------------------
def bounds(x_range, y_range):
    return dict(x_range=x_range, y_range=y_range)

def create_canvas(bbox,degree_factor):
    plot_width = int(abs(bbox[0][0]-bbox[0][1])*degree_factor)
    plot_height = int(abs(bbox[1][0]-bbox[1][1])*degree_factor)    
    return ds.Canvas(plot_width=plot_width, plot_height=plot_height, **bounds(*bbox))

# END FUNCTIONS ---------------------------------------------------------------
        

def main():    
    logging.basicConfig(format='%(levelname)s\t[%(asctime)s](%(filename)s)\t%(message)s',
                        level=logging.INFO,datefmt='%Y%m%d %H:%M:%S',filename=None)
    
    sid_dck = sys.argv[1]
    table = sys.argv[2]
    config_file = sys.argv[3]
    
    with open(config_file,'r') as fO:
        config = json.load(fO)
        
    dir_in = os.path.join(config['dir_data'],sid_dck)
    dir_out = os.path.join(config['dir_out'],sid_dck)
    
    # KWARGS FOR CDM FILE QUERY----------------------------------------------------
    kwargs = {}
    kwargs['dir_data'] = config['dir_data']
    kwargs['cdm_id'] = '*'
    if table == 'header':
        kwargs['columns'] = ['latitude','longitude']
        count_param = 'latitude'
    else:
        kwargs['columns'] = ['latitude','longitude','observation_value']
        count_param = 'observation_value'
        
    kwargs['filter_by_values'] = config[table]['filter_by_values']
    for kv in list(kwargs.get('filter_by_values').items()):
                        kwargs['filter_by_values'][(kv[0].split('.')[0],kv[0].split('.')[1])] = kwargs['filter_by_values'].pop(kv[0])
    
    # CREATE CANVAS FROM PARAMS ---------------------------------------------------
    region = config['region']
    resolution = config['resolution']
    canvas = create_canvas(properties.REGIONS.get(region),properties.DEGREE_FACTOR_RESOLUTION.get(resolution))
    
    # CREATE THE MONTHLY STATS ON THE DF PARTITIONS -------------------------------
    nreports_list = []
    mean_list = []
    start = datetime.datetime(config.get('start',1600),1,1)
    stop = datetime.datetime(config.get('stop',2100),12,1)
    files_list = glob.glob(os.path.join(dir_in,'-'.join([table,'????','??',kwargs['cdm_id']]) + '.psv' ))
    if len(files_list) == 0:
        if table == 'header':
            logging.error('NO DATA FILES FOR HEADER TABLE IN DIR {}'.format(dir_in))
            sys.exit(1)
        else:
            logging.warning('NO DATA FILES FOR TABLE {0} IN DIR {1}'.format(table,dir_in))
            sys.exit(0)
            
    for file in files_list:
        yyyy,mm = os.path.basename(file).split(table)[1].split('-')[0:2]
        dt = datetime.datetime(int(yyyy),int(mm),1)
        if dt < start or dt > stop:
            logging.info('File {} out of requested period'.format(file))
            continue
        parq_path = os.path.join(dir_out,'-'.join([yyyy,mm,table,'.data.parq.tmp']))

        cdm_table = query_cdm.query_monthly_table(sid_dck, table, dt.year, dt.month, **kwargs)
        cdm_table.dropna(inplace = True)
    
        len_table = len(cdm_table)
        logging.info('DF LEN: {}'.format(len(cdm_table)))
        # SAVE TO PARQUET AND READ DF BACK FROM THAT TO ENHANCE PERFORMANCE
        # CHECK HERE NUMBER OF RECORDS AFTER AND BEFORE SAVING, ETC....
        if len_table > LEN_DD:
            logging.info('Time partition to parquet')
            with diag.ProgressBar(), diag.Profiler() as prof, diag.ResourceProfiler(0.5) as rprof:
                cdm_table.to_parquet(parq_path, engine = 'fastparquet', compression = 'gzip',append = False)  
            del cdm_table
            
            logging.info('Time parition from parquet')
            cdm_table = dd.read_parquet(parq_path)
        logging.info('Canvas aggregation')
        nreports_arr = canvas.points(cdm_table,'longitude','latitude',ds.count(count_param)).assign_coords(time=dt).rename('counts')
        nreports_list.append(nreports_arr)
        if table != 'header':
            mean_arr = canvas.points(cdm_table,'longitude','latitude',ds.mean('observation_value')).assign_coords(time=dt).rename('mean')
            mean_list.append(mean_arr)
    
    #    Now this seems different with pandas to parquet, is it the engine choice?
    #    shutil.rm(parq_path)
        if len_table > LEN_DD:
            os.remove(parq_path)
    
        
    nreports_agg = xr.concat(nreports_list,dim = 'time')
    if table != 'header':
        mean_agg = xr.concat(mean_list,dim = 'time')
    
    dims_mean = ['latitude','longitude','mean']
    encodings_mean = { k:v for k,v in properties.NC_ENCODINGS.items() if k in dims_mean } 
    dims_counts = ['latitude','longitude','counts']
    encodings_counts = { k:v for k,v in properties.NC_ENCODINGS.items() if k in dims_counts } 
    
    out_file = os.path.join(dir_out,'-'.join([table,'no_reports_grid_ts',config['id_out'] + '.nc']))
    nreports_agg.encoding =  encodings_counts
    nreports_agg.to_netcdf(out_file,encoding = encodings_counts,mode='w')
    if table != 'header':
        out_file = os.path.join(dir_out,'-'.join([table,'mean_grid_ts',config['id_out'] + '.nc']))
        mean_agg.encoding =  encodings_mean
        mean_agg.to_netcdf(out_file,encoding = encodings_mean,mode='w')

if __name__ == "__main__":
    main()
