#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 20 11:43:22 2018

@author: iregon
"""
import os
import sys
import json
import logging
import numpy as np
import matplotlib.pyplot as plt
#plt.switch_backend('agg')
import datetime
import itertools
import xarray as xr


from figures import var_properties

logging.getLogger('plt').setLevel(logging.INFO)
logging.getLogger('mpl').setLevel(logging.INFO)

# PARAMS ----------------------------------------------------------------------
# Set plotting defaults
plt.rc('legend',**{'fontsize':12})        # controls default text sizes
plt.rc('axes', titlesize=12)     # fontsize of the axes title
plt.rc('axes', labelsize=12)    # fontsize of the x and y labels
plt.rc('xtick', labelsize=10)    # fontsize of the tick labels
plt.rc('ytick', labelsize=10)    # fontsize of the tick labels
plt.rc('figure', titlesize=14)  # fontsize of the figure title
# END PARAMS ------------------------------------------------------------------

def flip(items, ncol):
    return itertools.chain(*[items[i::ncol] for i in range(ncol)])

if __name__ == "__main__":

    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

    sid_dck = sys.argv[1]
    config_file = sys.argv[2]
    
    with open(config_file) as cf:
        config = json.load(cf)
    
    dir_data = os.path.join(config['dir_data'],sid_dck)
    dir_out = os.path.join(config['dir_out'],sid_dck)
    file_in_id = config['file_in_id']
    file_out = config['file_out']
     
    filtered = False
    log_scale_cells = False
    log_scale_reports = True
    n_reports_color = 'FireBrick'
    n_cells_color = 'Black'
    bbox_props = dict(boxstyle="round", fc="w", ec="0.5", alpha=0.9)
        
    observation_tables = ['observations-at','observations-sst','observations-dpt',
                          'observations-slp','observations-ws','observations-wd']   
    table = 'header'
    file_pattern = table + file_in_id + '.nc'
    hdr_dataset = xr.open_dataset(os.path.join(dir_data,file_pattern))
    # This is because at some point t I found them unsorted (1947-02 in 1945...)
    #hdr_dataset  = hdr_dataset.reindex(time=sorted(hdr_dataset.time.values))
    header_n_cells = hdr_dataset['counts'].where(hdr_dataset['counts'] > 0).count(dim=['longitude','latitude'])
    header_n_reports = hdr_dataset['counts'].sum(dim=['longitude','latitude'])
    header_n_reports_max = header_n_reports.max()
    if filtered:
        header_n_cells = header_n_cells.rolling(time=12, center=True).mean()
        header_n_reports = header_n_reports.rolling(time=12, center=True).mean()
        
    header_n_reports_max = header_n_reports.max()    
    
    f, ax = plt.subplots(3, 2, figsize=(10,10),sharex=True,sharey=True)# 
    ax2 = ax.copy()
    for i,table in enumerate(observation_tables):
        logging.info('Table: {}'.format(table))
        obs_avail = True
        var = table.split('-')[1]
        title = var_properties.var_properties['long_name_upper'][var]
        c = 0 if i%2 == 0 else 1
        r = int(i/2)
        file_pattern = table + file_in_id + '.nc'
        if not os.path.isfile(os.path.join(dir_data,file_pattern)):
            obs_avail = False
            
        if obs_avail:
            dataset = xr.open_dataset(os.path.join(dir_data,file_pattern))
            #dataset  = dataset.reindex(time=sorted(dataset.time.values))
            n_cells = dataset['counts'].where(dataset['counts'] > 0).count(dim=['longitude','latitude'])
            n_reports = dataset['counts'].sum(dim=['longitude','latitude'])
            if filtered:
                logging.info('...filtering time series')
                n_cells = n_cells.rolling(time=12, center=True).mean()
                n_reports = n_reports.rolling(time=12, center=True).mean()
           
        logging.info('...plotting time series')
        header_n_reports.plot(ax=ax[r,c],color=n_reports_color,zorder = 1 ,label='#reports',linewidth=5,alpha=0.15)
        if obs_avail:
            n_reports.plot(ax=ax[r,c],color=n_reports_color,zorder = 3 ,label='#obs parameter')
        ax2[r,c] = ax[r,c].twinx()
        header_n_cells.plot(ax=ax2[r,c],color=n_cells_color,linewidth=5,alpha=0.15,zorder = 2,label='#1x1 cells reports')
        if obs_avail:
            n_cells.plot(ax=ax2[r,c],color=n_cells_color,zorder = 4, label='#1x1 cells parameter')
        if not obs_avail:
            ax[r,c].text(0.5, 0.5,'No data',horizontalalignment='center',
                          verticalalignment='center',transform = ax[r,c].transAxes,size=20,bbox=bbox_props)
        
        ax2[r,c].set_ylabel('#1x1 cells', color=n_cells_color)
        ax2[r,c].tick_params(axis='y', colors=n_cells_color)
        ax[r,c].set_ylabel('#Observations', color=n_reports_color)
        ax[r,c].tick_params(axis='y', colors=n_reports_color)
        ax[r,c].set_title(title, color='k')
        
        if log_scale_reports:
            ax[r,c].set_yscale('log')
        if log_scale_cells:
            ax2[r,c].set_yscale('log')
        
        
        ax[r,c].tick_params(axis='x',labelbottom=True,labelrotation=0)
        ax[r,c].tick_params(axis='y',labelleft=True,labelrotation=0)
        ax2[r,c].ticklabel_format(axis='y', style='sci',scilimits=(-3,4))
        
    lines, labels = ax[r,c].get_legend_handles_labels()
    lines2, labels2 = ax2[r,c].get_legend_handles_labels()    
    lines = [lines[1]] + [lines2[1]] + [lines[0]] + [lines2[0]]
    labels = [labels[1]] + [labels2[1]] + [labels[0]] + [labels2[0]]
    f.legend(flip(lines,4),flip(labels,4),loc='lower center', ncol=4)
    f.tight_layout(rect=[0, 0.03, 1, 0.95])
    
    fig_path = os.path.join(dir_out,file_out)
    plt.savefig(fig_path,bbox_inches='tight',dpi = 300)
    plt.close(f)
