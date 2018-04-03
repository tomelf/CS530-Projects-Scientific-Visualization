#!/usr/bin/env python

import sys
import vtk

# Callback function for vtkSliderWidget
def vtkSliderCallback(obj, event):
    sliderRepres = obj.GetRepresentation()
    pos = sliderRepres.GetValue()
    warp.SetScaleFactor(pos/1000)

# Read in the image and bathymetry dataset.
imageReader = vtk.vtkJPEGReader()
imageReader.SetFileName(sys.argv[2])
bathymetryReader = vtk.vtkStructuredPointsReader()
bathymetryReader.SetFileName(sys.argv[1])

# Load bathymetry data into Geometry Filter
geometry = vtk.vtkImageDataGeometryFilter()
geometry.SetInputConnection(bathymetryReader.GetOutputPort())
warp = vtk.vtkWarpScalar()
warp.SetInputConnection(geometry.GetOutputPort())
warp.SetScaleFactor(0)

# Create texture object from satellite picture
texture = vtk.vtkTexture()
texture.SetInputConnection(imageReader.GetOutputPort())

# Create mapper
mapper = vtk.vtkDataSetMapper()
mapper.SetInputConnection(warp.GetOutputPort())
mapper.SetScalarRange(0, 255)
mapper.ScalarVisibilityOff()
mapper.ImmediateModeRenderingOff()

# Create actor and set the mapper and texture
actor = vtk.vtkActor()
actor.SetMapper(mapper)
actor.SetTexture(texture)

# Create renderer stuff
ren = vtk.vtkRenderer()
renWin = vtk.vtkRenderWindow()
renWin.AddRenderer(ren)
iren = vtk.vtkRenderWindowInteractor()
iren.SetRenderWindow(renWin)

# Add the actors to the renderer, set the background and size
ren.AddActor(actor)
ren.ResetCamera()
ren.SetBackground(0.1, 0.2, 0.4)

renWin.SetSize(800, 600)

# Add vtkSliderWidget
SliderRepres = vtk.vtkSliderRepresentation2D()
min = 0 #ImageViewer.GetSliceMin()
max = 100 #ImageViewer.GetSliceMax()
SliderRepres.SetMinimumValue(min)
SliderRepres.SetMaximumValue(max)
SliderRepres.SetValue(min)
SliderRepres.SetTitleText("scale factor")
SliderRepres.GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
SliderRepres.GetPoint1Coordinate().SetValue(0.1, 0.1)
SliderRepres.GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
SliderRepres.GetPoint2Coordinate().SetValue(0.4, 0.1)
SliderRepres.SetSliderLength(0.02)
SliderRepres.SetSliderWidth(0.03)
SliderRepres.SetEndCapLength(0.01)
SliderRepres.SetEndCapWidth(0.03)
SliderRepres.SetTubeWidth(0.005)
SliderRepres.SetLabelFormat("%3.0lf / 1000")
SliderRepres.SetTitleHeight(0.02)
SliderRepres.SetLabelHeight(0.02)
SliderWidget = vtk.vtkSliderWidget()
SliderWidget.SetInteractor(iren)
SliderWidget.SetRepresentation(SliderRepres)
SliderWidget.KeyPressActivationOff()
SliderWidget.SetAnimationModeToAnimate()
SliderWidget.SetEnabled(True)
SliderWidget.AddObserver("InteractionEvent", vtkSliderCallback)

iren.Initialize()
renWin.Render()
iren.Start()
