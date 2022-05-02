import clr
import sys
from os.path import exists   
from os import path

# The SetupLatest method will make your script find the MIKE assemblies at runtime.
# This is required for MIKE Version 2019 (17.0) and onwards. For previous versions, the
# next three lines must be removed.
clr.AddReference("DHI.Mike.Install, Version=1.0.0.0, Culture=neutral, PublicKeyToken=c513450b5d0bf0bf")
from DHI.Mike.Install import MikeImport, MikeProducts
MikeImport.SetupLatest(MikeProducts.MikeCore)

clr.AddReference("DHI.MHydro.Data")
from DHI.MHydro.Data import RootPfs
from DHI.MHydro.Data.WQ import WQData, WQParamLocation, WQParam

list_helper_dll = path.join(path.dirname(path.abspath(__file__)), 'ListHelper.dll')
clr.AddReference(list_helper_dll)
#res=clr.AddReference("ListHelper")
from ListHelper import MHydroListHelper

class MHydroDataHandler:

    def __init__(self):
        self.m_hydro_data = RootPfs()
        self.m_hydro_data.UndoMgr.Disable()
        self.wq=None
        self.catchment_List = None
        self.branch_list = None
        self.water_user_list = None
        self.reservoir_list = None
        self.wq_var_dict = dict()
        self.locations_not_found = list()

    def load_data(self, filePath):

        if not exists(filePath):
            print("could not find template file: "+filePath)
            raise

        self.m_hydro_data.Load(filePath)
        self.wq = WQData(self.m_hydro_data.WQBasin.Clob)
        self.catchment_List = list(self.m_hydro_data.CatchmentList)
        self.branch_list = list(self.m_hydro_data.BranchList)
        self.reservoir_list = list(self.m_hydro_data.ReservoirList)
        self.water_user_list = list(self.m_hydro_data.WaterUserList)
        self.model_definition = self.wq.WQModel.WQModelDefinitionList
        if len(self.wq.WQModel.WQModelDefinitionList) == 0:
            print("no water quality model is defined")
            raise 
        self.wq_variable_list = self.wq.WQModel.WQModelDefinitionList[0].WQVariableList
        for wq_variable in self.wq_variable_list:
            self.wq_var_dict[wq_variable.Name.lower()]=wq_variable.VariableID

    def update_wq_parameters(self, short_name, parameter_names, data_files, item_numbers):
        if self.wq is None:
            print("Model has not been loaded")
            raise
        
        parameter_names_update = [x.strip() for x in parameter_names.split("|")]
        data_files_update = [x.strip() for x in data_files.split("|")]
        item_numbers_update = [x.strip() for x in item_numbers.split("|")]

        par_location = self._get_location_param(short_name)

        for parId, parameter_name in enumerate(parameter_names_update):
            par_found = self._filter_param(par_location, parameter_name)
            
            if len(data_files_update)>1:
                par_found.DataFile = data_files_update[parId]
            else:
                par_found.DataFile = data_files_update[0]
            par_found.DataFileItemNo = item_numbers_update[parId]

    def get_mHydro_data(self):
        return self.m_hydro_data

    def get_locations_not_found(self):
        return self.locations_not_found

    def write_to_file(self, fileName):
        clob_string = self.wq.GetClobString()
        self.m_hydro_data.WQBasin.Clob = clob_string
        self.m_hydro_data.Save(fileName)

    def _get_location_param(self, short_name):
        short_name_lower=short_name.lower()
        par_loc_found = [x for x in self.wq.WQParamLocationList if x.LinkedToShortName.lower() == short_name_lower]
        if len(par_loc_found) == 0:
            print("Adding to locations: "+short_name)
            par_loc_found = [self._create_location_param(short_name)]

        return par_loc_found[0]#.WQParamList

    # not working because of the list implementation in pythonnet
    def _create_location_param(self, short_name):
        
        catch_found = [x for x in self.catchment_List if x.ShortName.lower() == short_name.lower()]
        branch_found = [x for x in self.branch_list if x.ShortName.lower() == short_name.lower()]
        water_user_found = [x for x in self.water_user_list if x.ShortName.lower() == short_name.lower()]
        reservoir_found = [x for x in self.reservoir_list if x.ShortName.lower() == short_name.lower()]
        
        par_location = WQParamLocation()
        par_location.Model = self.model_definition[0].ModelID
        par_location.Template = self.model_definition[0].Template
        par_location.LocationSubType = WQParamLocation.EnumLocationSubType.Initial

        if len(catch_found) > 0:
            par_found = catch_found[0]
            par_location.Chainage = par_found.Chainage
            par_location.LocationType = WQParamLocation.EnumLocationType.Catchment
            par_location.LocationSubType = WQParamLocation.EnumLocationSubType.Source
            par_location.ConservativeTransport = True
            par_location.ResidenceTimeCalcType = WQParamLocation.ReachResidenceTimeCalcTypes.NoneNoDecay
        elif len(branch_found)>0:
            par_found = branch_found[0]
            par_location.Chainage = par_found.EndChainage
            par_location.LocationType = WQParamLocation.EnumLocationType.Branch
            par_location.ConservativeTransport = False
            par_location.ResidenceTimeCalcType = WQParamLocation.ReachResidenceTimeCalcTypes.FromCalculatedWaterDepth
        elif len(water_user_found)>0:
            par_found = water_user_found[0]
            par_location.LocationType = WQParamLocation.EnumLocationType.WaterUser
            par_location.LocationSubType = WQParamLocation.EnumLocationSubType.PointSource
            par_location.ResidenceTimeCalcType = WQParamLocation.ReachResidenceTimeCalcTypes.NoneNoDecay
            par_location.ConservativeTransport = True
        elif len(reservoir_found)>0:
            par_found = reservoir_found[0]
            par_location.Chainage = par_found.Chainage
            par_location.LocationType = WQParamLocation.EnumLocationType.Reservoir
            par_location.LocationSubType = WQParamLocation.EnumLocationSubType.Source
            par_location.ConservativeTransport = False
            par_location.ResidenceTimeCalcType = WQParamLocation.ReachResidenceTimeCalcTypes.FromCalculatedWaterDepth
        else:
            print("location short name not found: "+short_name)
            raise

        par_location.Name = par_found.Name
        par_location.LinkedTo = par_found.ObjectID
        par_location.LinkedToShortName = par_found.ShortName

        MHydroListHelper.AddParamLocation(self.wq, par_location)

        return par_location

    def _filter_param(self, par_location, par_name):
        par_name = par_name.lower().strip()
        if par_name not in self.wq_var_dict:
            print("variable not found in Ecolab model: "+par_name)
            raise
        parId = self.wq_var_dict[par_name]
        par_found = [x for x in par_location.WQParamList if x.VariableID == parId]
        if len(par_found)==0:
            par_found=[self._create_parameter(par_name)]
            MHydroListHelper.AddParamToLocation(par_location, par_found[0])

        return par_found[0]

    def _create_parameter(self, par_name):
        var_found = [x for x in self.wq_variable_list if x.Name.lower() == par_name.lower()]
        id=var_found[0].VariableID.ToString()
        if len(var_found)==0:
            print("variable not found in WQ model: "+par_name)
        wq_param=WQParam()
        wq_param.VariableID= var_found[0].VariableID
        wq_param.Name = var_found[0].Name
        wq_param.Description = var_found[0].Description
        wq_param.MinValue = var_found[0].MinValue
        wq_param.MaxValue = var_found[0].MaxValue
        wq_param.DefaultValue = var_found[0].DefaultValue
        wq_param.FixedValue = var_found[0].DefaultValue
        wq_param.OnlineHelp = var_found[0].OnlineHelp
        wq_param.Unit = var_found[0].Unit
        wq_param.Type = var_found[0].Type
        wq_param.ParamType = wq_param.EnumParamType.TimeVarying
        return wq_param