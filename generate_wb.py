#!/usr/bin/env python
'''this script generates the annual average water balance maps for a SWAT+ hydrological model 
            However, can be adopted for any timestep.

Author  : albert nkwasa
Contact : albert.nkwasa@vub.be / nkwasa.albert@gmail.com
Date    : 2021.07.30

'''
import os
import pandas as pd
import geopandas as gpd
import gdal
import rasterio
from geocube.api.core import make_geocube

# #setting the working environment
working_dir = os.path.dirname(os.path.realpath(__file__))
os.chdir(working_dir)

wb_variables = ['et', 'surq_gen', 'wateryld', 'perc', 'latq', 'irr', 'precip']
scale = 'hru'
timestep = 'aa'


for k in wb_variables:
    if scale == 'hru':
        try:
            os.makedirs(f"{working_dir}/model_wb_maps/{k}_hru")
        except:
            pass

        os.chdir(f'{working_dir}/model_wb_maps/{k}_hru')
    # os.chdir('D:/phd_modelling/modelling_zones/models/{}/results_graphs/nutrients'.format(data_zone))

    # path to the result files
    wb_file = f'{working_dir}/Scenarios/Default/TxtInOut/hru_wb_aa.csv'
    name_header_wb = ['jday', 'mon', 'day', 'yr', 'unit', 'gis_id', 'name', 'precip', 'snofall', 'snomlt', 'surq_gen', 'latq',
                      'wateryld', 'perc', 'et', 'tloss', 'eplant', 'esoil', 'surq_cont', 'cn', 'sw_init', 'sw_final', 'sw_ave',
                      'sw_300', 'sno_init', 'sno_final', 'snopack', 'pet', 'qtile', 'irr', 'surq_runon', 'latq_runon', 'overbank',
                      'surq_cha', 'surq_res', 'surq_ls', 'latq_cha', 'latq_res', 'latq_ls']
    df_wb = pd.read_csv(wb_file, names=name_header_wb, skiprows=3)

    wb_par = df_wb[['gis_id', str(k)]]
    wb_par_dic = wb_par.set_index('gis_id').T.to_dict('list')

    # working with the HRU shapefile
    hru_shp_path = f'{working_dir}/Watershed/Shapes/hrus1.shp'
    gdf_wb = gpd.read_file(hru_shp_path)
    gdf_wb = gdf_wb.drop(['Channel', 'Landscape', 'Landuse',
                          'SlopeBand', 'Soil', '%Landscape', 'LINKNO'], axis=1)
    gdf_wb[str(k)] = 0

    for j in wb_par_dic:
        gdf_wb.loc[gdf_wb['HRUS'] == str(j), str(k)] = wb_par_dic[j]

    path_file_wb = str(k) + '_aa' + '.shp'
    gdf_wb.to_file(path_file_wb)
    # changing the projection and converting to a raster

    output_shp = 'test_{}.shp'.format(k)
    os.system('ogr2ogr {} -t_srs "EPSG:4326" {}'.format(output_shp, path_file_wb))
    output_raster = '{}_aa.tif'.format(k)
    cube = make_geocube(vector_data=output_shp, measurements=[
        str(k)], resolution=(0.0450450, -0.0450450), output_crs='epsg:4326', fill=-9999)  # resolution---->>can be adjusted to any resolution
    cube[str(k)].rio.to_raster(output_raster)
    os.remove('test_{}.shp'.format(k)), os.remove('test_{}.dbf'.format(
        k)), os.remove('test_{}.prj'.format(k)), os.remove('test_{}.shx'.format(k))


print('\t >finished')
