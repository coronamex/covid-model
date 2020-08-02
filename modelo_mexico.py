#!/usr/bin/env python

import pymc3 as pm
import pandas as pd
import numpy as np
import arviz as az
# from matplotlib import pyplot as plt
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
    required.add_argument("--lut_estados",
                          help=("Tabla que asocia código numérico de "
                                "estados con su nombre"),
                          required=True, type=str)
    required.add_argument("--region",
                          help=("Clave numérica de la entidad para "
                                "analizar."),
                          required=True, type=int)

    # Read arguments
    print("Reading arguments")
    args = parser.parse_args()

    # Processing goes here if needed

    return args

if __name__ == "__main__":
    args = process_arguments()

    # Leer datos
    lut_estados = pd.read_csv(args.lut_estados,
                              header=None, index_col=0)[1]
    Dat = pd.read_csv(args.base_de_datos,
                      compression='gzip', sep = ",",
                      encoding='iso-8859-1')

    # Contar pruebas por fecha por entidad
    Dat = Dat[Dat.RESULTADO != 3][['FECHA_SINTOMAS',
                                   'ENTIDAD_UM',
                                   'ID_REGISTRO',
                                   'RESULTADO']]
    Dat = Dat.groupby(['FECHA_SINTOMAS',
                       'ENTIDAD_UM',
                       'RESULTADO']).count()

    # Obtener datos de región de interés
    Dat_ent = Dat.loc[(slice(None), args.region), :]
    Dat_ent = Dat_ent.droplevel('ENTIDAD_UM')
    Dat_ent.reset_index(inplace=True)
    Dat_ent = Dat_ent.pivot(index='FECHA_SINTOMAS',
                            columns='RESULTADO',
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
    result['estado'] = lut_estados[args.region]
    result['fecha_estimado'] = date.today()
    result.to_csv("r_efectiva.csv")
