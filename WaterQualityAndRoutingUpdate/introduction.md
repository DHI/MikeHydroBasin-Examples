# Get started guide

This document describe how to get started with using python notebooks that has been developed to ease some of the configuration tasks when setting up mike hydro basin models.

## Environment

**Code editor**
 It is recommended to install visual studio code with python extensions, but any python code editor can be used. [Visual Studio Code - Code Editing. Redefined](https://code.visualstudio.com/)

**Python**

To run the code python must be installed on the computer. The code has been tested with c-python version 3.8 and makes use of the following python libraries:

- pythonnet
- pandas

They can be installed by opening a command prompt and use the python, pip package manager:

![](images\pip_install.svg)

## mHydro\_data\_handlers module

The python notebooks does not contain the python code that interacts with mike hydro basin. This is handled in the underlying module &quot;mHydro\_data\_handlers&quot;:
<br>
<img align="top" width="140" src="images\module_files1.svg">
</br>
The module is used from the notebooks by instantiating a MHydroDataHandler as in the example below:
_from mHydro\_data\_handlers import routing\_methods
 data\_handler=routing\_methods.MHydroDataHandler()_

If the mHydro\_data\_handlers directory is found in the same folder as the notebooks as seen below it can be imported as above else the directory must be added to the path.

<br>
<img align="top" width="260" src="images\main_folder.svg">
</br>

## Pythonnet and ListHelper.dll

It is not possible to modify the standard .net list needed for some of the updating of the model due to the current functionality of pythonnet. Instead a small helper library is used.

## Python notebooks

The python notebooks import data\_handlers from the mHydro\_data\_handlers module and only contains the workflow around using the data handlers. Currently there is two available notebooks:

- wq\_update\_notebook
- routing\_method\_update\_notebook

The use are explained inside the notebooks, and below is a brief introduction.

### Water quality locations update

The notebook named wq\_update\_notebook.ipynb is a python notebook that update water quality locations of a mike hydro setup. It adds new locations from either branches, catchments, water users or reservoirs or update existing ones. It use wq\_locations data handler from the mHydro\_data\_handlers module, but further details about its use is contained within the notebook. Below is a screenshot from mike hydro with an example of a water quality location and 3 defined parameters BOD, DO and NH4.

<br>
<img align="top" width="1000" src="images\wq_location_parameters.svg">
</br>
To modify the water quality locations information is given in a csv file as seen below:
<br>
<img align="top" width="1000" src="images\wq_update_csv.svg">
</br>

 It has information about locations and parameters that should be generated or updated. Parameter names and item numbers are separated with &quot;|&quot; if there is more than one. The position represent the position of the parameter in the &quot;Location and Parameters&quot; view in mike hydro. If only one data\_files os specified it is assumed that the parameters use the same dfs0 file.

### Routing methods update

The notebook is named &quot;routing\_method\_update\_notebook.ipynb&quot;. Routing methods are either created or update if the exists and can be specified for individual river nodes in the river network. The global list of nodes can be exported to a csv file from the notebook and this can afterwards be modified and used for updating or adding new routing methods. Below is an example of this update file which is generated. ![]<br>
<img align="top" width="1000" src="images\router_update_csv.svg">
</br>

Further details are found inside the notebook but the parameters follow otherwise the parameter definitions which are also found inside the mike hydro gui as seen below.
<br>
<img align="top" width="1000" src="images\routing_methods.svg">
</br>