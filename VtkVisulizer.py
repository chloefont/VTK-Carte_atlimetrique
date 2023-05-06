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

    RAW_DATA_FILE = "data/altitudes.txt"
    VTK_GRID_FILE = "data/grid.vtk"

    EARTH_RADIUS = 6371009  # meters
    CAMERA_DISTANCE = 500000
    SEA_LEVEL = 0

    grid = None

    if not os.path.exists(VTK_GRID_FILE):
        txt2vtk = Txt2vtk(RAW_DATA_FILE, LAT_MIN, LAT_MAX, LONG_MIN, LONG_MAX)
        txt2vtk.read()
        txt2vtk.write(VTK_GRID_FILE)
        grid = txt2vtk.vtk_grid
    else:
        # Load the grid from file
        reader = vtk.vtkStructuredGridReader()
        reader.SetFileName(VTK_GRID_FILE)
        reader.Update()

        # Get the output (vtkStructuredGrid) from the reader
        grid = reader.GetOutput()

    ctf = vtk.vtkColorTransferFunction()
    ctf.AddRGBPoint(0, 0.513, 0.49, 1)  # Water, Blue (0x827CFF) for water
    ctf.AddRGBPoint(1, 0.157, 0.325, 0.141)  # Grass, Dark green (0x285223) for low altitude
    ctf.AddRGBPoint(500, 0.219, 0.717, 0.164)  # Grass, Light green (0x37B629) for middle (low) altitude
    ctf.AddRGBPoint(900, 0.886, 0.721, 0.364)  # Rock, Sort of yellow/brown (0xE1B75C)) for middle (high) altitude
    ctf.AddRGBPoint(1600, 1, 1, 1)  # Snow, White (0xFFFFFF) for high altitude (for cliffs)

    # --------- Mapper - Actor ---------
    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(grid)
    mapper.SetLookupTable(ctf)

    gridActor = vtk.vtkActor()
    gridActor.SetMapper(mapper)

    # --------- Render ---------
    renderer = vtk.vtkRenderer()
    renderer.AddActor(gridActor)

    # Setting focal point to center of the displayed area.
    fx, fy, fz = to_cartesian(EARTH_RADIUS, math.radians((LAT_MIN + LAT_MAX) / 2),
                              math.radians((LONG_MIN + LONG_MAX) / 2))
    renderer.GetActiveCamera().SetFocalPoint([fx, fy, fz])

    # Setting camera position to center of the zone, elevated by CAMERA_DISTANCE (500km currently)
    cx, cy, cz = to_cartesian(EARTH_RADIUS + CAMERA_DISTANCE, math.radians((LAT_MIN + LAT_MAX) / 2),
                              math.radians((LONG_MIN + LONG_MAX) / 2))
    renderer.GetActiveCamera().SetPosition([cx, cy, cz])
    renderer.GetActiveCamera().SetClippingRange(0.1, 1_000_000)

    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(renderer)
    renWin.SetSize(800, 800)

    # --------- Interactor ---------
    intWin = vtk.vtkRenderWindowInteractor()
    intWin.SetRenderWindow(renWin)

    style = vtk.vtkInteractorStyleTrackballCamera()
    intWin.SetInteractorStyle(style)

    # --------- Print image ---------
    renWin.Render()
    w2if = vtk.vtkWindowToImageFilter()
    w2if.SetInput(renWin)
    w2if.Update()
    filename = "Map_Screenshot_Sea_Level_" + str(SEA_LEVEL) + ".png"
    writer = vtk.vtkPNGWriter()
    writer.SetFileName(filename)
    writer.SetInputData(w2if.GetOutput())
    writer.Write()

    intWin.Initialize()
    intWin.Start()