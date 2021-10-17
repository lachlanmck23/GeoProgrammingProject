# GeoProgrammingProject
##Data and code repository for Geospatial Programming major project##

##########
DATA FILES
##########

Grocery.zip contains original grocery store point data.
#########################################################
Hospitals.zip contains original hospital point data.
#########################################################
WhitehorseAddressesFull.zip contains address point data for all of Whitehorse, too big for succesful operation of any version of script.
#########################################################
Whitehorse20Addresses.zip contains address point data consisting of 20 addresses, used for testing and demonstrating functionality of script.
#########################################################
ParklandNotMerged.zip contains original parkland vector file (parkland2.shp), which is used in all versions of script except ConsoleScriptwithClipMethodforPreparedParkLayerFULLYFUNCTIONAL.py. 
ConsoleScriptwithClipMethodforOriginalParklandFileNONFUNCTIONALDUETOINVALIDGEOMETRYISSUE.py is nonfunctional due to invalid geometries encountered as a result of using this file.
#########################################################
ParklandMergedandSplit.zip contains parkland vector file (parklandsplit.shp) used in ConsoleScriptwithClipMethodforPreparedParkLayerFULLYFUNCTIONAL.py, 
has already been dissolved manually with toolbox, so skips these steps in script, no issues with invalid geometries.
#########################################################
FinalAddressFileWScore20Addresses.zip contains final address point file output with scores, after functional script run with Whitehorse20Addresses.zip.


#######
SCRIPTS
#######

ConsoleScriptwithClipMethodforOriginalParklandFileNONFUNCTIONALDUETOINVALIDGEOMETRYISSUE.py is the first revision of script. It is non-functional due to issues with invalid geometries. Run from Python console in QGIS.
#########################################################
ConsoleScriptwithClipMethodforPreparedParkLayerFULLYFUNCTIONAL.py is the second revision. It is fully functional, but requires pre-prepared (parklandsplit.shp) file to fix invalid geometry issue. Run from Python console in QGIS.
#########################################################
FullFinalConsoleScriptWithZonalMethodTHISISMOSTCOMPLETEANDFUNCTIONALCONSOLESCRIPTUSEDFORTOOL.py is the final console script revision. It is fully functional and takes the (parkland2.shp) file. It uses the zonal histogram method instead of clipping, and is a full end-to-end processing script. Run from Python console in QGIS.
#########################################################
LockdownLiveabilityToolNoAdjustableParameters.py is an interactive processing script based on FullFinalConsoleScriptWithZonalMethodTHISISMOSTCOMPLETEANDFUNCTIONALCONSOLESCRIPTUSEDFORTOOL.py. It allows for selection of layers to determine filepath of input data, however the filenames used are determined by the actual script within the tool. As such, editing the filename variables in the script would be required to use different input data. It is run from the processing toolbox in QGIS.
#########################################################
LockdownLiveabilityToolWithAdjustableParameters.py is the same as the previous tool, but allows for interactive selection of buffer size and significant parkland size. It is the most complete script produced and could be considered the final product of the project. It is run from the processing toolbox in QGIS.
