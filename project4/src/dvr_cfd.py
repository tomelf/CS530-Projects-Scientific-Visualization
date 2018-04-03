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
                  [0,0.66,0,1,0],
                  [900,0.66,0.1,1,0.009],
                  [10000,0.66,0.3,1,0.01],
                  [20000,0.66,0.5,1,0.3],
                  [30000,0.66,1,1,1]
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
    
    ren.GetActiveCamera().SetViewUp(0.2320640509325283, 0.6216278154231228, 0.748147803149258)
    ren.GetActiveCamera().SetPosition(-86.30842917477719, -55.80182530081589, 297.63908735650085)
    ren.GetActiveCamera().SetFocalPoint(199.18608617782593, 149.5, 38.5)
    ren.GetActiveCamera().SetClippingRange(4.197001562269691, 982.4499004768599)
    
    renWin.SetSize(1600, 900)
    renWin.Render()
    
    renWin.AddObserver("AbortCheckEvent", CheckAbort)
    
    iren.Initialize()
    renWin.Render()
    iren.Start()

if __name__=="__main__":
    Main()