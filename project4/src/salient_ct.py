#!/usr/bin/env python

import sys
import vtk
import os
from vtk import vtkScalarBarActor

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

def Main():
    global ren
    print "data: %s" % sys.argv[1]
    reader = vtk.vtkStructuredPointsReader()
    reader.SetFileName(sys.argv[1])
    
    isosurfaces = [
                   [500,0.1,0.3,1,0.3],
                   [1158,0.1,0.6,1,0.5],
                   [2750,0.1,1,1,1]
                   ]
    
    ren = vtk.vtkRenderer()
    
    for surface in isosurfaces:
    
        lut = vtk.vtkColorTransferFunction()
        lut.SetColorSpaceToHSV()
        lut.AddHSVPoint(surface[0],surface[1],surface[2],surface[3])
    
        contours = vtk.vtkContourFilter()
        contours.SetInputConnection(reader.GetOutputPort());
        contours.ComputeNormalsOn()

        contours.SetValue(0, surface[0])
    
        mapper = vtk.vtkDataSetMapper()
        mapper.SetInputConnection(contours.GetOutputPort())
        mapper.SetLookupTable(lut)
        mapper.ImmediateModeRenderingOff()

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetOpacity(surface[4])

        ren.AddActor(actor)

    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    iren.RemoveObservers('RightButtonPressEvent')
    iren.AddObserver('RightButtonPressEvent', print_camera_settings, 1.0)
    iren.AddObserver('RightButtonPressEvent', after_print_camera_settings, -1.0)

    # for depth peeling
    ren.SetUseDepthPeeling(1)
    ren.SetMaximumNumberOfPeels(4) # default 4
    ren.SetOcclusionRatio(0) # default 0
    
    ren.ResetCamera()
    ren.SetBackground(0,0,0)
    ren.ResetCameraClippingRange()
    
    ren.GetActiveCamera().SetViewUp(-0.033792287793636924, 0.000854723562570334, -0.9994285120674231)
    ren.GetActiveCamera().SetPosition(-308.155681140229, -119.92183136577268, 117.3094068139949 )
    ren.GetActiveCamera().SetFocalPoint(91.14654767513275, 104.1683804243803, 104.0)
    ren.GetActiveCamera().SetClippingRange(191.00826351112892, 795.369621458024)
    
    # for depth peeling
    renWin.SetAlphaBitPlanes(1)
    renWin.SetMultiSamples(0)

    renWin.SetSize(1600, 900)

    # Render
    iren.Initialize()
    renWin.Render()
    iren.Start()

if __name__=="__main__":
    Main()