import vtk
import math
from skimage import measure, morphology
import numpy as np


class Txt2vtk:
    line_size = 0
    column_size = 0
    EARTH_RADIUS = 6371009  # meters
    SEA_LEVEL = 0
    vtk_grid = vtk.vtkStructuredGrid()

    # The first line of the file is the size of the grid
    def __init__(self, filename, lat_min, lat_max, long_min, long_max):
        self.filename = filename
        self.lat_min = lat_min
        self.lat_max = lat_max
        self.long_min = long_min
        self.long_max = long_max

    def read(self):
        file = open(self.filename, 'r')

        # Read first line
        grid_dimensions = file.readline().strip().split(" ")
        self.line_size = int(grid_dimensions[0])
        self.column_size = int(grid_dimensions[1])

        # Read rest of the file
        raw_altitudes = [[int(x) for x in line.strip().split(" ")] for line in file]

        positions = vtk.vtkPoints()
        interval_lat = (self.lat_max - self.lat_min) / (self.line_size - 1)  # TODO retirer le -1?
        interval_long = (self.long_max - self.long_min) / (self.column_size - 1)

        for i in range(self.line_size):
            for j in range(self.column_size):
                positions.InsertNextPoint(
                    self.coordinates_to_cartesian(raw_altitudes[i][j] + self.EARTH_RADIUS, math.radians(self.lat_min + i * interval_lat), math.radians(self.long_min + j * interval_long)))

        # # TODO Set lake altitudes to 0
        # # Détection des lacs
        # visited = np.zeros(raw_altitudes.shape, dtype=bool)
        # for i in range(altitudes.shape[0]):
        #     for j in range(altitudes.shape[1]):
        #         if not visited[i, j] and altitudes[i, j] < 30:
        #             # Début d'une nouvelle zone
        #             queue = [(i, j)]
        #             visited[i, j] = True
        #             while queue:
        #                 x, y = queue.pop(0)
        #                 # Parcours des voisins
        #                 for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
        #                     nx, ny = x + dx, y + dy
        #                     if nx >= 0 and ny >= 0 and nx < altitudes.shape[0] and ny < altitudes.shape[1]:
        #                         if not visited[nx, ny]:
        #                             if altitudes[nx, ny] < 30:
        #                                 # Ajout à la zone
        #                                 queue.append((nx, ny))
        #                                 visited[nx, ny] = True

        altitudes = vtk.vtkIntArray()

        for i in range(0, self.line_size):
            for j in range(0, self.column_size):
                if raw_altitudes[i][j] < self.SEA_LEVEL:
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