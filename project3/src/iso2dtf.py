#!/usr/bin/env python

import sys
import re
import vtk
from vtk import vtkScalarBarActor

def isovalueSliderHandler(obj, event):
    global isovalue, contours
    isovalue = obj.GetRepresentation().GetValue()
    contours.SetValue(0, isovalue)
    print "Change Isovalue: %f"%isovalue

def gminSliderHandler(obj, event):
    global gmin, gmax, gminSlider, gmclipper1
    gmin = obj.GetRepresentation().GetValue()
    if gmin>=gmax:
        gmin = gmax-1
        gminSlider.SetValue(gmin)
        
    gmclipper1.SetValue(gmin)
    gmclipper1.Update()
    print "gmin: %f, gmax: %f"%(gmin,gmax)

def gmaxSliderHandler(obj, event):
    global gmin, gmax, gmaxSlider, gmclipper2
    gmax = obj.GetRepresentation().GetValue()
    if gmin>=gmax:
        gmax = gmin+1
        gmaxSlider.SetValue(gmax)
        
    gmclipper2.SetValue(gmax)
    gmclipper2.Update()
    print "gmin: %f, gmax: %f"%(gmin,gmax)

def clipXSliderHandler(obj, event):
    global clipX
    clipX = obj.GetRepresentation().GetValue()
    updateCT()

def clipYSliderHandler(obj, event):
    global clipY
    clipY = obj.GetRepresentation().GetValue()
    updateCT()

def clipZSliderHandler(obj, event):
    global clipZ
    clipZ = obj.GetRepresentation().GetValue()
    updateCT()

def updateCT():
    global clipX, clipY, clipZ, plane1, plane2, plane3, planeSource1, planeSource2, planeSource3, clipper1, clipper2, clipper3
    planeSource1.SetOrigin(clipX,0,0)
    planeSource2.SetOrigin(0,clipY,0)
    planeSource3.SetOrigin(0,0,clipZ)
    plane1.SetOrigin(planeSource1.GetOrigin())
    plane2.SetOrigin(planeSource2.GetOrigin())
    plane3.SetOrigin(planeSource3.GetOrigin())
    clipper1.Update()
    clipper2.Update()
    clipper3.Update()
    print "clip (%f,%f,%f)" %(clipX,clipY,clipZ)

def Main():
    global isovalue, contours, planeSource1, planeSource2, planeSource3, plane1, plane2, plane3, clipper1, clipper2, clipper3, clipX, clipY, clipZ, lut, gmin, gmax, min, max, gminSlider, gmaxSlider, gmclipper1, gmclipper2

    print "data: %s" % sys.argv[1]
    reader = vtk.vtkStructuredPointsReader()
    reader.SetFileName(sys.argv[1])
    reader.Update()
    
    print "gradientmag: %s" % sys.argv[2]
    gmreader = vtk.vtkStructuredPointsReader()
    gmreader.SetFileName(sys.argv[2])
    gmreader.Update()
    
    clipX = 0
    clipY = 0
    clipZ = 0
    
    r = reader.GetOutput().GetScalarRange()
    datamin = r[0]
    datamax = r[1]
    isovalue = (datamax+datamin)/2.0

    for i in range(3, len(sys.argv)):
        if sys.argv[i] == "--val":
            print "isovalue %s" % sys.argv[i+1]
            isovalue = float(sys.argv[i+1])
        if sys.argv[i] == "--clip":
            print "clip (%s,%s,%s)" % (sys.argv[i+1],sys.argv[i+2],sys.argv[i+3])
            clipX = float(sys.argv[i+1])
            clipY = float(sys.argv[i+2])
            clipZ = float(sys.argv[i+3])
    
    contours = vtk.vtkContourFilter()
    contours.SetInputConnection(reader.GetOutputPort());
    contours.ComputeNormalsOn()
    contours.SetValue(0, isovalue)

    planeSource1 = vtk.vtkPlaneSource()
    planeSource1.SetNormal(1,0,0)
    planeSource1.SetOrigin(clipX,0,0)
    planeSource2 = vtk.vtkPlaneSource()
    planeSource2.SetNormal(0,1,0)
    planeSource2.SetOrigin(0,clipY,0)
    planeSource3 = vtk.vtkPlaneSource()
    planeSource3.SetNormal(0,0,1)
    planeSource3.SetOrigin(0,0,clipZ)

    plane1 = vtk.vtkPlane()
    plane1.SetNormal(planeSource1.GetNormal())
    plane1.SetOrigin(planeSource1.GetOrigin())
    clipper1 = vtk.vtkClipPolyData()
    clipper1.SetClipFunction(plane1)
    clipper1.SetInputConnection(contours.GetOutputPort())
    clipper1.Update()

    plane2 = vtk.vtkPlane()
    plane2.SetNormal(planeSource2.GetNormal())
    plane2.SetOrigin(planeSource2.GetOrigin())
    clipper2 = vtk.vtkClipPolyData()
    clipper2.SetClipFunction(plane2)
    clipper2.SetInputConnection(clipper1.GetOutputPort())
    clipper2.Update()

    plane3 = vtk.vtkPlane()
    plane3.SetNormal(planeSource3.GetNormal())
    plane3.SetOrigin(planeSource3.GetOrigin())
    clipper3 = vtk.vtkClipPolyData()
    clipper3.SetClipFunction(plane3)
    clipper3.SetInputConnection(clipper2.GetOutputPort())
    clipper3.Update()

    probeFilter = vtk.vtkProbeFilter()
    probeFilter.SetInputConnection(0, clipper3.GetOutputPort())
    probeFilter.SetInputConnection(1, gmreader.GetOutputPort())
    probeFilter.Update()

    gmrange = probeFilter.GetOutput().GetScalarRange()
    gmin = gmrange[0]
    gmax = gmrange[1]
    
    gmclipper1 = vtk.vtkClipPolyData()
    gmclipper1.SetInputConnection(probeFilter.GetOutputPort())
    gmclipper1.InsideOutOff()
    gmclipper1.SetValue(int(gmin))
    gmclipper1.Update()

    gmclipper2 = vtk.vtkClipPolyData()
    gmclipper2.SetInputConnection(gmclipper1.GetOutputPort())
    gmclipper2.InsideOutOn()
    gmclipper2.SetValue(int(gmax))
    gmclipper2.Update()

    # display the data in rainbow color scale
    lut = vtk.vtkColorTransferFunction()
    lut.SetColorSpaceToHSV()
    lut.RemoveAllPoints()
    dis = (gmax-gmin)/7
    for i in range(0,8):
        lut.AddHSVPoint(gmin+dis*i,0.1*i,1,1)

    clipperMapper = vtk.vtkPolyDataMapper()
    clipperMapper.SetLookupTable(lut)
    clipperMapper.SetInputConnection(gmclipper2.GetOutputPort())

    colorBar = vtkScalarBarActor()
    colorBar.SetLookupTable(clipperMapper.GetLookupTable())
    colorBar.SetTitle("gradient magnitude ")
    colorBar.SetNumberOfLabels(6)
    colorBar.SetLabelFormat("%4.0f")
    colorBar.SetPosition(0.9, 0.1)
    colorBar.SetWidth(0.1)
    colorBar.SetHeight(0.7)

    clipperActor=vtk.vtkActor()
    clipperActor.GetProperty().SetRepresentationToWireframe()
    clipperActor.SetMapper(clipperMapper)

    backFaces = vtk.vtkProperty()
    backFaces.SetSpecular(0)
    backFaces.SetDiffuse(0)
    backFaces.SetAmbient(0)
    backFaces.SetAmbientColor(1,0,0)
    clipperActor.SetBackfaceProperty(backFaces)

    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    ren.AddActor(clipperActor)
    ren.AddActor(colorBar)
    ren.ResetCamera()
    ren.SetBackground(0.2,0.3,0.4)
    ren.ResetCameraClippingRange()
    renWin.SetSize(1200, 600)

    gminSlider = vtk.vtkSliderRepresentation2D()
    gminSlider.SetMinimumValue(gmrange[0])
    gminSlider.SetMaximumValue(gmrange[1])
    gminSlider.SetValue(gmin)
    gminSlider.SetTitleText("gradmin")
    gminSlider.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    gminSlider.GetPoint1Coordinate().SetValue(0.0, 0.6)
    gminSlider.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    gminSlider.GetPoint2Coordinate().SetValue(0.2, 0.6)
    gminSlider.SetSliderLength(0.02)
    gminSlider.SetSliderWidth(0.03)
    gminSlider.SetEndCapLength(0.01)
    gminSlider.SetEndCapWidth(0.03)
    gminSlider.SetTubeWidth(0.005)
    gminSlider.SetLabelFormat("%3.0lf")
    gminSlider.SetTitleHeight(0.02)
    gminSlider.SetLabelHeight(0.02)
    gminSliderWidget = vtk.vtkSliderWidget()
    gminSliderWidget.SetInteractor(iren)
    gminSliderWidget.SetRepresentation(gminSlider)
    gminSliderWidget.KeyPressActivationOff()
    gminSliderWidget.SetAnimationModeToAnimate()
    gminSliderWidget.SetEnabled(True)
    gminSliderWidget.AddObserver("InteractionEvent", gminSliderHandler)

    gmaxSlider = vtk.vtkSliderRepresentation2D()
    gmaxSlider.SetMinimumValue(gmrange[0])
    gmaxSlider.SetMaximumValue(gmrange[1])
    gmaxSlider.SetValue(gmax)
    gmaxSlider.SetTitleText("gradmax")
    gmaxSlider.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    gmaxSlider.GetPoint1Coordinate().SetValue(0.0, 0.5)
    gmaxSlider.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    gmaxSlider.GetPoint2Coordinate().SetValue(0.2, 0.5)
    gmaxSlider.SetSliderLength(0.02)
    gmaxSlider.SetSliderWidth(0.03)
    gmaxSlider.SetEndCapLength(0.01)
    gmaxSlider.SetEndCapWidth(0.03)
    gmaxSlider.SetTubeWidth(0.005)
    gmaxSlider.SetLabelFormat("%3.0lf")
    gmaxSlider.SetTitleHeight(0.02)
    gmaxSlider.SetLabelHeight(0.02)
    gmaxSliderWidget = vtk.vtkSliderWidget()
    gmaxSliderWidget.SetInteractor(iren)
    gmaxSliderWidget.SetRepresentation(gmaxSlider)
    gmaxSliderWidget.KeyPressActivationOff()
    gmaxSliderWidget.SetAnimationModeToAnimate()
    gmaxSliderWidget.SetEnabled(True)
    gmaxSliderWidget.AddObserver("InteractionEvent", gmaxSliderHandler)
    
    isovalueSlider = vtk.vtkSliderRepresentation2D()
    isovalueSlider.SetMinimumValue(datamin)
    isovalueSlider.SetMaximumValue(datamax)
    isovalueSlider.SetValue(isovalue)
    isovalueSlider.SetTitleText("isovalue")
    isovalueSlider.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    isovalueSlider.GetPoint1Coordinate().SetValue(0.0, 0.4)
    isovalueSlider.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    isovalueSlider.GetPoint2Coordinate().SetValue(0.2, 0.4)
    isovalueSlider.SetSliderLength(0.02)
    isovalueSlider.SetSliderWidth(0.03)
    isovalueSlider.SetEndCapLength(0.01)
    isovalueSlider.SetEndCapWidth(0.03)
    isovalueSlider.SetTubeWidth(0.005)
    isovalueSlider.SetLabelFormat("%3.0lf")
    isovalueSlider.SetTitleHeight(0.02)
    isovalueSlider.SetLabelHeight(0.02)
    SliderWidget1 = vtk.vtkSliderWidget()
    SliderWidget1.SetInteractor(iren)
    SliderWidget1.SetRepresentation(isovalueSlider)
    SliderWidget1.KeyPressActivationOff()
    SliderWidget1.SetAnimationModeToAnimate()
    SliderWidget1.SetEnabled(True)
    SliderWidget1.AddObserver("InteractionEvent", isovalueSliderHandler)

    isovalueSlider = vtk.vtkSliderRepresentation2D()
    isovalueSlider.SetMinimumValue(datamin)
    isovalueSlider.SetMaximumValue(datamax)
    isovalueSlider.SetValue(isovalue)
    isovalueSlider.SetTitleText("isovalue")
    isovalueSlider.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    isovalueSlider.GetPoint1Coordinate().SetValue(0.0, 0.4)
    isovalueSlider.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    isovalueSlider.GetPoint2Coordinate().SetValue(0.2, 0.4)
    isovalueSlider.SetSliderLength(0.02)
    isovalueSlider.SetSliderWidth(0.03)
    isovalueSlider.SetEndCapLength(0.01)
    isovalueSlider.SetEndCapWidth(0.03)
    isovalueSlider.SetTubeWidth(0.005)
    isovalueSlider.SetLabelFormat("%3.0lf")
    isovalueSlider.SetTitleHeight(0.02)
    isovalueSlider.SetLabelHeight(0.02)
    SliderWidget1 = vtk.vtkSliderWidget()
    SliderWidget1.SetInteractor(iren)
    SliderWidget1.SetRepresentation(isovalueSlider)
    SliderWidget1.KeyPressActivationOff()
    SliderWidget1.SetAnimationModeToAnimate()
    SliderWidget1.SetEnabled(True)
    SliderWidget1.AddObserver("InteractionEvent", isovalueSliderHandler)

    clipXSlider = vtk.vtkSliderRepresentation2D()
    clipXSlider.SetMinimumValue(0)
    clipXSlider.SetMaximumValue(300)
    clipXSlider.SetValue(clipX)
    clipXSlider.SetTitleText("X")
    clipXSlider.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    clipXSlider.GetPoint1Coordinate().SetValue(0.0, 0.3)
    clipXSlider.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    clipXSlider.GetPoint2Coordinate().SetValue(0.2, 0.3)
    clipXSlider.SetSliderLength(0.02)
    clipXSlider.SetSliderWidth(0.03)
    clipXSlider.SetEndCapLength(0.01)
    clipXSlider.SetEndCapWidth(0.03)
    clipXSlider.SetTubeWidth(0.005)
    clipXSlider.SetLabelFormat("%1.2lf")
    clipXSlider.SetTitleHeight(0.02)
    clipXSlider.SetLabelHeight(0.02)
    SliderWidget2 = vtk.vtkSliderWidget()
    SliderWidget2.SetInteractor(iren)
    SliderWidget2.SetRepresentation(clipXSlider)
    SliderWidget2.KeyPressActivationOff()
    SliderWidget2.SetAnimationModeToAnimate()
    SliderWidget2.SetEnabled(True)
    SliderWidget2.AddObserver("InteractionEvent", clipXSliderHandler)

    clipYSlider = vtk.vtkSliderRepresentation2D()
    clipYSlider.SetMinimumValue(0)
    clipYSlider.SetMaximumValue(300)
    clipYSlider.SetValue(clipY)
    clipYSlider.SetTitleText("Y")
    clipYSlider.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    clipYSlider.GetPoint1Coordinate().SetValue(0.0, 0.2)
    clipYSlider.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    clipYSlider.GetPoint2Coordinate().SetValue(0.2, 0.2)
    clipYSlider.SetSliderLength(0.02)
    clipYSlider.SetSliderWidth(0.03)
    clipYSlider.SetEndCapLength(0.01)
    clipYSlider.SetEndCapWidth(0.03)
    clipYSlider.SetTubeWidth(0.005)
    clipYSlider.SetLabelFormat("%1.2lf")
    clipYSlider.SetTitleHeight(0.02)
    clipYSlider.SetLabelHeight(0.02)
    SliderWidget3 = vtk.vtkSliderWidget()
    SliderWidget3.SetInteractor(iren)
    SliderWidget3.SetRepresentation(clipYSlider)
    SliderWidget3.KeyPressActivationOff()
    SliderWidget3.SetAnimationModeToAnimate()
    SliderWidget3.SetEnabled(True)
    SliderWidget3.AddObserver("InteractionEvent", clipYSliderHandler)

    clipZSlider = vtk.vtkSliderRepresentation2D()
    clipZSlider.SetMinimumValue(0)
    clipZSlider.SetMaximumValue(300)
    clipZSlider.SetValue(clipZ)
    clipZSlider.SetTitleText("Z")
    clipZSlider.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    clipZSlider.GetPoint1Coordinate().SetValue(0.0, 0.1)
    clipZSlider.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    clipZSlider.GetPoint2Coordinate().SetValue(0.2, 0.1)
    clipZSlider.SetSliderLength(0.02)
    clipZSlider.SetSliderWidth(0.03)
    clipZSlider.SetEndCapLength(0.01)
    clipZSlider.SetEndCapWidth(0.03)
    clipZSlider.SetTubeWidth(0.005)
    clipZSlider.SetLabelFormat("%1.2lf")
    clipZSlider.SetTitleHeight(0.02)
    clipZSlider.SetLabelHeight(0.02)
    SliderWidget4 = vtk.vtkSliderWidget()
    SliderWidget4.SetInteractor(iren)
    SliderWidget4.SetRepresentation(clipZSlider)
    SliderWidget4.KeyPressActivationOff()
    SliderWidget4.SetAnimationModeToAnimate()
    SliderWidget4.SetEnabled(True)
    SliderWidget4.AddObserver("InteractionEvent", clipZSliderHandler)

    # Render
    iren.Initialize()
    renWin.Render()
    iren.Start()

if __name__=="__main__":
    Main()