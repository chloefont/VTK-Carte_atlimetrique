import vtk
import os
from Txt2vtk import Txt2vtk
from utils import coordinates_to_cartesian
import math

if __name__ == '__main__':
    """"
    This script is used to visualize the grid in VTK format.
    Note : the grid is generated if it does not exist. Otherwise, the existing vtk file is loaded.
    """
    LAT_MIN = 45
    LAT_MAX = 47.5
    LONG_MIN = 5
    LONG_MAX = 7.5

    EARTH_RADIUS = 6371009  # meters
    CAMERA_DISTANCE = 500000
    SEA_ALTITUDE = 0

    RAW_DATA_FILE = "data/altitudes.txt"
    VTK_GRID_FILE = "data/grid_" + str(SEA_ALTITUDE) + ".vtk"

    grid = None

    if not os.path.exists(VTK_GRID_FILE):
        txt2vtk = Txt2vtk(RAW_DATA_FILE, LAT_MIN, LAT_MAX, LONG_MIN, LONG_MAX, sea_level=SEA_ALTITUDE)
        txt2vtk.read()
        txt2vtk.write(VTK_GRID_FILE)
        grid = txt2vtk.vtk_grid
    else:
        # Load the grid from vtk file
        reader = vtk.vtkStructuredGridReader()
        reader.SetFileName(VTK_GRID_FILE)
        reader.Update()
        grid = reader.GetOutput()

    color_mapping = vtk.vtkColorTransferFunction()
    color_mapping.AddRGBPoint(0, 0, 0.392, 1)
    color_mapping.AddRGBPoint(1, 0.1, 0.4, 0.01)
    color_mapping.AddRGBPoint(200, 0.1, 0.5, 0.01)
    color_mapping.AddRGBPoint(400, 0.01, 0.7, 0.01)
    color_mapping.AddRGBPoint(800, 0.8, 0.6, 0.1)
    color_mapping.AddRGBPoint(1600, 1, 1, 1)

    mapper = vtk.vtkDataSetMapper()
    mapper.SetInputData(grid)
    mapper.SetLookupTable(color_mapping)

    gridActor = vtk.vtkActor()
    gridActor.SetMapper(mapper)

    renderer = vtk.vtkRenderer()
    renderer.AddActor(gridActor)

    f_point_x, f_point_y, f_point_z = coordinates_to_cartesian(EARTH_RADIUS, math.radians((LAT_MIN + LAT_MAX) / 2),
                                                               math.radians((LONG_MIN + LONG_MAX) / 2))
    renderer.GetActiveCamera().SetFocalPoint([f_point_x, f_point_y, f_point_z])

    position_x, position_y, position_z = coordinates_to_cartesian(EARTH_RADIUS + CAMERA_DISTANCE, math.radians((LAT_MIN + LAT_MAX) / 2),
                                                                  math.radians((LONG_MIN + LONG_MAX) / 2))
    renderer.GetActiveCamera().SetPosition([position_x, position_y, position_z])
    renderer.GetActiveCamera().SetClippingRange(0.1, 10000)

    window = vtk.vtkRenderWindow()
    window.AddRenderer(renderer)
    window.SetSize(1000, 1000)

    interactor = vtk.vtkRenderWindowInteractor()
    interactor.SetRenderWindow(window)

    style = vtk.vtkInteractorStyleTrackballCamera()
    interactor.SetInteractorStyle(style)

    window.Render()
    image_filter = vtk.vtkWindowToImageFilter()
    image_filter.SetInput(window)
    image_filter.Update()
    filename = "Switzerland_" + str(SEA_ALTITUDE) + ".png"
    png_writer = vtk.vtkPNGWriter()
    png_writer.SetFileName(filename)
    png_writer.SetInputData(image_filter.GetOutput())
    png_writer.Write()

    interactor.Initialize()
    interactor.Start()