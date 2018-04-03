#!/usr/bin/env python

import sys
import re
import vtk
from vtk import vtkScalarBarActor

continuousType = "HSV"
discreateType = "HSV"
continuousSize = 0
discreateSize = 0
continuousData = []
discreteData = []

def loadContinuousFile(filename):
    global continuousType, continuousSize
    f = open(filename, "r")
    first_flag = True
    for line in f:
        line = line.lstrip()
        if line[0] != '#' and first_flag:
            first_flag = False
            
            m = re.match('(\d+)[ \t]*([A-Za-z]+)', line)
            if m:
                continuousSize = m.group(1)
                continuousType = m.group(2)
    
        elif line[0] != '#' and not first_flag:
            m = re.match('([-\./\d]+)[ \t]*([-\./\d]+)[ \t]*([-\./\d]+)[ \t]*([-\./\d]+)', line)
            if m:
                continuousData.append([m.group(1), m.group(2), m.group(3), m.group(4)])
    f.close()

def loadDiscreteFile(filename):
    global discreateType, discreateSize
    f = open(filename, "r")
    first_flag = True
    for line in f:
        line = line.lstrip()
        if line[0] != '#' and first_flag:
            first_flag = False
            m = re.match('(\d+)[ \t]*([A-Za-z]+)', line)
            if m:
                discreateSize = m.group(1)
                discreateType = m.group(2)
    
        elif line[0] != '#' and not first_flag:
            m = re.match('([-\./\d]+)[ \t]*([-\./\d]+)[ \t]*([-\./\d]+)[ \t]*([-\./\d]+)', line)
            if m:
                discreteData.append([m.group(1), m.group(2), m.group(3), m.group(4)])
    f.close()

def loadIsovalueFile(filename):
    f = open(filename, "r")
    isovalues = []
    for line in f:
        isovalues.append(float(line.strip()))
    f.close()
    
    return isovalues

def updateUI(mode=0):
    lut.RemoveAllPoints()
    print "[Color Map]"
    if mode==0: #continuous
        print continuousType
        if continuousType == "HSV":
            lut.SetColorSpaceToHSV()
            for p in continuousData:
                print p
                lut.AddHSVPoint(float(p[0]),float(p[1]),float(p[2]),float(p[3]),0.5,0)
        elif continuousType == "RGB":
            lut.SetColorSpaceToRGB()
            for p in continuousData:
                print p
                lut.AddRGBPoint(float(p[0]),float(p[1]),float(p[2]),float(p[3]),0.5,0)
    elif mode==1: #discrete
        print discreateType
        if discreateType == "HSV":
            lut.SetColorSpaceToHSV()
            for p in discreteData:
                print p
                lut.AddHSVPoint(float(p[0]),float(p[1]),float(p[2]),float(p[3]),0.5,1)
        elif discreateType == "RGB":
            lut.SetColorSpaceToRGB()
            for p in discreteData:
                print p
                lut.AddRGBPoint(float(p[0]),float(p[1]),float(p[2]),float(p[3]),0.5,1)

def showContinuous():
    updateUI(0)
    renWin.Render()

def showDiscrete():
    updateUI(1)
    renWin.Render()

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
    global isovalues, contours, planeSource1, planeSource2, planeSource3, plane1, plane2, plane3, clipper1, clipper2, clipper3, clipX, clipY, clipZ, lut, renWin

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
    
    print "isoval: %s" % sys.argv[3]
    isovalues = loadIsovalueFile(sys.argv[3])
    
    lut = vtk.vtkColorTransferFunction()
    lut.SetColorSpaceToHSV()
    lut.AddHSVPoint(0,0,1,1)
    
    for i in range(4, len(sys.argv)):
        if sys.argv[i] == "--cmap":
            print "colors file: %s" % sys.argv[i+1]
            loadContinuousFile(sys.argv[i+1])
            updateUI(0)
        if sys.argv[i] == "--clip":
            print "clip (%s,%s,%s)" % (sys.argv[i+1],sys.argv[i+2],sys.argv[i+3])
            clipX = float(sys.argv[i+1])
            clipY = float(sys.argv[i+2])
            clipZ = float(sys.argv[i+3])
    
    contours = vtk.vtkContourFilter()
    contours.SetInputConnection(reader.GetOutputPort());
    contours.ComputeNormalsOn()
                         
    for i in range(0, len(isovalues)):
        contours.SetValue(i, isovalues[i])

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

    clipperMapper = vtk.vtkPolyDataMapper()
    clipperMapper.SetLookupTable(lut)
    clipperMapper.SetInputConnection(probeFilter.GetOutputPort())
    clipperMapper.SetScalarRange(probeFilter.GetOutput().GetScalarRange())

    colorBar = vtkScalarBarActor()
    colorBar.SetLookupTable(clipperMapper.GetLookupTable())
    colorBar.SetTitle("gradient magnitude")
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