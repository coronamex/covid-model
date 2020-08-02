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

args_lut_zms = "/home/sur/micropopgen/src/coronamex/covid-model/selected_zms.csv"
args_base_de_datos = "/home/sur/micropopgen/src/coronamex/datos/datos_abiertos/base_de_datos.csv.gz"

# Leer datos
lut_zms = pd.read_csv(args_lut_zms,
                          header=0, index_col=None,
                          dtype = {'CVE_ZM': str,
                                   'CVE_ENT': str,
                                   'CVE_MUN': str})
lut_zms = lut_zms.drop(columns=['NOM_ZM', 'NOM_MUN', 'CVE_ENT', 'NOM_ENT'])
lut_zms.index = lut_zms['CVE_ZM']
lut_zms

Dat = pd.read_csv(args_base_de_datos,
                  compression='gzip', sep = ",",
                  encoding='iso-8859-1',
                  dtype = {'ENTIDAD_RES': str,
                           'MUNICIPIO_RES': str})

# Contar pruebas por fecha por entidad
Dat = Dat[Dat.RESULTADO != 3][['FECHA_SINTOMAS',
                               'ENTIDAD_RES',
                               'MUNICIPIO_RES',
                               'ID_REGISTRO',
                               'RESULTADO']]
Dat['CVE_MUN'] = Dat.ENTIDAD_RES + Dat.MUNICIPIO_RES
Dat = Dat.drop(columns=['ENTIDAD_RES', 'MUNICIPIO_RES'])
Dat.CVE_MUN[0:10]
Dat
Dat[]




Dat = Dat.groupby(['FECHA_SINTOMAS',
                   'MUNICIPIO_RES',
                   'RESULTADO']).count()
