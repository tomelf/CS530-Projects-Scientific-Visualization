#!/usr/bin/env python

import sys
import vtk

def isovalueSliderHandler(obj, event):
    global isovalue, contours
    isovalue = obj.GetRepresentation().GetValue()
    contours.SetValue(0, isovalue)
    print "Change Isovalue: %f" % isovalue

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
    global isovalue, contours, ren
    
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

    print "data: %s %s %s" % (sys.argv[1], sys.argv[2], sys.argv[3])
    
    cfdreader = vtk.vtkStructuredPointsReader()
    cfdreader.SetFileName(sys.argv[1])
    
    # setup wing data
    wingReader = vtk.vtkUnstructuredGridReader()
    wingReader.SetFileName(sys.argv[3])
    wingReader.Update()
    wingMapper = vtk.vtkDataSetMapper()
    wingMapper.SetInputConnection(wingReader.GetOutputPort())
    wingActor = vtk.vtkActor()
    wingActor.SetMapper(wingMapper)
    wingActor.GetProperty().SetColor(.4, .4, .4)
    
    bRakesToActor = [True, True, False]
    bWingToActor = True
    
    datamin = 0
    datamax = 230
    
    lut = vtk.vtkColorTransferFunction()
    lut.SetColorSpaceToHSV()
    lut.AddHSVPoint(datamin, 0, 1, 1)
    dis = float(datamax - datamin) / 7
    for i in range(0, 8):
        lut.AddHSVPoint(float(datamin + dis * i), 0.1 * i, 1, 1)
    
    colorBar = vtk.vtkScalarBarActor()
    colorBar.SetLookupTable(lut)
    colorBar.SetTitle("")
    colorBar.SetNumberOfLabels(6)
    colorBar.SetLabelFormat("%4.0f")
    colorBar.SetPosition(0.9, 0.1)
    colorBar.SetWidth(0.05)
    colorBar.SetHeight(0.4)
    ren.AddActor(colorBar)
    
    rakes = [
             vtk.vtkLineSource(),
             vtk.vtkLineSource(),
             vtk.vtkLineSource()
             ]
    rakes[0].SetPoint1(-230, -230, 0)
    rakes[0].SetPoint2(230, 230, 0)
    rakes[0].SetResolution(50)
    
    rakes[1].SetPoint1(230, -230, 0)
    rakes[1].SetPoint2(-230, 230, 0)
    rakes[1].SetResolution(50)
    
    rakes[2].SetPoint1(0, -100, 10)
    rakes[2].SetPoint2(0, 100, 10)
    rakes[2].SetResolution(60)
    
    rakeColors = [
                  [0, 1, 0],
                  [0, 1, 0],
                  [0, 1, 0],
                  ]
    
    for i in range(0, len(rakes)):
        integ = vtk.vtkRungeKutta4()
        streamLine = vtk.vtkStreamLine()
        streamLine.SetInputConnection(cfdreader.GetOutputPort())
        streamLine.SetSourceConnection(rakes[i].GetOutputPort())
        streamLine.SetMaximumPropagationTime(50);
        streamLine.SetIntegrationStepLength(1);
        streamLine.SetStepLength(0.01);
        streamLine.SetIntegrationDirectionToForward();
        streamLine.SetIntegrator(integ)
        streamLine.SpeedScalarsOn()
        
        streamLineMapper = vtk.vtkPolyDataMapper()
        streamLineMapper.SetInputConnection(streamLine.GetOutputPort())
        streamLineMapper.SetLookupTable(lut)
        
        streamLineActor = vtk.vtkActor()
        streamLineActor.SetMapper(streamLineMapper)
        streamLineActor.GetProperty().SetColor(rakeColors[i])
        streamLineActor.GetProperty().SetOpacity(0.9);
        
        if bRakesToActor[i]:
            ren.AddActor(streamLineActor)
 
    if bWingToActor:
        ren.AddActor(wingActor)
    
    isoreader = vtk.vtkStructuredPointsReader()
    isoreader.SetFileName(sys.argv[2])
    isoreader.Update()
    
#     r = isoreader.GetOutput().GetScalarRange()
#     datamin = r[0]
#     datamax = r[1]
#     isovalue = (datamax+datamin)/2.0
    isovalue = 300
    datamin = 0
    datamax = 300
    
    contours = vtk.vtkContourFilter()
    contours.SetInputConnection(isoreader.GetOutputPort());
    contours.ComputeNormalsOn()
    contours.SetValue(0, isovalue)
    
    lut = vtk.vtkColorTransferFunction()
    lut.SetColorSpaceToHSV()
    lut.AddHSVPoint(datamin, 0, 1, 1)
    dis = (datamax - datamin) / 7
    for i in range(0, 8):
        lut.AddHSVPoint(datamin + dis * i, 0.1 * i, 1, 1)
        
    isoMapper = vtk.vtkPolyDataMapper()
    isoMapper.SetLookupTable(lut)
    isoMapper.SetInputConnection(contours.GetOutputPort())

    isoActor = vtk.vtkActor()
    isoActor.GetProperty().SetRepresentationToWireframe()
    isoActor.SetMapper(isoMapper)
    isoActor.GetProperty().SetOpacity(0.08);

    ren.AddActor(wingActor)
    ren.AddActor(isoActor)
    
    ren.SetBackground(0, 0, 0)
    renWin.SetSize(1600, 900)
    
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
    SliderWidget1.SetEnabled(False)
    SliderWidget1.AddObserver("InteractionEvent", isovalueSliderHandler)
    
    ren.ResetCamera()
    ren.GetActiveCamera().SetClippingRange(417.55784439078775, 1491.5763714138557)
    ren.GetActiveCamera().SetFocalPoint(118.72183980792761, 0.00012969970703125, 36.469017028808594)
    ren.GetActiveCamera().SetPosition(680.0192576650034, 16.65944318371372, 790.5781258299678)
    ren.GetActiveCamera().SetViewUp(-0.802117714199773, -0.005112780752923929, 0.5971440630533839)

    # Render
    iren.Initialize()
    renWin.Render()
    iren.Start()

if __name__ == "__main__":
    Main()
