# This file is part of SERPENTINE-DEMO.
#
# Copyright 2020 Jens Pomoell
#
# Licensed under the EUPL, Version 1.1 or - as soon they will be approved by the
# European Commission - subsequent versions of the EUPL (the "Licence");
# You may not use this work except in compliance with the Licence.
#
# You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the Licence is distributed on an "AS IS" basis,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the Licence for the specific language governing permissions and
# limitations under the Licence.

"""Collection of tools
"""

import numpy as np
import vtk


class PolyDataUpdater(object):
    """Class for updating VTK data attributes
    """
    def __init__(self):
        pass

    def get_mesh_data(self, poly_data, color_attribute=None):
        """Returns vertices, indices and color attribute of triangulation
        """
        if poly_data.GetPolys().GetMaxCellSize() > 3:
            cut_triangles = vtk.vtkTriangleFilter()
            cut_triangles.SetInputData(poly_data)
            cut_triangles.Update()
            poly_data = cut_triangles.GetOutput()

        if color_attribute is not None:
            attribute = vtk.util.numpy_support.vtk_to_numpy(poly_data.GetPointData().GetArray(color_attribute[0]))
            color_range = color_attribute[1:3]
        else:
            attribute = []
            color_range = []

        vertices = vtk.util.numpy_support.vtk_to_numpy(poly_data.GetPoints().GetData())
        indices = vtk.util.numpy_support.vtk_to_numpy(poly_data.GetPolys().GetData()).reshape(-1, 4)[:, 1:4]

        return np.array(vertices, np.float32), np.array(indices, np.uint32), np.array(attribute, np.float32)

    def update_plane_cut(self, data, origin, normal, plot, color_attribute):

        poly_data = extract_plane(data, origin, normal)

        if poly_data.GetNumberOfCells() > 0:
            vertices, indices, attribute = self.get_mesh_data(poly_data, color_attribute)

            with plot.hold_sync():
                plot.vertices = vertices
                plot.indices = indices
                plot.attribute = attribute

    def update_sphere_cut(self, data, origin, radius, plot, color_attribute):

        poly_data = extract_sphere(data, origin, radius)

        if poly_data.GetNumberOfCells() > 0:
            vertices, indices, attribute = self.get_mesh_data(poly_data, color_attribute)

            with plot.hold_sync():
                plot.vertices = vertices
                plot.indices = indices
                plot.attribute = attribute


def extract_plane(data, origin, normal):
    """Extracts a planar slice of data from VTK data object
    """
    plane = vtk.vtkPlane()
    plane.SetOrigin(*origin)
    plane.SetNormal(*normal)

    cutter = vtk.vtkCutter()
    cutter.SetInputDataObject(data.reader.GetOutput())
    cutter.SetCutFunction(plane)
    cutter.Update()

    return cutter.GetOutputDataObject(0)


def extract_sphere(data, origin, radius):
    """Extracts a spherical slice of data from VTK data object
    """
    sphere = vtk.vtkSphere()
    sphere.SetRadius(radius)

    cutter = vtk.vtkCutter()
    cutter.SetInputDataObject(data.reader.GetOutput())
    cutter.SetCutFunction(sphere)
    cutter.Update()

    return cutter.GetOutputDataObject(0)
