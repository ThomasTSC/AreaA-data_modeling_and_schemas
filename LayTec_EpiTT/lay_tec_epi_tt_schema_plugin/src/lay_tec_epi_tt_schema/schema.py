#
# Copyright The NOMAD Authors.
#
# This file is part of NOMAD. See https://nomad-lab.eu for further info.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from nomad.metainfo import Quantity, Package, SubSection, MEnum, Section
from nomad.datamodel.data import EntryData, ArchiveSection
from nomad.datamodel.metainfo.annotations import ELNAnnotation, ELNComponentEnum
from nomad.datamodel.metainfo.eln import Measurement, Substance, SampleID, System
from nomad.units import ureg
import numpy as np
from datetime import datetime
import re
import pandas as pd

from nomad.datamodel.metainfo.basesections import Measurement
from nomad.datamodel.data import EntryData
from nomad.metainfo import (
    Package,
    Section,
)
from nomad.datamodel.data import (
    EntryData,
    ArchiveSection,
)

m_package = Package(name='LayTec EpiTT Schema')
'''
 'CurveDistanceY'],
 'REFLEC_WAVELENGTH': '633.14',
 'REFLEC_BANDWIDTH': '3.33',
 'PYRO_WAVELENGTH': '951.29',
 'PYRO_BANDWIDTH': '10.01',
 'WHITE_WAVELENGTH': '405.14',
 'WHITE_BANDWIDTH': '2.15',
 'COLS': '58',
 'TIME': '2020-08-27-11-11-30',
 'MODULE_NAME': 'Ring TT1 1',
 'WAFER_LABEL': 'Al Zone 1 (Center)',
 'WAFER_ZONE': 'Center',
 'WAFER': '1',
 'RUN_ID': '200827_158_TEOS',
 'RUNTYPE_ID': '20',
 'RUNTYPE_NAME': 'AlGa510mm90',

 >>>> 1. BEGIN
>>>> 2. PyroTemp
>>>> 3. DetWhite
>>>> 4. DetReflec
>>>> 5. RLo
'''

class LayTecEpiTT_process_time(ArchiveSection):
    '''
    LayTec's EpiTT is an emissivity-corrected pyrometer and
    reflectance measurement for in-situ measurement during
    growth processes (https://www.laytec.de/epitt)
    '''
    process_time = Quantity(
        type=np.dtype(np.float64),
        unit = "seconds",
        shape = ['*'],
        )

class ReflectanceWavelengthTransient(ArchiveSection):
    m_def = Section(
        a_eln=dict(lane_width='600px'),
        label_quantity="wavelength",
        a_plot=[
            {'label': 'EpiTT transient',
             'x': 'process_time',
             'y': 'intensity'
            }]
        )
    wavelength = Quantity(
        type=str,
        description='Reflectanec Wavelength',
        )
    wavelength_name = Quantity(
        type=str,
        description='Name of Reflectance ',
        )
    #time = Quantity(
    #    type=np.dtype(np.float64),
    #    unit = "",
    #    shape = ['n_values'],
    #    )
    process_time = Quantity(
        type=LayTecEpiTT_process_time.process_time, #dict(type_kind='reference',type_data='#/definitions/section_definitions/1/quantities/8'),
        default = '#data/process_time'
        )
    intensity= Quantity(
        type=np.dtype(np.float64),
        #unit = "µm",
        shape = ['*'],
        a_plot={
            'x': 'process_time', 'y': 'intensity'
        })

class LayTecEpiTT(Measurement, LayTecEpiTT_process_time):
    '''
    LayTec's EpiTT is an emissivity-corrected pyrometer and
    reflectance measurement for in-situ measurement during
    growth processes (https://www.laytec.de/epitt)
    '''
    method = Quantity(
        type=str,
        description='Method used to collect the data',
        default='LayTec_EpiTT')
    #'TIME': '2020-08-27-11-11-30',
    module_name = Quantity(
        type=str, #'Ring TT1 1',
        description='MODULE_NAME',
        )
    wafer_label = Quantity(
        type=str, #'Al Zone 1 (Center)',
        description='WAFER_LABEL',
        )
    wafer_zone = Quantity(
        type=str, #'Center',
        description='WAFER_ZONE',
        )
    wafer = Quantity(
        type=str, #'1',
        description='WAFER',
        )
    run_ID = Quantity(
        type=str, #'200827_158_TEOS',
        description='RUNTYPE_ID',
        )
    runtype_ID = Quantity(
        type=str, #'20',
        description='RUNTYPE_ID',
        )
    runtype_name = Quantity(
        type=str, #'AlGa510mm90',
        description='RUNTYPE_NAME',
        )
    # process_time = Quantity(
    #     type=np.dtype(np.float64),
    #     unit = "seconds",
    #     shape = ['n_values'],
    #     )
    pyrometer_temperature = Quantity(
        type=np.dtype(np.float64),
        description="PyroTemp transient. LayTec's TrueTemperature of the substrate surface --> Emissivity-corrected pyrometer ",
        unit = "°C",
        shape = ['*'],
        )
    reflectance_wavelength = SubSection(section_def=ReflectanceWavelengthTransient, repeats=True)

    #growth_analysis = SubSection(section)

class LayTec_EpiTT_Measurement(LayTecEpiTT, EntryData, ArchiveSection):
    '''
    Class autogenerated from yaml schema.
    '''
    m_def = Section(
        a_eln=dict(lane_width='600px'),
        a_plot=[
            {'label': 'EpiTT transients',
             'x': 'process_time',
             'y': ['pyrometer_temperature','reflectance_wavelength/:/intensity'],
             #'layout': {'yaxis': {'type': 'log'}},
            },]
        )

    data_file = Quantity(
        type=str,
        description='Data file containing the EpiTT data (*.dat)',
        a_eln=dict(
            component='FileEditQuantity',
        )
        )
    def normalize(self, archive, logger):
        super(LayTec_EpiTT_Measurement, self).normalize(archive, logger)
        logger.info('ExampleSection.normalize called')

        def parse_epitt_data(self):
            #with open (fp, "rt") as f:
            #data = self.readlines()
            line = self.readline().strip()
            parameters = {}
            header = []
            while line.startswith(("##","!",)) or line.strip()=="":
                match = re.match(r"##(\w+)\s*=\s*(.*)", line.strip())
                if match:
                    parameter_name = match.group(1)
                    parameter_value = match.group(2)
                    if parameter_name == "YUNITS":
                        yunits = parameter_value.split("\t")
                        parameters[parameter_name] = yunits
                    else:
                        parameters[parameter_name] = parameter_value
                line = self.readline().strip()
            header=line.split("\t")
            data_in_df = pd.read_csv(self,sep="\t",names=header,skipfooter=1)
            return parameters, data_in_df

        if archive.data.data_file:
            with archive.m_context.raw_file(self.data_file) as file:
                epitt_data=parse_epitt_data(file)
                name_string=""
                paramters_for_name=["RUN_ID","RUNTYPE_ID","RUNTYPE_NAME","MODULE_NAME","WAFER_LABEL","WAFER"]
                for p in paramters_for_name:
                    if p in epitt_data[0].keys():
                        name_string += "_" + epitt_data[0][p]
                if name_string != "":
                    self.name = name_string[1:]
                    self.lab_id = name_string[1:]
                if "TIME" in epitt_data[0].keys():
                    self.datetime = datetime.strptime(epitt_data[0]["TIME"],'%Y-%m-%d-%H-%M-%S') #'2020-08-27-11-11-30',
                if "MODULE_NAME" in epitt_data[0].keys():
                    self.module_name = epitt_data[0]["MODULE_NAME"]
                if "WAFER_LABEL" in epitt_data[0].keys():
                    self.wafer_label = epitt_data[0]["WAFER_LABEL"]
                if "WAFER_ZONE" in epitt_data[0].keys():
                    self.wafer_zone = epitt_data[0]["WAFER_ZONE"]
                if "WAFER" in epitt_data[0].keys():
                    self.wafer = epitt_data[0]["WAFER"]
                if "RUN_ID" in epitt_data[0].keys():
                    self.run_ID = epitt_data[0]["RUN_ID"]
                if "RUNTYPE_ID" in epitt_data[0].keys():
                    self.runtype_ID = epitt_data[0]["RUNTYPE_ID"]
                if "RUNTYPE_NAME" in epitt_data[0].keys():
                    self.runtype_name = epitt_data[0]["RUNTYPE_NAME"]
                #self.time_transient = epitt_data[1]["BEGIN"]
                self.process_time = epitt_data[1]["BEGIN"]
                self.pyrometer_temperature = epitt_data[1]["PyroTemp"]
                self.reflectance_wavelength = []
                for wl, datacolname in zip(['REFLEC_WAVELENGTH', 'PYRO_WAVELENGTH', 'WHITE_WAVELENGTH'],["DetReflec", "RLo", "DetWhite"]):
                    if wl in epitt_data[0].keys():
                        transient_object = ReflectanceWavelengthTransient()
                        transient_object.wavelength = epitt_data[0][wl]
                        transient_object.wavelength_name = wl#epitt_data[0]["REFLEC_WAVELENGTH"]
                        transient_object.intensity = epitt_data[1][datacolname]
                        self.reflectance_wavelength.append(transient_object)

        #def rolling_average_insitu_reflectance(wavelength, start, period):
        #    df_refl_data=pd.DataFrame([self.process_time,self.)


m_package.__init_metainfo__()
'''
with open (fp, "rt") as f:
    line = f.readline().strip()
        # Extract parameters
    parameters = {}
    header = []
    #print(line)
    while line.startswith(("##","!",)) or line.strip()=="":
        #if "=" in line:
        #if line.startswith("##")==True:# or line.startswith("!")==True :
        #line=f.readline()
            #print(line)
        #if line.startswith("##"):
            #print(line)
            match = re.match(r"##(\w+)\s*=\s*(.*)", line.strip())
            if match:
                parameter_name = match.group(1)
                parameter_value = match.group(2)
                if parameter_name == "YUNITS":
                    yunits = parameter_value.split("\t")
                    parameters[parameter_name] = yunits
                else:
                    parameters[parameter_name] = parameter_value
            line = f.readline().strip()
            #print("l:",line,":e")

        #elif line.startswith("BEGIN"):
        #print(f.readlines())
    header=line.split("\t")
    data_in_df = pd.read_csv(f,sep="\t",names=header,skipfooter=1)
        #elif line.startswith("BEGIN"):
        #    print("pipi")
        #elif line.strip()  != "":
        #    print(line)
        #    header = line.split("\t")'''