# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerMetadata
                                 A QGIS plugin
 An improved layer info dialog
                              -------------------
        begin                : 2015-06-09
        git sha              : $Format:%H$
        copyright            : (C) 2015 by Steven Kay
        email                : stevendkay@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4 import uic
# Initialize Qt resources from file resources.py
import resources_rc
from PyQt4 import QtCore, QtGui
from qgis.core import *
from qgis.core import QgsMapLayerRegistry
import time
from LayerMetadata_dialog import LayerMetadataDialog
import os.path


class LayerMetadata:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'LayerMetadata_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = LayerMetadataDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&LayerMetadata')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'LayerMetadata')
        self.toolbar.setObjectName(u'LayerMetadata')
 
        self.path = os.path.dirname( os.path.abspath( __file__ ) )
        
        # load the form
        self.dock = uic.loadUi( os.path.join(self.path, 'dockwidget.ui' ) )
        self.iface.addDockWidget( Qt.RightDockWidgetArea, self.dock )
        self.dock.cbGrouping.currentIndexChanged.connect(self.changedGrouping)
        self.dock.pbRefresh.clicked.connect(self.changedGrouping)
        self.reset()


    def reset(self):
        '''
        list of checkboxes and corresponding props
        '''
        self.checkboxes = []
        self.props = []
        
        self.yesplease = [] # the list of properties to show
        self.populateTableWidget()
        
        self.changedGrouping()
        
        

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('LayerMetadata', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/LayerMetadata/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Layer Metadata'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&LayerMetadata'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar

    def populateTableWidget(self):
        '''
        creates a list of widget items for the tableview.
        Note that if you add new properties, they must appear in this dictionary or they won't appear in the tree widget!
        '''
        opts = {
            "crs":"All",
            "layername":"All",
            "id":"All",
            "extent":"All",
            "geom":"Vector",
            "capabilities":"Vector",
            "extent":"All",
            "proj4":"All",
            "class":"All",
            "size":"Raster",
            "width":"Raster",
            "height":"Raster",
            "bands":"Raster",
            "metadata":"Raster",
            "x pixel size":"Raster",
            "y pixel size":"Raster",
            "band info":"Raster",
            "fields":"Vector",
            "provider":"All"
        }
        items=[]
        ix = 0
        self.dock.tabShow.setRowCount(len(opts))
        for x in opts:
            cb = QCheckBox()
            self.dock.tabShow.setCellWidget(ix, 0, cb);
            cb.setChecked(True)
            cb.stateChanged.connect(self.flipVisibility)
            self.checkboxes.append(cb)
            newitem = QTableWidgetItem(x)
            self.yesplease.append(x)
            self.dock.tabShow.setItem(ix, 1, newitem)
            newitem = QTableWidgetItem(opts[x])
            self.props.append(x)
            self.dock.tabShow.setItem(ix, 2, newitem)
            ix+=1
        self.dock.tabShow.resizeRowsToContents()
        return items
    
    def flipVisibility(self,cb):
        '''
        changed a checkbox, so refresh list of yesplease
        '''
        self.yesplease = []
        for x in range(0,self.dock.tabShow.rowCount()):
            checked = self.checkboxes[x].isChecked()
            if checked:
                self.yesplease.append(self.props[x])
        self.changedGrouping()
        
        
    def getItemsForTreeWidget(self, widget):
        '''
        gets a series of top-level tree items, one per text field, with
        attached second-level tree items, one per value. Lists are truncated at 1000 elements in case of
        low RAM.
        '''
        
        items = []
        ix = 0
        layers = QgsMapLayerRegistry.instance().mapLayers().values()
        outputLayers=[]
        groupby = widget.itemText(widget.currentIndex()) 
        ldata = {}
        ix = 0
        for layer in layers:
            dict = {}
            dict['layername'] = layer.name()
            
            try:
                prov = layer.dataProvider()
            except:
                # web layers (e.g. openlayers) do not have a provider
                dict['crs'] = str(layer.crs().authid())
                dict['provider'] = 'No provider (e.g. OpenLayers)'
                dict['class'] = 'Plugin'
                ldata[ix] = dict
                ix += 1
                continue
            
            dict['url'] = prov.dataSourceUri()
            dict['extent'] = prov.extent().toString(5)
            dict['provider'] = prov.name()
            dict['crs'] = str(layer.crs().authid())
            dict['proj4'] = str(layer.crs().toProj4())
            
            if layer.__class__.__name__ == 'QgsVectorLayer':
                dict['class'] = 'Vector'
            elif layer.__class__.__name__ == 'QgsRasterLayer':
                dict['class'] = 'Raster'
            else:
                dict['class'] = 'Unknown'
            
            dict['id'] = layer.id()
            if dict['class']=='Vector':
                dict['geom'] = str(self.getgeometrytypeforvector(layer.geometryType()))
                dict['capabilities'] = str(layer.capabilitiesString())
                fields = prov.fields()
                s=[]
                for field in fields:
                    fieldinfo = "%s %s %d:%d" % (field.name(), field.typeName(), field.length(), field.precision())
                    if fieldinfo!="":
                        s.append(fieldinfo)
                dict['fields'] = "\n".join([x for x in s])
            if dict['class']=='Raster':
                dict['size'] = "%d, %d" % (layer.width(), layer.height())
                dict['width'] = "%d" % layer.width()
                dict['height'] = "%d" % layer.height()
                dict['x pixel size'] = "%2.4f" % layer.rasterUnitsPerPixelX()
                dict['y pixel size'] = "%2.4f" % layer.rasterUnitsPerPixelY()
                numbands = prov.bandCount()
                dict['bands'] = str(numbands)
                s=[]
                for bix in range(1,numbands+1):
                    s.append('band %d datatype : %s' % (bix,self.getdatatypeforraster(prov.dataType(bix))))
                    s.append('band %d nodata : %s' % (bix, str(prov.srcNoDataValue(bix))))
                dict['band info']="\n".join([x for x in s])
            ldata[ix] = dict
            ix += 1
        
        ''' find unique values '''
        distinct = []
        for x in ldata:
            try :
                vall = ldata[x][groupby]
            except:
                vall = "N/A"
            if vall not in distinct:
                distinct.append(vall)
        
        for val in distinct:
            ''' add distinct values for the groupby field at level 1 '''
            widg = QTreeWidgetItem([val])
            items.append(widg)
            for layerix in sorted(ldata):
                try:
                    if ldata[layerix][groupby] == val:
                        ''' add layer name at 2nd level '''
                        layerwidj = QTreeWidgetItem(widg, [ldata[layerix]['layername'],'','',''])
                        ''' add properties at 3rd level '''
                        for prop in sorted(ldata[layerix]):
                            if prop in self.yesplease:
                                QTreeWidgetItem(layerwidj, [prop,ldata[layerix][prop]])
                except:
                    layerwidj = QTreeWidgetItem(widg, [ldata[layerix]['layername'],'','',''])
                    ''' add properties at 3rd level '''
                    for prop in sorted(ldata[layerix]):
                        if prop in self.yesplease:
                           QTreeWidgetItem(layerwidj, [prop,ldata[layerix][prop]])
                
        return items
    
    def getdatatypeforraster(self,intval):
        s = {0:"Unknown",1:"Byte",2:"Unsigned Int 16 bit",3:"Int 16 bit",4:"Unsigned Int 32 bit",5:"Int 32 bit", 6:"Float 32 bit", 7:"Float 64 bit", 8:"Cint16",9:"Cint32",10:"Cint64",
             10:"CFloat32", 11:"CFloat64", 12:"ARGB", 13:"ARGB pre-multiplied"}
        return s[intval]
    
    
    def getgeometrytypeforvector(self,intval):
        s = {0:"POINT",1:"LINE",2:"POLYGON",3:"UNKNOWN",4:"No GEOMETRY"}
        try:
            return s[intval]
        except:
            return s[3]
    
    def changedGrouping(self):
        items = self.getItemsForTreeWidget(self.dlg.cbGrouping)
        
        self.dlg.treeWidget.clear()
        self.dlg.treeWidget.addTopLevelItems(items)
        self.dlg.treeWidget.reexpand()
        
        self.dock.treeWidget.clear()
        items = self.getItemsForTreeWidget(self.dock.cbGrouping)
        self.dock.treeWidget.addTopLevelItems(items)
        self.dock.treeWidget.reexpand()
        
    
    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        self.dlg.cbGrouping.currentIndexChanged.connect(self.changedGrouping)
        self.reset()
        # Run the dialog event loop
        result = self.dlg.exec_()
