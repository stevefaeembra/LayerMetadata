# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LayerMetadata
                                 A QGIS plugin
 An improved layer info dialog
                             -------------------
        begin                : 2015-06-09
        copyright            : (C) 2015 by Steven Kay
        email                : stevendkay@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load LayerMetadata class from file LayerMetadata.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .LayerMetadata import LayerMetadata
    return LayerMetadata(iface)
