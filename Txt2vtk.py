import vtk
import math
from skimage import measure, morphology
import numpy as np


class Txt2vtk:
    line_size = 0
    column_size = 0
    EARTH_RADIUS = 6371009  # meters
    vtk_grid = vtk.vtkStructuredGrid()

    def __init__(self, filename, lat_min, lat_max, long_min, long_max, sea_level=0):
        self.filename = filename
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.long_min = long_min
        self.long_max = long_max
        self.sea_level = sea_level

    def read(self):
        file = open(self.filename, 'r')

        # Read header
        grid_dimensions = file.readline().strip().split(" ")
        self.line_size = int(grid_dimensions[0])
        self.column_size = int(grid_dimensions[1])

        #Read data
        raw_altitudes = [[int(x) for x in line.strip().split(" ")] for line in file]

        positions = vtk.vtkPoints()
        interval_lat = (self.lat_max - self.lat_min) / (self.line_size - 1)  # TODO retirer le -1?
        interval_long = (self.long_max - self.long_min) / (self.column_size - 1)

        for i in range(self.line_size):
            for j in range(self.column_size):
                positions.InsertNextPoint(
                    self.coordinates_to_cartesian(raw_altitudes[i][j] + self.EARTH_RADIUS, math.radians(self.lat_min + i * interval_lat), math.radians(self.long_min + j * interval_long)))

        raw_altitudes = np.array(raw_altitudes)
        lakes = detect_flat_areas(raw_altitudes)
        raw_altitudes[lakes] = 0

        altitudes = vtk.vtkIntArray()

        for i in range(0, self.line_size):
            for j in range(0, self.column_size):
                if raw_altitudes[i][j] < self.sea_level:
                    altitudes.InsertNextValue(0)
                else:
                    altitudes.InsertNextValue(raw_altitudes[i][j])

        self.vtk_grid = vtk.vtkStructuredGrid()
        self.vtk_grid.SetDimensions(self.line_size, self.column_size, 1)
        self.vtk_grid.SetPoints(positions)
        self.vtk_grid.GetPointData().SetScalars(altitudes)

    def coordinates_to_cartesian(self, radius, lat, long):
        x = radius * math.sin(lat) * math.sin(long)
        y = radius * math.cos(lat)
        z = radius * math.sin(lat) * math.cos(long)

        return x, y, z

    def write(self, filename):
        writer = vtk.vtkStructuredGridWriter()
        writer.SetInputData(self.vtk_grid)
        writer.SetFileName(filename)
        writer.Write()

def detect_flat_areas(altitudes, size = 512):
    labels = measure.label(altitudes, connectivity=1)
    lakes = morphology.remove_small_objects(labels, size) > 0
    return lakes

if __name__ == '__main__':
    LAT_MIN = 45
    LAT_MAX = 47.5
    LONG_MIN = 5
    LONG_MAX = 7.5

    RAW_DATA_FILE = "data/altitudes.txt"
    VTK_GRID_FILE = "data/grid.vtk"

    txt2vtk = Txt2vtk(RAW_DATA_FILE, LAT_MIN, LAT_MAX, LONG_MIN, LONG_MAX)
    txt2vtk.read()
    txt2vtk.write(VTK_GRID_FILE)