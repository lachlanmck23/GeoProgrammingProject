## Defining filepaths and filenames
#######################################################
## THESE NEED TO BE DEFINED BY THE USER IF DIFFERENT ##
#######################################################
in_path = "C:/Users/FF/Desktop/GeoProgrammingProject/CorrectCRSData/"
out_path = "C:/Users/FF/Desktop/GeoProgrammingProject/Output/"

##Script set up for test 20 address file
addressFile = "AddressesTest.shp"

## Uncomment below line for use with full address file (NOTE: SCRIPT WILL NOT COMPLETE DUE TO DATASET SIZE)
## addressFile = "Addresses.shp"

## Uses original parkland file as no geometry issues using zonal method
parklandFile = "Parkland2.shp"

hospitalFile = "Hospitals.shp"
groceryFile = "Grocery.shp"

## Add address layer to view
addressLayer = iface.addVectorLayer(in_path + addressFile, addressFile[:-4], 'ogr')

## Define parameter dictionary, and run buffer tool
## Output result to /Output/ folder
bufferDict = {
'INPUT': addressLayer, 
'DISTANCE': 5000, 
'SEGMENTS': 10, 
'ENDCAPSTYLE': 0, 
'JOIN_STYLE':0,
'MITER_LIMIT':2,
'DISSOLVE_RESULT': False, 
'OUTPUT': (out_path + 'buffer_' + addressFile)
}
processing.run('native:buffer', bufferDict)
    
## Define filename of buffered file
bufferedFile =  ('buffer_' + addressFile)  

## Load buffered layer and hopsital layer to view
bufferedLayer = iface.addVectorLayer(out_path + bufferedFile, bufferedFile[:-4], 'ogr') 
hospitalLayer = iface.addVectorLayer(in_path + hospitalFile, hospitalFile[:-4], 'ogr')

## Define parameter dictionary, and run count points in polygons tool
## Output result to /Output/ folder
HcountDict = {
'CLASSFIELD' : '', 
'FIELD' : 'Hcount', 
'OUTPUT' : out_path + 'bufferHcount.shp', 
'POINTS' : hospitalLayer, 
'POLYGONS' : bufferedLayer, 
'WEIGHT' : ''
} 
processing.run('native:countpointsinpolygon', HcountDict)


## Define filename of buffers w/ hospital count, add layer to view
HcountFile = 'bufferHcount.shp'
HcountLayer = iface.addVectorLayer(out_path + HcountFile, HcountFile[:-4], 'ogr')

## Add grocery store layer to view
groceryLayer = iface.addVectorLayer(in_path + groceryFile, groceryFile[:-4], 'ogr')

## Define parameter dictionary, and run points in polygons tool
## Output result to /Output/ folder
GcountDict = {
'CLASSFIELD' : '', 
'FIELD' : 'Gcount', 
'OUTPUT' : out_path + 'bufferHGcount.shp', 
'POINTS' : groceryLayer, 
'POLYGONS' : HcountLayer, 
'WEIGHT' : ''
} 
processing.run('native:countpointsinpolygon', GcountDict)

## Define filename of buffers with hospital and store counts, and add layer to view    
HGcountFile = 'bufferHGcount.shp'
HGcountLayer = iface.addVectorLayer(out_path + HGcountFile, HGcountFile[:-4], 'ogr')

## Add parkland layer to view
parklandLayer = iface.addVectorLayer(in_path + parklandFile, parklandFile[:-4], 'ogr')

## Define parameter dictionary, and run buffer tool
## Output result to /Output/ folder
parkbufferDict = {
'INPUT': parklandLayer, 
'DISTANCE': 20, 
'SEGMENTS': 10, 
'ENDCAPSTYLE': 0, 
'JOIN_STYLE':0,
'MITER_LIMIT':2,
'DISSOLVE_RESULT': True, 
'OUTPUT': (out_path + 'buffer_' + parklandFile)
}
processing.run('native:buffer', parkbufferDict)

## Define filename of buffered dissolved parkland, add layer to view
parkBufferFile = 'buffer_' + parklandFile
parkBufferLayer = iface.addVectorLayer(out_path + parkBufferFile, parkBufferFile[:-4], 'ogr')

## Define parameter dictionary, and run negative buffer tool
## Output result to /Output/ folder    
parkNegbufferDict = {
'INPUT': parkBufferLayer, 
'DISTANCE': -20, 
'SEGMENTS': 10, 
'ENDCAPSTYLE': 0, 
'JOIN_STYLE':0,
'MITER_LIMIT':2,
'DISSOLVE_RESULT': False, 
'OUTPUT': (out_path + 'dissolve_' + parklandFile)
}
processing.run('native:buffer', parkNegbufferDict)

## Define filename of de-buffered dissolved parkland, add layer to view
parkDissolveFile = 'dissolve_' + parklandFile
parkDissolveLayer = iface.addVectorLayer(out_path + parkDissolveFile, parkDissolveFile[:-4], 'ogr')

## Loop through the features in the de-buffered parkland layer, define parameter dictionary, and run multipart to singlepart tool
## Output result to /Output/ folder
multiDict = { 
'INPUT' : parkDissolveLayer, 
'OUTPUT' : out_path + 'final_' + parklandFile
}
processing.run('native:multiparttosingleparts', multiDict)
    
## Define filename of de-buffered dissolved parkland, add layer to view
finalParkFile = 'final_' + parklandFile
finalParkLayer = iface.addVectorLayer(out_path + finalParkFile, finalParkFile[:-4], 'ogr')

## Define parameter dictionary, and run add geometry columns tool
## Output result to /Output/ folder
geomDict = { 
'CALC_METHOD' : 0, 
'INPUT' : finalParkLayer, 
'OUTPUT' : out_path + 'geom_'+ parklandFile
}
processing.run('qgis:exportaddgeometrycolumns', geomDict)

## Define filename of parkland w/ geometry, add layer to view
parkGeomFile = 'geom_'+ parklandFile
parkGeomLayer = iface.addVectorLayer(out_path + parkGeomFile, parkGeomFile[:-4], 'ogr')

## Define parameter dictionary, and run extract by attribute tool
## Output result to /Output/ folder
extractDict = { 
'FIELD' : 'area', 
'INPUT' : out_path + parkGeomFile, 
'OPERATOR' : 3, 
'OUTPUT' : out_path + 'extract_'+ parklandFile, 
'VALUE' : '15000' 
}
processing.run('native:extractbyattribute', extractDict)
    
## Define extracted "significant" parkland filename, and add layer to view
parkExtractFile = 'extract_'+ parklandFile
parkExtractLayer = iface.addVectorLayer(out_path + parkExtractFile, parkExtractFile[:-4], 'ogr')

extentDict = { 
'INPUT' : out_path+parkExtractFile, 
'OUTPUT' : out_path+'extent.shp', 
'ROUND_TO' : 0 
}
processing.run('native:polygonfromlayerextent', extentDict)

extentFile = out_path+'extent.shp'
extentLayer = iface.addVectorLayer(extentFile, extentFile[:-4], 'ogr')
extent = extentLayer.getFeatures()
for feature in extent:
    extentAttributes = feature.attributes()
    extentString = str(str(extentAttributes[0])+','+str(extentAttributes[2])+','+str(extentAttributes[1])+','+str(extentAttributes[3])+'['+str(extentLayer.crs().authid())+']')    
    print(extentString)

rasterizeDict = {
'BURN' : 1, 
'DATA_TYPE' : 5, 
'EXTENT' : extentString, 
'EXTRA' : '', 
'FIELD' : '', 
'HEIGHT' : 5000, 
'INIT' : None, 
'INPUT' : parkExtractLayer, 
'INVERT' : False, 
'NODATA' : 0, 
'OPTIONS' : '', 
'OUTPUT' : out_path+'Raster.tif', 
'UNITS' : 0, 
'WIDTH' : 5000
}
processing.run('gdal:rasterize', rasterizeDict)

rasterFile = out_path+'Raster.tif'

## Define parameter dictionary, and run clip tool with extracted parkland layer as overlay on address buffers
## Output result to /Output/ folder
zonalDict = { 
'COLUMN_PREFIX' : 'Z_',
'INPUT_VECTOR' : out_path + HGcountFile,
'INPUT_RASTER' : rasterFile, 
'OUTPUT' : out_path+'zonal_'+addressFile, 
'RASTER_BAND' : 1 
}
processing.run('native:zonalhistogram', zonalDict)

## Define filename of clipped buffer layer, add layer to view
zonalFile = 'zonal_'+ addressFile
zonalLayer = iface.addVectorLayer(out_path + zonalFile, zonalFile[:-4], 'ogr')


## Create QgsdataProvider object, used for updating data fields in clipped buffers w/ geometry layer
zonal_provider = zonalLayer.dataProvider()

## Use QgsdataProvider.addAttributes method to add empty QgsField objects corresponding to the normalised scores, and liveability score
## to the geomLayer file, QVariant.Double method used to create fields of data type "double"
zonal_provider.addAttributes([QgsField('HospNorm',QVariant.Double)])
zonal_provider.addAttributes([QgsField('GrocNorm',QVariant.Double)])
zonal_provider.addAttributes([QgsField('ParkNorm',QVariant.Double)])
zonal_provider.addAttributes([QgsField('LiveScore',QVariant.Double)])

## Update these new data fields and commit changes
zonalLayer.updateFields()
zonalLayer.commitChanges

## Define indexes for each count and area value in the geomLayer. This is to be able to easily obtain max value for each field, for normalisation equation
hospIndex = zonalLayer.fields().indexFromName('Hcount')
grocIndex = zonalLayer.fields().indexFromName('Gcount')
parkIndex = zonalLayer.fields().indexFromName('Z_1')

## Get features of geomLayer for subsequent loop
zonalAddresses = zonalLayer.getFeatures()

## Using a for loop, update the previously created fields with normalised scores, and lockdown liveability score
## This is done mathematically using each features value and the max value for that field
for address in zonalAddresses:
    
    zonalLayer.startEditing()    
    address['HospNorm'] = address['Hcount']/(zonalLayer.maximumValue(hospIndex))
    address['GrocNorm'] = address['Gcount']/(zonalLayer.maximumValue(grocIndex))
    address['ParkNorm'] = address['Z_1']/(zonalLayer.maximumValue(parkIndex))
    address['LiveScore'] = (address['HospNorm']+address['GrocNorm']+address['ParkNorm'])/3
    
    zonalLayer.updateFeature(address)

## Commit changes to data fields
zonalLayer.commitChanges

## Define parameter dictionary, and run join tool to join final attributes back to original layer
## Output result to /Output/ folder
joinDict = { 
'INPUT' : in_path + addressFile,
'FIELD' : 'PFI',
'INPUT_2' : out_path + zonalFile,
'FIELD_2' : 'PFI', 
'FIELDS_TO_COPY' : ['Hcount','Gcount','area','HospNorm','GrocNorm','ParkNorm','LiveScore'],
'METHOD' : 1, 
'DISCARD_NONMATCHING' : False,
'PREFIX' : '',
'OUTPUT' : out_path+'final_'+ addressFile,     
'NON_MATCHING': out_path+'nonmatching.shp'
}
processing.run('native:joinattributestable', joinDict)
    
## Define filename of final layer, and add final layer to view    
finalFile = 'final_'+ addressFile
finalLayer = iface.addVectorLayer(out_path + finalFile, finalFile[:-4], 'ogr')


