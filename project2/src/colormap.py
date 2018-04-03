#!/usr/bin/env python

import sys
import re
import vtk
from vtk import vtkScalarBarActor, vtkTextProperty

import Tkinter
from vtk.tk.vtkTkRenderWindowInteractor import vtkTkRenderWindowInteractor

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

def updateUI(mode=0):
    lut.RemoveAllPoints()

    if mode==0: #continuous
        print continuousType
        if continuousType == "HSV":
            for p in continuousData:
                print p
                lut.AddHSVPoint(float(p[0]),float(p[1]),float(p[2]),float(p[3]),0.5,0)
        elif continuousType == "RGB":
            for p in continuousData:
                print p
                lut.AddRGBPoint(float(p[0]),float(p[1]),float(p[2]),float(p[3]),0.5,0)
    elif mode==1: #discrete
        print discreateType
        if discreateType == "HSV":
            for p in discreteData:
                print p
                lut.AddHSVPoint(float(p[0]),float(p[1]),float(p[2]),float(p[3]),0.5,1)
        elif discreateType == "RGB":
            for p in discreteData:
                print p
                lut.AddRGBPoint(float(p[0]),float(p[1]),float(p[2]),float(p[3]),0.5,1)

def showContinuous():
    updateUI(0)
    renWin.Render()

def showDiscrete():
    updateUI(1)
    renWin.Render()

def Main():
    global datamin, datamax, lut, renWin

    # Load bathymetry dataset
    bathymetryReader = vtk.vtkStructuredPointsReader()
    bathymetryReader.SetFileName(sys.argv[1])
    bathymetryReader.Update()
    r = bathymetryReader.GetOutput().GetPointData().GetScalars().GetRange()
    datamin = r[0]
    datamax = r[1]

    loadContinuousFile(sys.argv[2])
    loadDiscreteFile(sys.argv[3])

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
    colorBar.SetWidth(0.07)
    colorBar.SetHeight(0.8)

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    # Create renderer stuff
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)
    renWin.SetSize(1280, 800)

    # Add the actors to the renderer, set the background and size
    ren.AddActor(actor)
    ren.AddActor(colorBar)
    ren.ResetCamera()
    ren.SetBackground(0, 0, 0)
    ren.ResetCameraClippingRange()

    root = Tkinter.Tk()
    root.title('Task 2. MRI Data')
    frame = Tkinter.Frame(root)
    frame.pack(fill=Tkinter.BOTH, expand="false", side=Tkinter.TOP)

    mode = Tkinter.IntVar()
    mode.set(1)
    Tkinter.Radiobutton(frame, text="Continuous color map", padx=20, variable=mode, value=1, command=showContinuous).pack(anchor=Tkinter.W)
    Tkinter.Radiobutton(frame, text="Discrete color map", padx=20, variable=mode, value=2, command=showDiscrete).pack(anchor=Tkinter.W)

    # Setup for rendering window interactor       
    renWinInteract = vtkTkRenderWindowInteractor(frame,rw=renWin, width=1280, height=800)
    
    # Specify interaction with 2D image
    style = vtk.vtkInteractorStyleImage()
    style.SetInteractionModeToImage2D()
    renWinInteract.SetInteractorStyle(style)

    renWinInteract.Initialize()
    renWinInteract.pack(side='top', fill='both', expand="false")
    renWinInteract.Start()

    updateUI(0)
    renWin.Render()

    root.mainloop()

if __name__=="__main__":
    Main()