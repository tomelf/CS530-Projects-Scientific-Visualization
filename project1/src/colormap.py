#!/usr/bin/env python

import sys
import vtk
from vtk import vtkScalarBarActor, vtkTextProperty

# Callback function for vtkSliderWidgets
def vtkSliderCallback1(obj, event):
    sliderRepres1 = obj.GetRepresentation()
    pos = sliderRepres1.GetValue()
    global colorVar1
    lut.RemovePoint(colorVar1)
    colorVar1 = pos
    lut.AddRGBPoint(colorVar1,0,0.25,0.5);

def vtkSliderCallback2(obj, event):
    sliderRepres2 = obj.GetRepresentation()
    pos = sliderRepres2.GetValue()
    global colorVar2
    lut.RemovePoint(colorVar2)
    colorVar2 = pos
    lut.AddRGBPoint(colorVar2,1,1,0.5);

# Load bathymetry dataset
bathymetryReader = vtk.vtkStructuredPointsReader()
bathymetryReader.SetFileName(sys.argv[1])

colorVar1 = -4500
colorVar2 = 2000

# Setup color mapping
lut = vtk.vtkColorTransferFunction()
lut.SetColorSpaceToRGB()
lut.AddRGBPoint(-9000,0,0,0);
lut.AddRGBPoint(colorVar1,0,0.25,0.5);
lut.AddRGBPoint(-1,0,1,1);
lut.AddRGBPoint(0,0.25,0.75,0);
lut.AddRGBPoint(colorVar2,1,1,0.5);
lut.AddRGBPoint(4000,1,1,1);

# Load bathymetry data into Geometry Filter
geometry = vtk.vtkImageDataGeometryFilter()
geometry.SetInputConnection(bathymetryReader.GetOutputPort())

mapper = vtk.vtkDataSetMapper()
mapper.SetInputConnection(geometry.GetOutputPort())
mapper.SetLookupTable(lut)
mapper.SetScalarRange(0, 255)
mapper.ImmediateModeRenderingOff()

# Setup color mapping bar
colorBar = vtkScalarBarActor()
colorBar.SetLookupTable(mapper.GetLookupTable())
colorBar.SetTitle("color map")
colorBar.SetNumberOfLabels(6)
colorBar.SetLabelFormat("%6.0f")
colorBar.SetPosition(0.89, 0.1)
colorBar.SetWidth(0.08)
colorBar.SetHeight(0.7)

actor = vtk.vtkActor()
actor.SetMapper(mapper)

# Create renderer stuff
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Add the actors to the renderer, set the background and size
ren.AddActor(actor)
ren.AddActor(colorBar)
ren.ResetCamera()
ren.SetBackground(0.1, 0.2, 0.4)
ren.ResetCameraClippingRange()
renWin.SetSize(800, 600)

# Add vtkSliderWidget
SliderRepres1 = vtk.vtkSliderRepresentation2D()
min = -8999 #ImageViewer.GetSliceMin()
max = -2 #ImageViewer.GetSliceMax()
SliderRepres1.SetMinimumValue(min)
SliderRepres1.SetMaximumValue(max)
SliderRepres1.SetValue(-4500)
SliderRepres1.SetTitleText("negetive scale")
SliderRepres1.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
SliderRepres1.GetPoint1Coordinate().SetValue(0.5, 0.2)
SliderRepres1.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
SliderRepres1.GetPoint2Coordinate().SetValue(0.8, 0.2)
SliderRepres1.SetSliderLength(0.02)
SliderRepres1.SetSliderWidth(0.03)
SliderRepres1.SetEndCapLength(0.01)
SliderRepres1.SetEndCapWidth(0.03)
SliderRepres1.SetTubeWidth(0.005)
SliderRepres1.SetLabelFormat("%3.0lf")
SliderRepres1.SetTitleHeight(0.02)
SliderRepres1.SetLabelHeight(0.02)
SliderWidget1 = vtk.vtkSliderWidget()
SliderWidget1.SetInteractor(iren)
SliderWidget1.SetRepresentation(SliderRepres1)
SliderWidget1.KeyPressActivationOff()
SliderWidget1.SetAnimationModeToAnimate()
SliderWidget1.SetEnabled(True)
SliderWidget1.AddObserver("InteractionEvent", vtkSliderCallback1)

# Add vtkSliderWidget
SliderRepres2 = vtk.vtkSliderRepresentation2D()
min = 1 #ImageViewer.GetSliceMin()
max = 3999 #ImageViewer.GetSliceMax()
SliderRepres2.SetMinimumValue(min)
SliderRepres2.SetMaximumValue(max)
SliderRepres2.SetValue(2000)
SliderRepres2.SetTitleText("positive scale")
SliderRepres2.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
SliderRepres2.GetPoint1Coordinate().SetValue(0.5, 0.1)
SliderRepres2.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
SliderRepres2.GetPoint2Coordinate().SetValue(0.8, 0.1)
SliderRepres2.SetSliderLength(0.02)
SliderRepres2.SetSliderWidth(0.03)
SliderRepres2.SetEndCapLength(0.01)
SliderRepres2.SetEndCapWidth(0.03)
SliderRepres2.SetTubeWidth(0.005)
SliderRepres2.SetLabelFormat("%3.0lf")
SliderRepres2.SetTitleHeight(0.02)
SliderRepres2.SetLabelHeight(0.02)
SliderWidget2 = vtk.vtkSliderWidget()
SliderWidget2.SetInteractor(iren)
SliderWidget2.SetRepresentation(SliderRepres2)
SliderWidget2.KeyPressActivationOff()
SliderWidget2.SetAnimationModeToAnimate()
SliderWidget2.SetEnabled(True)
SliderWidget2.AddObserver("InteractionEvent", vtkSliderCallback2)

iren.Initialize()
renWin.Render()
iren.Start()
