import clr
from os.path import exists  
import csv


# The SetupLatest method will make your script find the MIKE assemblies at runtime.
# This is required for MIKE Version 2019 (17.0) and onwards. For previous versions, the
# next three lines must be removed.
clr.AddReference("DHI.Mike.Install, Version=1.0.0.0, Culture=neutral, PublicKeyToken=c513450b5d0bf0bf")
from DHI.Mike.Install import MikeImport, MikeProducts
MikeImport.SetupLatest(MikeProducts.MikeCore)

clr.AddReference("DHI.MHydro.Data")
from DHI.MHydro.Data import RootPfs, KinematicRoutingMethodPfs, RiverNodeType

clr.AddReference("DHI.MikeBasin.Common")
from DHI.MikeBasin.Common import WaterLevelMethods

clr.AddReference("DHI.Generic")
from DHI.Generic import *

class MHydroDataHandler:

    def __init__(self):
        self.m_hydro_data = RootPfs()
        self.m_hydro_data.UndoMgr.Disable()
        self.global_node_list = list()
        self.kinematic_routing_methods = list()
        self.nodes_missing = list()

    def load_data(self, filePath):
        """load mike hydro data"""

        if not exists(filePath):
            print("could not find template file: "+filePath)
            raise

        self.m_hydro_data.Load(filePath)
        self.global_node_list = self._get_global_node_list()
        self.kinematic_routing_methods = self.m_hydro_data.KinematicRoutingMethodList

    def get_mHydro_data(self):
        return self.m_hydro_data

    def write_to_file(self, fileName):
        """export to mike hydro file"""

        self.m_hydro_data.Save(fileName)

    def update_node(self, par_dict):
        """update or create node with new parameters"""

        node = self._get_node(par_dict["River node"])
        if node is None:
            self.nodes_missing.append(par_dict["River node"])
            return

        routing_method=self._get_routing_method_node(node)
        self._update_routing_method_from_dict(routing_method, par_dict, node)

    def get_parameter_dictionary(self, nodeId, description, routing_type, delay, shape, 
                                water_level_method, manning_N, width, slope, 
                                manning_max_depth):
        """make dictionary with parameters used for updating node"""

        par=dict()
        par["River node"]=nodeId
        par["ID"]=description
        par["Flow routing method"]=routing_type #self._routing_type(routing_type.lower())
        if par["Flow routing method"] is None:
            print("Node id:"+nodeId+". Routing type not found: "+routing_type)
            return
        par["Delay"]=delay
        par["Shape"]=shape
        par["Water level method"]=water_level_method#self._water_level_method(water_level_method.lower())
        if par["Water level method"] is None:
            print("Node id:"+nodeId+". water level method not found: "+water_level_method)
            return
        par["ManningN"]=manning_N
        par["Slope"]=slope
        par["ManningMaxDepth"]=manning_max_depth
        par["Width"]=width
        par["Type"]=""
        return(par)

    def write_update_template(self, file_path):
        """create a template file with all nodes in model and there info"""
        if exists(file_path):
            print("Template file already exists. Delete to generate a new file.")
            raise FileExistsError

        par_dict=self.get_parameter_dictionary("nodeId", "", "translation", 1, 1, "manning", 1, 1, 0, 0)
        export_dict={"Branch":"","River node":"","Chainage":""}
        for key, val in par_dict.items():
            export_dict[key]=val
        
        with open(file_path, "w", newline='') as f:
            writer=csv.writer(f, delimiter = ',')
            writer.writerow(list(export_dict.keys()))
            for node in self.global_nodes_list():
                routing_method=self._get_routing_method_node(node)
                self._update_dict_from_routing_method(routing_method, node, export_dict)
                export_dict["Branch"]=node.BranchName
                export_dict["Chainage"]=node.Chainage
                writer.writerow(list(export_dict.values()))

    def global_nodes_list(self):
        if len(self.global_node_list) is None:
            print("global list of nodes is empty. Try loading the data using: load_data()")
        return self.global_node_list

    def _get_node(self, node_identifier):
        nodeFound=[x for x in self.global_node_list if 
            x.Identifier.lower().strip()==node_identifier.lower().strip()]
        if len(nodeFound)>0:
            return nodeFound[0]
        return None

    def _update_dict_from_routing_method(self, routing_method, node, par_dict):
        par_dict["River node"] = node.Identifier
        par_dict["ID"] = routing_method.RoutingID
        par_dict["Flow routing method"]= self._routing_type(routing_method.FlowRoutingMethod,True)
        par_dict["Delay"] = routing_method.DelayK
        par_dict["Shape"] = routing_method.ShapeX
        par_dict["Water level method"] = self._water_level_method(routing_method.WaterLevelMethod,True)
        par_dict["ManningN"] = routing_method.ManningN
        par_dict["Width"] = routing_method.Width
        par_dict["Slope"] = routing_method.Slope
        par_dict["ManningMaxDepth"] = routing_method.ManningMaxDepth
        par_dict["Type"]=self._river_node_type(node.RiverNodeType, True)

    def _update_routing_method_from_dict(self, routing_method, par_dict, node):
        routing_method.BranchID=node.BranchID
        routing_method.RnChainage = node.Chainage # what is this?
        routing_method.RiverNodeID = node.ObjectID
        if par_dict["ID"]!=None:
            routing_method.RoutingID = par_dict["ID"]
        routing_method.FlowRoutingMethod = self._routing_type(par_dict["Flow routing method"].lower())
        routing_method.DelayK = par_dict["Delay"]
        routing_method.ShapeX = par_dict["Shape"]
        routing_method.WaterLevelMethod = self._water_level_method(par_dict["Water level method"].lower())
        routing_method.ManningN = par_dict["ManningN"]
        routing_method.Width = par_dict["Width"]
        routing_method.Slope = par_dict["Slope"]
        routing_method.ManningMaxDepth = par_dict["ManningMaxDepth"]

    def _get_routing_method_node(self, node):
        routing_method=[x for x in list(self.m_hydro_data.KinematicRoutingMethodList) if x.RiverNodeID==node.ObjectID]
        if len(routing_method)>1:
            print("more than 1 routing method, only first used for node: "+node.Identifier)
        if len(routing_method)==0:
            routing_method=KinematicRoutingMethodPfs(self.m_hydro_data)
            self.m_hydro_data.KinematicRoutingMethodList.Add(routing_method)
        else:
            routing_method=routing_method[0]

        return routing_method

    def _get_global_node_list(self):
        global_river_node_list=[x.RiverNodeList for x in self.m_hydro_data.BranchList]
        global_node_list = [node for sublist in global_river_node_list for node in sublist if node.IsEndOfBranch is False]
        return global_node_list

    def _routing_type(self,x, reverse=False):
        type_dict={
            'translation':RoutingType.Translation,
            'linearreservoir':RoutingType.LinearReservoir,
            'muskingum':RoutingType.Muskingum,
            'norouting':RoutingType.NoRouting
        }
        if reverse:
            return {v: k for k, v in type_dict.items()}.get(x,None)
        else:
            return type_dict.get(x, None)
    
    def _water_level_method(self,x, reverse=False):
        type_dict={
            'manning':WaterLevelMethods.Manning,
            'ratingcurve':WaterLevelMethods.RatingCurve,
            '':getattr(WaterLevelMethods,'None')
        }
        if reverse:
            return {v: k for k, v in type_dict.items()}.get(x,None)
        else:
            return type_dict.get(x, None)

    def _river_node_type(self,x, reverse=False):
        type_dict={
            "Catchment":RiverNodeType.Catchment,
            "Regular":RiverNodeType.Regular,
            "Reservoir":RiverNodeType.Reservoir,
            "RoutingMethod":RiverNodeType.RoutingMethod,
            "CatchmentRoutingMethod":RiverNodeType.CatchmentRoutingMethod,
            "ReservoirCatchment":RiverNodeType.ReservoirCatchment,
            "RoutingMethodPriority":RiverNodeType.RoutingMethodPriority,
            "CatchmentRoutingMethodPriority":RiverNodeType.CatchmentRoutingMethodPriority,
            "CatchmentPriority":RiverNodeType.CatchmentPriority
        }
        if reverse:
            return {v: k for k, v in type_dict.items()}.get(x,"other")
        else:
            return type_dict.get(x,None)
