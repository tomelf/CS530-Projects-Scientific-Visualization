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
    global ren
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
    
    bRakesToActor = [True, True, True]
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
    
#     rakes[2].SetPoint1(0, -200, 10)
#     rakes[2].SetPoint2(0, 200, 10)
#     rakes[2].SetResolution(50)
    
    for i in range(0, len(rakes)):
        rakeMapper = vtk.vtkPolyDataMapper()
        rakeMapper.SetInputConnection(rakes[i].GetOutputPort())
        rakeActor = vtk.vtkActor()
        rakeActor.SetMapper(rakeMapper)
        
        integ = vtk.vtkRungeKutta4()
        streamLine = vtk.vtkStreamLine()
        streamLine.SetInputConnection(cfdreader.GetOutputPort())
        streamLine.SetSourceConnection(rakes[i].GetOutputPort())
        streamLine.SetMaximumPropagationTime(50);
        streamLine.SetIntegrationStepLength(.1);
        streamLine.SetStepLength(0.001);
        streamLine.SetIntegrationDirectionToForward();
        streamLine.SetIntegrator(integ)
        streamLine.SpeedScalarsOn()
        
        scalarSurface = vtk.vtkRuledSurfaceFilter()
        scalarSurface.SetInputConnection(streamLine.GetOutputPort())
        scalarSurface.SetOffset(0)
        scalarSurface.SetOnRatio(0)
#         scalarSurface.PassLinesOn()
        scalarSurface.SetRuledModeToPointWalk()
#         scalarSurface.SetDistanceFactor(40)
         
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(scalarSurface.GetOutputPort())
        mapper.SetLookupTable(lut)
        mapper.SetScalarRange(cfdreader.GetOutput().GetScalarRange())
        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetColor(0, 1, 0)
        actor.GetProperty().SetOpacity(0.5);
        
        if bRakesToActor[i]:
            ren.AddActor(actor)
 
    if bWingToActor:
        ren.AddActor(wingActor)
    
    ren.SetBackground(0, 0, 0)
    renWin.SetSize(1600, 900)
    
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
