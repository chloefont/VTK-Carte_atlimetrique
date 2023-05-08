import vtk
import os
from Txt2vtk import Txt2vtk
import math

def to_cartesian(radius: float, latitude: float, longitude: float):
    """
    Translate spherical coordinate to cartesian coordinate
    inclination and azimuth must be in radian
    https://en.wikipedia.org/wiki/Spherical_coordinate_system
    """
    x = radius * math.sin(latitude) * math.sin(longitude)
    y = radius * math.cos(latitude)
    z = radius * math.sin(latitude) * math.cos(longitude)
    return x, y, z

if __name__ == '__main__':
    LAT_MIN = 45
    LAT_MAX = 47.5
    LONG_MIN = 5
    LONG_MAX = 7.5

    EARTH_RADIUS = 6371009  # meters
    CAMERA_DISTANCE = 500000
    SEA_LEVEL = 0

    RAW_DATA_FILE = "data/altitudes.txt"
    VTK_GRID_FILE = "data/grid_" + str(SEA_LEVEL) + ".vtk"

    grid = None

    if not os.path.exists(VTK_GRID_FILE):
        txt2vtk = Txt2vtk(RAW_DATA_FILE, LAT_MIN, LAT_MAX, LONG_MIN, LONG_MAX, sea_level=SEA_LEVEL)
        txt2vtk.read()
        txt2vtk.write(VTK_GRID_FILE)
        grid = txt2vtk.vtk_grid
    else:
        # Load the grid from vtk file
        reader = vtk.vtkStructuredGridReader()
        reader.SetFileName(VTK_GRID_FILE)
        reader.Update()
        grid = reader.GetOutput()

    ctf = vtk.vtkColorTransferFunction()
    ctf.AddRGBPoint(0, 0, 0.392, 1)
    ctf.AddRGBPoint(1, 0.1, 0.4, 0.01)
    ctf.AddRGBPoint(200, 0.1, 0.5, 0.01)
    ctf.AddRGBPoint(400, 0.01, 0.7, 0.01)
    ctf.AddRGBPoint(800, 0.8, 0.6, 0.1)
    ctf.AddRGBPoint(1600, 1, 1, 1)

    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(grid)
    mapper.SetLookupTable(ctf)

    gridActor = vtk.vtkActor()
    gridActor.SetMapper(mapper)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(gridActor)

    fx, fy, fz = to_cartesian(EARTH_RADIUS, math.radians((LAT_MIN + LAT_MAX) / 2),
                              math.radians((LONG_MIN + LONG_MAX) / 2))
    renderer.GetActiveCamera().SetFocalPoint([fx, fy, fz])

    cx, cy, cz = to_cartesian(EARTH_RADIUS + CAMERA_DISTANCE, math.radians((LAT_MIN + LAT_MAX) / 2),
                              math.radians((LONG_MIN + LONG_MAX) / 2))
    renderer.GetActiveCamera().SetPosition([cx, cy, cz])
    renderer.GetActiveCamera().SetClippingRange(0.1, 10000)

    window = vtk.vtkRenderWindow()
    window.AddRenderer(renderer)
    window.SetSize(1000, 1000)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)

    style = vtk.vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(style)

    window.Render()
    imageFilter = vtk.vtkWindowToImageFilter()
    imageFilter.SetInput(window)
    imageFilter.Update()
    filename = "Switzerland_" + str(SEA_LEVEL) + ".png"
    pngWriter = vtk.vtkPNGWriter()
    pngWriter.SetFileName(filename)
    pngWriter.SetInputData(imageFilter.GetOutput())
    pngWriter.Write()

    interactor.Initialize()
    interactor.Start()