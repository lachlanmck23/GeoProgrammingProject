# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
from qgis import processing
import processing
from processing.core.Processing import Processing
import gdal
from PyQt5.QtCore import QVariant
from qgis.utils import iface
import os.path

from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterNumber,
                       QgsVectorDataProvider,
                       QgsField,
                       )
from qgis import processing


class LockdownLiveabilityTool(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """
    
    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT = 'INPUT'
    INPUTBUFFER = 'INPUTBUFFER'
    INPUTSIZE = 'INPUTSIZE'
    INPUT2 = 'INPUT2'
    INPUT3 = 'INPUT3'
    INPUT4 = 'INPUT4'
    OUTPUT = 'OUTPUT'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return LockdownLiveabilityTool()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'lockdownliveabilitytool'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Lockdown Liveability Tool')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('Example scripts')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'examplescripts'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        return self.tr("This tool takes an address point layer, and buffers it a selectable distance (default is 5km) to simulate a lockdown movement restriction. \nIt then counts Hospitals and Grocery Stores, as well as significant (>1.5ha) areas of parkland (significance size for parkland also adjustable). \nA lockdown liveability score is then calculated for each address.\n After processing, all files will appear in directory of input files. final_Address is layer with results,  needs to be manually added after processing.")

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT,
                self.tr('Address Point Layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUTBUFFER, 
                self.tr("Desired Lockdown Buffer Size in Metres"), 
                QgsProcessingParameterNumber.Integer, QVariant(5000)
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT2,
                self.tr('Hospital Point Layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT3,
                self.tr('Grocery Store Point Layer'),
                [QgsProcessing.TypeVectorPoint]
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT4,
                self.tr('Parkland Polygon Layer'),
                [QgsProcessing.TypeVectorPolygon]
            )
        )
        self.addParameter(
            QgsProcessingParameterNumber(
                self.INPUTSIZE, 
                self.tr("Input size for Significant Parkland Determination (in m^2)"), 
                QgsProcessingParameterNumber.Integer, QVariant(15000)
            )
        )
        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        """
        Here is where the processing itself takes place.
        """

        # Retrieve the feature source and sink. The 'dest_id' variable is used
        # to uniquely identify the feature sink, and must be included in the
        # dictionary returned by the processAlgorithm function.
        source = self.parameterAsSource(
            parameters,
            self.INPUT,
            context
        )
        source = self.parameterAsSource(
            parameters,
            self.INPUTBUFFER,
            context
        )
        source = self.parameterAsSource(
            parameters,
            self.INPUT2,
            context
        )
        source = self.parameterAsSource(
            parameters,
            self.INPUT3,
            context
        )
        source = self.parameterAsSource(
            parameters,
            self.INPUT4,
            context
        )
        source = self.parameterAsSource(
            parameters,
            self.INPUTSIZE,
            context
        )
        
        
        
        
        
        ## Obtain filepath from selected address layer, could not extend this functionality to work for actual layer inputs,
        ## resulted in instant crash if using the filePathFile, or 'INPUT1-4' as input for processing tools
        filePathFile = self.parameterDefinition('INPUT').valueAsPythonString(parameters['INPUT'], context)
        in_path = os.path.dirname(filePathFile[1:]) + '/'
        out_path = in_path 
        
        
        bufferdist = self.parameterAsDouble(parameters, self.INPUTBUFFER,
                                            context)
                                            
        sigsize = self.parameterAsDouble(parameters, self.INPUTSIZE,
                                            context)
        

        ## Defining filepaths and filenames
        #############################################################################
        ## NEED TO BE MANUALLY DEFINED BY USER IF USING FILES WITH DIFFERENT NAMES ##
        #############################################################################
        ##Script set up for test 20 address file
        
        addressFile = "AddressesTest.shp"

        ## Uncomment below line for use with full address file (NOTE: SCRIPT WILL NOT COMPLETE DUE TO DATASET SIZE)
        ## addressFile = "Addresses.shp"

        ## Uses original parkland file as no geometry issues using zonal method
        parklandFile = "Parkland2.shp"
        
        hospitalFile = "Hospitals.shp"
        groceryFile = "Grocery.shp"
        
        
        ##############################################################################
        ##############################################################################
        #############################################################################

        ## Add address layer to view, followed by obtaining features with getFeatures method, for subsequent loop
        addressLayer = iface.addVectorLayer(in_path + addressFile, addressFile[:-4], 'ogr')

        ## Define parameter dictionary, and run buffer tool
        ## Output result to /Output/ folder
        bufferDict = {
        'INPUT': addressLayer, 
        'DISTANCE': bufferdist, 
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

        ## Add parkland layer to view, followed by obtaining features with getFeatures method, for subsequent loop
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
        'VALUE' : sigsize 
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
            try:    
                address['HospNorm'] = address['Hcount']/(zonalLayer.maximumValue(hospIndex))
            except:
                    address['HospNorm'] = 0
            try:
                address['GrocNorm'] = address['Gcount']/(zonalLayer.maximumValue(grocIndex))
            except:
                    address['GrocNorm'] = 0
            try:
                address['ParkNorm'] = address['Z_1']/(zonalLayer.maximumValue(parkIndex))
            except:
                    address['ParkNorm'] = 0
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



        return {}
        
    

