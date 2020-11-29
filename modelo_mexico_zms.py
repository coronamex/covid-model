#!/usr/bin/env python
# Copyright (C) 2020 Sur Herrera Paredes

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import pymc3 as pm
import pandas as pd
import numpy as np
import arviz as az
from covid.models.generative import GenerativeModel
from covid.data import summarize_inference_data
from datetime import date
from covid.data import get_and_process_covidtracking_data, summarize_inference_data
import argparse

def process_arguments():
    # Read arguments
    parser_format = argparse.ArgumentDefaultsHelpFormatter
    parser = argparse.ArgumentParser(formatter_class=parser_format)
    required = parser.add_argument_group("Required arguments")

    # Define description
    parser.description = ("Correr datos de México en modelo de "
                          "rt.live.")

    # Define required arguments
    required.add_argument("--base_de_datos",
                          help=("Base de datos más reciente de la SSA."),
                          required=True, type=str)
    required.add_argument("--lut_zms",
                          help=("Tabla que asocia municipios con zonas "
                                "metropolitanas."),
                          required=True, type=str)
    required.add_argument("--region",
                          help=("Clave CVE de la zona metropolitana a "
                                "analizar."),
                          required=True, type=str)

    # Read arguments
    print("Reading arguments")
    args = parser.parse_args()

    # Processing goes here if needed

    return args

# args_lut_zms = "/home/sur/micropopgen/src/coronamex/covid-model/selected_zms.csv"
# args_base_de_datos = "/home/sur/micropopgen/src/coronamex/datos/datos_abiertos/base_de_datos.csv.gz"
# args_region = '01.01'

if __name__ == "__main__":
    args = process_arguments()

    # Leer mapa municipios zm
    lut_zms = pd.read_csv(args.lut_zms,
                              header=0, index_col=None,
                              dtype = {'CVE_ZM': str,
                                       'CVE_ENT': str,
                                       'CVE_MUN': str})
    lut_zms = lut_zms.drop(columns=['NOM_MUN', 'NOM_ENT'])
    lut_zms.index = lut_zms['CVE_MUN']

    # Leer base de datos
    Dat = pd.read_csv(args.base_de_datos,
                      compression='gzip', sep = ",",
                      encoding='iso-8859-1',
                      dtype = {'ENTIDAD_RES': str,
                               'MUNICIPIO_RES': str})

    # # Contar pruebas por fecha por entidad
    # Dat = Dat[Dat.RESULTADO != 3][['FECHA_SINTOMAS',
    #                                'ENTIDAD_RES',
    #                                'MUNICIPIO_RES',
    #                                'ID_REGISTRO',
    #                                'RESULTADO']]

    # Seleccionar datos con resultado
    Dat = Dat[Dat.CLASIFICACION_FINAL.isin([1, 2, 3, 7, 8])][['FECHA_SINTOMAS',
                                       'ENTIDAD_RES',
                                       'MUNICIPIO_RES',
                                       'ID_REGISTRO',
                                       'CLASIFICACION_FINAL']]

    # Determinar positivos y negativos, usando pruebas PCR,
    # asociación, dictaminación y pruebas de antígenos.
    ii = Dat.CLASIFICACION_FINAL.isin([1,2,3,8])
    Dat.loc[ii, 'CLASIFICACION_FINAL'] = 1
    ii = Dat.CLASIFICACION_FINAL.isin([7])
    Dat.loc[ii, 'CLASIFICACION_FINAL'] = 2

    # # Primero seleccionar municipios en ZMs de interés
    # Dat['CVE_MUN'] = Dat.ENTIDAD_RES + Dat.MUNICIPIO_RES
    # Dat = Dat.drop(columns=['ENTIDAD_RES', 'MUNICIPIO_RES'])
    # ii = Dat['CVE_MUN'].isin(lut_zms.CVE_MUN)
    # Dat = Dat.loc[ii,].reset_index()

    # # Mapear casos a ZMs de interés
    # cve_zms = lut_zms.CVE_ZM[Dat.CVE_MUN].reset_index().CVE_ZM
    # Dat['CVE_ZM'] = cve_zms

    # # Limpiar
    # Dat = Dat.drop(columns = ['index', 'CVE_MUN'])

    # # Contar
    # Dat = Dat.groupby(['FECHA_SINTOMAS',
    #                    'CVE_ZM',
    #                    'RESULTADO']).count()

    # # Obtener datos de región de interés
    # Dat_ent = Dat.loc[(slice(None), args.region), :]
    # Dat_ent = Dat_ent.droplevel('CVE_ZM')
    # Dat_ent.reset_index(inplace=True)
    # Dat_ent = Dat_ent.pivot(index='FECHA_SINTOMAS',
    #                         columns='RESULTADO',
    #                         values='ID_REGISTRO')
    # Dat_ent.reset_index(inplace=True)
    # Dat_ent.fillna(0, inplace=True)
    # Dat_ent['total'] = Dat_ent[1] + Dat_ent[2]
    # Dat_ent = Dat_ent.rename(columns={'FECHA_SINTOMAS': 'date',
    #                                   1: 'positive',
    #                                   2: 'negative'}).drop(columns ='negative')
    # Dat_ent['date'] = pd.to_datetime(Dat_ent.date)
    # Dat_ent.set_index('date', inplace=True)

    # Primero seleccionar municipios en ZMs de interés
    Dat['CVE_MUN'] = Dat.ENTIDAD_RES + Dat.MUNICIPIO_RES
    Dat = Dat.drop(columns=['ENTIDAD_RES', 'MUNICIPIO_RES'])
    ii = Dat['CVE_MUN'].isin(lut_zms.CVE_MUN)
    Dat = Dat.loc[ii,].reset_index()

    # Mapear casos a ZMs de interés
    cve_zms = lut_zms.CVE_ZM[Dat.CVE_MUN].reset_index().CVE_ZM
    Dat['CVE_ZM'] = cve_zms

    # Limpiar
    Dat = Dat.drop(columns = ['index', 'CVE_MUN'])

    # Contar
    Dat = Dat.groupby(['FECHA_SINTOMAS',
                       'CVE_ZM',
                       'CLASIFICACION_FINAL']).count()

    # Obtener datos de región de interés
    Dat_ent = Dat.loc[(slice(None), args.region), :]
    Dat_ent = Dat_ent.droplevel('CVE_ZM')
    Dat_ent.reset_index(inplace=True)
    Dat_ent = Dat_ent.pivot(index='FECHA_SINTOMAS',
                            columns='CLASIFICACION_FINAL',
                            values='ID_REGISTRO')
    Dat_ent.reset_index(inplace=True)
    Dat_ent.fillna(0, inplace=True)
    Dat_ent['total'] = Dat_ent[1] + Dat_ent[2]
    Dat_ent = Dat_ent.rename(columns={'FECHA_SINTOMAS': 'date',
                                      1: 'positive',
                                      2: 'negative'}).drop(columns ='negative')
    Dat_ent['date'] = pd.to_datetime(Dat_ent.date)
    Dat_ent.set_index('date', inplace=True)


    # Correr modelo
    gm = GenerativeModel(str(args.region), Dat_ent)
    gm.sample()

    # Escribir resultados
    result = summarize_inference_data(gm.inference_data)
    result['zona_metropolitana'] = args.region
    result['fecha_estimado'] = date.today()
    result.to_csv("r_efectiva.csv")
