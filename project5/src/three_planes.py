#!/usr/bin/env python

import sys
import vtk

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
    global ren, sliders, planes, planeCuts, origins
    # Create the RenderWindow, Renderer and both Actors
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.SetMultiSamples(0)
    renWin.AddRenderer(ren)
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)
    iren.RemoveObservers('RightButtonPressEvent')
    iren.AddObserver('RightButtonPressEvent', print_camera_settings, 1.0)
    iren.AddObserver('RightButtonPressEvent', after_print_camera_settings, -1.0)
    
    print "data: %s %s" % (sys.argv[1], sys.argv[2])
    
    cfdreader = vtk.vtkStructuredPointsReader()
    cfdreader.SetFileName(sys.argv[1])

    # setup wing data
    wingReader = vtk.vtkUnstructuredGridReader()
    wingReader.SetFileName(sys.argv[2])
    wingReader.Update()
    wingMapper = vtk.vtkDataSetMapper()
    wingMapper.SetInputConnection(wingReader.GetOutputPort())
    wingActor = vtk.vtkActor()
    wingActor.SetMapper(wingMapper)
    wingActor.GetProperty().SetColor(.4, .4, .4)
    
    planes = [
                vtk.vtkPlane(),
                vtk.vtkPlane(),
                vtk.vtkPlane()
                ]
    
    planeCuts = [
                 vtk.vtkCutter(),
                 vtk.vtkCutter(),
                 vtk.vtkCutter()
                 ]
    
    normals = [
               [1, 0, 0],
               [1, 0, 0],
               [1, 0, 0]
               ]
    origins = [
              [20, 0, 0],
              [100, 0, 0],
              [190, 0, 0]
              ]
    
    sliders = [
              vtk.vtkSliderRepresentation2D(),
              vtk.vtkSliderRepresentation2D(),
              vtk.vtkSliderRepresentation2D()
              ]
    
    sliderWidgets = [
                    vtk.vtkSliderWidget(),
                    vtk.vtkSliderWidget(),
                    vtk.vtkSliderWidget()
                    ]
    
    bPlaneToActor = [True, True, True]
    bWingToActor = True
    
    datamin = 0
    datamax = 230
    lut = vtk.vtkColorTransferFunction()
    lut.SetColorSpaceToHSV()
    lut.AddHSVPoint(datamin, 0, 1, 1)
    dis = (datamax - datamin) / 7
    for i in range(0, 8):
        lut.AddHSVPoint(datamin + dis * i, 0.1 * i, 1, 1)
    
    for i in range(0, len(planes)):
        planes[i].SetOrigin(origins[i])
        planes[i].SetNormal(normals[i])
        planeCuts[i].SetInputConnection(cfdreader.GetOutputPort())
        planeCuts[i].SetCutFunction(planes[i])
        
        arrowSource = vtk.vtkArrowSource()
        arrowSource.SetTipLength(0.3)
        arrowSource.SetShaftRadius(0.001)
        
        vectorGlyph = vtk.vtkGlyph3D()
        vectorGlyph.SetInputConnection(0, planeCuts[i].GetOutputPort())
        vectorGlyph.SetInputConnection(1, arrowSource.GetOutputPort())
        vectorGlyph.ScalingOn()
        vectorGlyph.SetScaleModeToScaleByVector()
        vectorGlyph.SetScaleFactor(0.35)
        vectorGlyph.OrientOn()
        vectorGlyph.ClampingOff()
        vectorGlyph.SetVectorModeToUseVector()
        vectorGlyph.SetIndexModeToOff()
        
        cutMapper = vtk.vtkDataSetMapper()
        cutMapper.SetLookupTable(lut)
        cutMapper.SetScalarRange(vectorGlyph.GetRange())
        cutMapper.SetInputConnection(vectorGlyph.GetOutputPort())
        
        cutActor = vtk.vtkActor()
        cutActor.SetMapper(cutMapper)
        cutActor.GetProperty().SetOpacity(0.4);
        cutActor.GetProperty().SetColor(0, 1, 0)
        
        if bPlaneToActor[i]:
            ren.AddActor(cutActor)
            
        sliders[i].SetMinimumValue(-50)
        sliders[i].SetMaximumValue(230)
        sliders[i].SetValue(origins[i][0])
        sliders[i].SetTitleText("x-axis of plane %d" % i)
        sliders[i].GetPoint1Coordinate().SetCoordinateSystemToNormalizedDisplay()
        sliders[i].GetPoint1Coordinate().SetValue(0.0, 1 - 0.1 * (i + 1))
        sliders[i].GetPoint2Coordinate().SetCoordinateSystemToNormalizedDisplay()
        sliders[i].GetPoint2Coordinate().SetValue(0.2, 1 - 0.1 * (i + 1))
        sliders[i].SetSliderLength(0.02)
        sliders[i].SetSliderWidth(0.03)
        sliders[i].SetEndCapLength(0.01)
        sliders[i].SetEndCapWidth(0.03)
        sliders[i].SetTubeWidth(0.005)
        sliders[i].SetLabelFormat("%3.0lf")
        sliders[i].SetTitleHeight(0.02)
        sliders[i].SetLabelHeight(0.02)
        sliderWidgets[i].SetInteractor(iren)
        sliderWidgets[i].SetRepresentation(sliders[i])
        sliderWidgets[i].KeyPressActivationOff()
        sliderWidgets[i].SetAnimationModeToAnimate()
        sliderWidgets[i].SetEnabled(False)
        sliderWidgets[i].AddObserver("InteractionEvent", sliderHandler)

    if bWingToActor:
        ren.AddActor(wingActor)
    
    ren.SetBackground(0, 0, 0)
    renWin.SetSize(1600, 900)
    ren.ResetCamera()
    ren.GetActiveCamera().SetClippingRange(203.2899494251721, 731.8103494457274)
    ren.GetActiveCamera().SetFocalPoint(118.72183980792761, 0.00012969970703125, 36.469017028808594)
    ren.GetActiveCamera().SetPosition(300.86018729049954, -5.765715551063601, 435.4418666873332)
    ren.GetActiveCamera().SetViewUp(-0.802117714199773, -0.005112780752923929, 0.5971440630533839)
    
    # Render
    iren.Initialize()
    renWin.Render()
    iren.Start()

def sliderHandler(obj, event):
    global origins, sliders, planes, planeCuts
    
    for i in range(0, len(planes)):
        origins[i][0] = sliders[i].GetValue()
        planes[i].SetOrigin(origins[i])
        planeCuts[i].Update()

if __name__ == "__main__":
    Main()
