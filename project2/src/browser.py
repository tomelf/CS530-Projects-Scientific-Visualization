#!/usr/bin/env python

import sys
import vtk
from vtk import vtkScalarBarActor, vtkTextProperty

# Callback function for vtkSliderWidgets
def vminSliderHandler(obj, event):
    sliderRepres1 = obj.GetRepresentation()
    pos = sliderRepres1.GetValue()
    global vmin
    vmin = pos
    if vmin>=vmax-1:
        vmin = vmax-1
    updateUI()

def vmaxSliderHandler(obj, event):
    sliderRepres2 = obj.GetRepresentation()
    pos = sliderRepres2.GetValue()
    global vmax
    vmax = pos
    if vmax<=vmin+1:
        vmax = vmin+1
    updateUI()

def wSliderHandler(obj, event):
    sliderRepres3 = obj.GetRepresentation()
    pos = sliderRepres3.GetValue()
    global w_value
    w_value = pos

    if w_value + vmax >= datamax-1:
        w_value = datamax-1-vmax
    if vmin - w_value <= datamin+1:
        w_value = vmin-datamin-1

    updateUI()

def updateUI():
    global vmin, vmax, w_value, lut, SliderRepres1, SliderRepres2, SliderRepres3

    if vmax+w_value>=datamax-1:
        vmax = datamax-w_value-1
    if vmin+w_value>=datamax-2:
        vmin = datamax-w_value-2

    if vmax-w_value<=datamin+2:
        vmax = w_value+datamin+2
    if vmin-w_value<=datamin+1:
        vmin = w_value+datamin+1

    SliderRepres1.SetValue(vmin)
    SliderRepres2.SetValue(vmax)
    SliderRepres3.SetValue(w_value)

    lut.RemoveAllPoints()
    lut.AddHSVPoint(datamin,0,0,0)
    lut.AddHSVPoint(vmin,0,1,1)
    lut.AddHSVPoint(vmax,0,1,1)
    lut.AddHSVPoint(datamax,0,0,1)
    lut.AddHSVPoint(vmin-w_value,0,0,(vmin-w_value-datamin)/(datamax-datamin))
    lut.AddHSVPoint(vmax+w_value,0,0,(vmax+w_value-datamin)/(datamax-datamin))
    
def Main():
    global vmin, vmax, w_value, datamin, datamax, lut, SliderRepres1, SliderRepres2, SliderRepres3
    # Load bathymetry dataset
    bathymetryReader = vtk.vtkStructuredPointsReader()
    bathymetryReader.SetFileName(sys.argv[1])
    bathymetryReader.Update()
    r = bathymetryReader.GetOutput().GetPointData().GetScalars().GetRange()

    datamin = r[0]
    datamax = r[1]

    vmin = datamin + (datamax-datamin)*0.4
    vmax = datamin + (datamax-datamin)*0.6
    w_value = (datamax-datamin)/20

    # Setup color mapping
    lut = vtk.vtkColorTransferFunction()
    lut.SetColorSpaceToHSV()

    # Load bathymetry data into Geometry Filter
    geometry = vtk.vtkImageDataGeometryFilter()
    geometry.SetInputConnection(bathymetryReader.GetOutputPort())

    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputConnection(geometry.GetOutputPort())
    mapper.SetLookupTable(lut)
    mapper.ImmediateModeRenderingOff()

    # Setup color mapping bar
    colorBar = vtkScalarBarActor()
    colorBar.SetLookupTable(mapper.GetLookupTable())
    colorBar.SetTitle("color map")
    colorBar.SetNumberOfLabels(6)
    colorBar.SetLabelFormat("%4.0f")
    colorBar.SetPosition(0.9, 0.1)
    colorBar.SetWidth(0.1)
    colorBar.SetHeight(0.7)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create renderer stuff
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()

    # Specify interaction with 2D image
    style = vtk.vtkInteractorStyleImage()
    style.SetInteractionModeToImage2D()
    iren.SetInteractorStyle(style)

    iren.SetRenderWindow(renWin)

    # Add the actors to the renderer, set the background and size
    ren.AddActor(actor)
    ren.AddActor(colorBar)
    ren.ResetCamera()
    ren.SetBackground(0, 0, 0)
    ren.ResetCameraClippingRange()
    renWin.SetSize(1280, 800)

    # Add vtkSliderWidget
    SliderRepres1 = vtk.vtkSliderRepresentation2D()
    min = datamin+1
    max = datamax-2
    SliderRepres1.SetMinimumValue(min)
    SliderRepres1.SetMaximumValue(max)
    SliderRepres1.SetTitleText("vmin")
    SliderRepres1.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    SliderRepres1.GetPoint1Coordinate().SetValue(0.1, 0.1)
    SliderRepres1.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    SliderRepres1.GetPoint2Coordinate().SetValue(0.3, 0.1)
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
    SliderWidget1.AddObserver("InteractionEvent", vminSliderHandler)

    # Add vtkSliderWidget
    SliderRepres2 = vtk.vtkSliderRepresentation2D()
    min = datamin+2
    max = datamax-1
    SliderRepres2.SetMinimumValue(min)
    SliderRepres2.SetMaximumValue(max)
    SliderRepres2.SetTitleText("vmax")
    SliderRepres2.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    SliderRepres2.GetPoint1Coordinate().SetValue(0.4, 0.1)
    SliderRepres2.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    SliderRepres2.GetPoint2Coordinate().SetValue(0.6, 0.1)
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
    SliderWidget2.AddObserver("InteractionEvent", vmaxSliderHandler)

    # Add vtkSliderWidget
    SliderRepres3 = vtk.vtkSliderRepresentation2D()
    min = 1
    max = (datamax-datamin)/10
    SliderRepres3.SetMinimumValue(min)
    SliderRepres3.SetMaximumValue(max)
    SliderRepres3.SetTitleText("w")
    SliderRepres3.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
    SliderRepres3.GetPoint1Coordinate().SetValue(0.7, 0.1)
    SliderRepres3.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
    SliderRepres3.GetPoint2Coordinate().SetValue(0.9, 0.1)
    SliderRepres3.SetSliderLength(0.02)
    SliderRepres3.SetSliderWidth(0.03)
    SliderRepres3.SetEndCapLength(0.01)
    SliderRepres3.SetEndCapWidth(0.03)
    SliderRepres3.SetTubeWidth(0.005)
    SliderRepres3.SetLabelFormat("%3.0lf")
    SliderRepres3.SetTitleHeight(0.02)
    SliderRepres3.SetLabelHeight(0.02)
    SliderWidget3 = vtk.vtkSliderWidget()
    SliderWidget3.SetInteractor(iren)
    SliderWidget3.SetRepresentation(SliderRepres3)
    SliderWidget3.KeyPressActivationOff()
    SliderWidget3.SetAnimationModeToAnimate()
    SliderWidget3.SetEnabled(True)
    SliderWidget3.AddObserver("InteractionEvent", wSliderHandler)

    updateUI()

    iren.Initialize()
    renWin.Render()
    iren.Start()

if __name__=="__main__":
    Main()