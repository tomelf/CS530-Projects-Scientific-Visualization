#!/usr/bin/env python

import sys
import vtk
from vtk.util.misc import vtkGetDataRoot

def print_camera_settings(obj, event):
    global ren
    # ---------------------------------------------------------------
    # Print out the current settings of the camera
    # ---------------------------------------------------------------
    camera = ren.GetActiveCamera()
    print "Camera settings:"
    print "  * position:        %s" % (camera.GetPosition(),)
    print "  * focal point:     %s" % (camera.GetFocalPoint(),)
    print "  * up vector:       %s" % (camera.GetViewUp(),)
    print "  * clipping range:  %s" % (camera.GetClippingRange(),)

def after_print_camera_settings(obj, event):
    print ""

def CheckAbort(obj, event):
    if obj.GetEventPending() != 0:
        obj.SetAbortRender(1)

def Main():
    global ren
    print "data: %s" % sys.argv[1]
    reader = vtk.vtkStructuredPointsReader()
    reader.SetFileName(sys.argv[1])

    # Create the standard renderer, render window and interactor
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    
    iren.RemoveObservers('RightButtonPressEvent')
    iren.AddObserver('RightButtonPressEvent', print_camera_settings, 1.0)
    iren.AddObserver('RightButtonPressEvent', after_print_camera_settings, -1.0)

    datapoints = [
               [420,0.1,0.1,1,0.0001],
               [950,0,0.8,1,0.0002],
               [1642,0.1,0,1,1]
               ]

    # Create transfer mapping scalar value to opacity
    opacityTransferFunction = vtk.vtkPiecewiseFunction()
    for p in datapoints:
        opacityTransferFunction.AddPoint(p[0], p[4])
    
    # Create transfer mapping scalar value to color
    colorTransferFunction = vtk.vtkColorTransferFunction()
    for p in datapoints:
        colorTransferFunction.AddHSVPoint(p[0], p[1], p[2], p[3])
    
    # The property describes how the data will look
    volumeProperty = vtk.vtkVolumeProperty()
    volumeProperty.SetColor(colorTransferFunction)
    volumeProperty.SetScalarOpacity(opacityTransferFunction)
    volumeProperty.ShadeOn()
    volumeProperty.SetInterpolationTypeToLinear()
    
    # The mapper / ray cast function know how to render the data
    compositeFunction = vtk.vtkVolumeRayCastCompositeFunction()
    volumeMapper = vtk.vtkVolumeRayCastMapper()
    volumeMapper.SetVolumeRayCastFunction(compositeFunction)
    volumeMapper.SetInputConnection(reader.GetOutputPort())
    volumeMapper.SetSampleDistance(0.1)
    print "sample distance: %f"%volumeMapper.GetSampleDistance()

    # The volume holds the mapper and the property and
    # can be used to position/orient the volume
    volume = vtk.vtkVolume()
    volume.SetMapper(volumeMapper)
    volume.SetProperty(volumeProperty)

    ren.AddVolume(volume)
    ren.SetBackground(0, 0, 0)

    ren.GetActiveCamera().SetViewUp(-0.033792287793636924, 0.000854723562570334, -0.9994285120674231)
    ren.GetActiveCamera().SetPosition(-308.155681140229, -119.92183136577268, 117.3094068139949 )
    ren.GetActiveCamera().SetFocalPoint(91.14654767513275, 104.1683804243803, 104.0)
    ren.GetActiveCamera().SetClippingRange(191.00826351112892, 795.369621458024)
    
    renWin.SetSize(1600, 900)
    renWin.Render()
    
    renWin.AddObserver("AbortCheckEvent", CheckAbort)

    iren.Initialize()
    renWin.Render()
    iren.Start()

if __name__=="__main__":
    Main()