#!/usr/bin/env python

import sys
import re
import vtk
from vtk import vtkScalarBarActor

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
    global clipX, clipY, clipZ, plane1s, plane2s, plane3s, planeSource1s, planeSource2s, planeSource3s, clipper1s, clipper2s, clipper3s
    for i in range(0,len(clipper1s)):
        planeSource1s[i].SetOrigin(clipX,0,0)
        planeSource2s[i].SetOrigin(0,clipY,0)
        planeSource3s[i].SetOrigin(0,0,clipZ)
        plane1s[i].SetOrigin(planeSource1s[i].GetOrigin())
        plane2s[i].SetOrigin(planeSource2s[i].GetOrigin())
        plane3s[i].SetOrigin(planeSource3s[i].GetOrigin())
        clipper1s[i].Update()
        clipper2s[i].Update()
        clipper3s[i].Update()
    print "clip (%f,%f,%f)" %(clipX,clipY,clipZ)

def loadParamsFile(filename):
    global continuousType, continuousSize, continuousData
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
            m = re.match('([-\./\d]+)[ \t]*([-\./\d]+)[ \t]*([-\./\d]+)[ \t]*([-\./\d]+)[ \t]*([-\./\d]+)[ \t]*([-\./\d]+)[ \t]*([-\./\d]+)', line)
            if m:
                #<isovalue> <grad_min> <grad_max> <x> <y> <z> <alpha>
                continuousData.append(
                                      [float(m.group(1)),float(m.group(2)),float(m.group(3)),float(m.group(4)),
                                       float(m.group(5)),float(m.group(6)),float(m.group(7))]
                                      )
    f.close()

def Main():
    global continuousSize, continuousType, continuousData, contours, planeSource1s, planeSource2s, planeSource3s, plane1s, plane2s, plane3s, clipper1s, clipper2s, clipper3s, clipX, clipY, clipZ, lut

    print "data: %s" % sys.argv[1]
    reader = vtk.vtkStructuredPointsReader()
    reader.SetFileName(sys.argv[1])
    reader.Update()
    
    print "gradientmag: %s" % sys.argv[2]
    gmreader = vtk.vtkStructuredPointsReader()
    gmreader.SetFileName(sys.argv[2])
    gmreader.Update()
    
    continuousSize = 0
    continuousType = "HSV"
    continuousData = []
    
    print "params: %s" % sys.argv[3]
    loadParamsFile(sys.argv[3])
    
    clipX = 0
    clipY = 0
    clipZ = 0
    
    r = reader.GetOutput().GetScalarRange()
    datamin = r[0]
    datamax = r[1]

    for i in range(4, len(sys.argv)):
        if sys.argv[i] == "--clip":
            print "clip (%s,%s,%s)" % (sys.argv[i+1],sys.argv[i+2],sys.argv[i+3])
            clipX = float(sys.argv[i+1])
            clipY = float(sys.argv[i+2])
            clipZ = float(sys.argv[i+3])
    
    clipperActors = []
    planeSource1s = []
    planeSource2s = []
    planeSource3s = []
    plane1s = []
    plane2s = []
    plane3s = []
    clipper1s = []
    clipper2s = []
    clipper3s = []

    for i in range(0,len(continuousData)):
        contours = vtk.vtkContourFilter()
        contours.SetInputConnection(reader.GetOutputPort());
        contours.ComputeNormalsOn()
        contours.SetValue(0, float(continuousData[i][0]))

        planeSource1s.append(vtk.vtkPlaneSource())
        planeSource1s[i].SetNormal(1,0,0)
        planeSource1s[i].SetOrigin(clipX,0,0)
        plane1s.append(vtk.vtkPlane())
        plane1s[i].SetNormal(planeSource1s[i].GetNormal())
        plane1s[i].SetOrigin(planeSource1s[i].GetOrigin())
        clipper1s.append(vtk.vtkClipPolyData())
        clipper1s[i].SetClipFunction(plane1s[i])
        clipper1s[i].SetInputConnection(contours.GetOutputPort())
        clipper1s[i].Update()

        planeSource2s.append(vtk.vtkPlaneSource())
        planeSource2s[i].SetNormal(0,1,0)
        planeSource2s[i].SetOrigin(0,clipY,0)
        plane2s.append(vtk.vtkPlane())
        plane2s[i].SetNormal(planeSource2s[i].GetNormal())
        plane2s[i].SetOrigin(planeSource2s[i].GetOrigin())
        clipper2s.append(vtk.vtkClipPolyData())
        clipper2s[i].SetClipFunction(plane2s[i])
        clipper2s[i].SetInputConnection(clipper1s[i].GetOutputPort())
        clipper2s[i].Update()

        planeSource3s.append(vtk.vtkPlaneSource())
        planeSource3s[i].SetNormal(0,0,1)
        planeSource3s[i].SetOrigin(0,0,clipZ)
        plane3s.append(vtk.vtkPlane())
        plane3s[i].SetNormal(planeSource3s[i].GetNormal())
        plane3s[i].SetOrigin(planeSource3s[i].GetOrigin())
        clipper3s.append(vtk.vtkClipPolyData())
        clipper3s[i].SetClipFunction(plane3s[i])
        clipper3s[i].SetInputConnection(clipper2s[i].GetOutputPort())
        clipper3s[i].Update()

        probeFilter = vtk.vtkProbeFilter()
        probeFilter.SetInputConnection(0, clipper3s[i].GetOutputPort())
        probeFilter.SetInputConnection(1, gmreader.GetOutputPort())
        probeFilter.Update()

        gmrange = probeFilter.GetOutput().GetScalarRange()
        gmin = gmrange[0]
        gmax = gmrange[1]

        gmclipper1 = vtk.vtkClipPolyData()
        gmclipper1.SetInputConnection(probeFilter.GetOutputPort())
        gmclipper1.InsideOutOff()
        gmclipper1.SetValue(int(continuousData[i][1]))
        gmclipper1.Update()

        gmclipper2 = vtk.vtkClipPolyData()
        gmclipper2.SetInputConnection(gmclipper1.GetOutputPort())
        gmclipper2.InsideOutOn()
        gmclipper2.SetValue(int(continuousData[i][2]))
        gmclipper2.Update()

        lut = vtk.vtkColorTransferFunction()
        if continuousType == "HSV":
            lut.SetColorSpaceToHSV()
            p = continuousData[i]
            print "Color: %s"%p
            lut.AddHSVPoint(p[0],p[3],p[4],p[5])
        elif continuousType == "RGB":
            lut.SetColorSpaceToRGB()
            p = continuousData[i]
            print "Color: %s"%p
            lut.AddRGBPoint(p[0],p[3],p[4],p[5])

        clipperMapper = vtk.vtkPolyDataMapper()
        clipperMapper.SetLookupTable(lut)
        clipperMapper.SetInputConnection(gmclipper2.GetOutputPort())

        clipperActors.append(vtk.vtkActor())
        clipperActors[i].GetProperty().SetRepresentationToWireframe()
        clipperActors[i].SetMapper(clipperMapper)
        
        backFaces = vtk.vtkProperty()
        backFaces.SetSpecular(0)
        backFaces.SetDiffuse(0)
        backFaces.SetAmbient(0)
        backFaces.SetAmbientColor(1,0,0)
        clipperActors[i].SetBackfaceProperty(backFaces)

    lut_color = vtk.vtkColorTransferFunction()
    for d in continuousData:
        if continuousType == "HSV":
            lut_color.SetColorSpaceToHSV()
            lut_color.AddHSVPoint(d[0],d[3],d[4],d[5])
        elif continuousType == "RGB":
            lut_color.SetColorSpaceToRGB()
            lut_color.AddRGBPoint(d[0],d[3],d[4],d[5])

    colorMapper = vtk.vtkPolyDataMapper()
    colorMapper.SetLookupTable(lut_color)

    colorBar = vtkScalarBarActor()
    colorBar.SetLookupTable(colorMapper.GetLookupTable())
    colorBar.SetTitle("isovalue")
    colorBar.SetNumberOfLabels(6)
    colorBar.SetLabelFormat("%4.0f")
    colorBar.SetPosition(0.9, 0.1)
    colorBar.SetWidth(0.1)
    colorBar.SetHeight(0.7)

    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    for i in range(0,len(clipperActors)):
        clipperActors[i].GetProperty().SetOpacity(continuousData[i][6]) # load opacity for actor
        ren.AddActor(clipperActors[i])
    ren.AddActor(colorBar)

    # for depth peeling
    ren.SetUseDepthPeeling(1)
    ren.SetMaximumNumberOfPeels(2) # default 4
    ren.SetOcclusionRatio(0.1) # default 0

    ren.ResetCamera()
    ren.SetBackground(0.2,0.3,0.4)
    ren.ResetCameraClippingRange()

    # for depth peeling
    renWin.SetAlphaBitPlanes(1)
    renWin.SetMultiSamples(0)

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