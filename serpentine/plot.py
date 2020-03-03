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

"""Plotting tools
"""

import numpy as np
import vtk
import k3d
import ipywidgets
import serpentine.tools


class InteractiveSlicer(object):
    """Interactive slice plot for exploring 3D simulation data.
    """
    def __init__(self, data=None):
        self.updater = serpentine.tools.PolyDataUpdater()

        self.color_map = k3d.matplotlib_color_maps.nipy_spectral

        self.color_attribute = ('vr', 250.0, 750.0)

        if data is not None:
            self.create(data)
            self.launch()

    def launch(self):
        display(self.plot)

    def controllers(self):

        sliders = [self.spherical_slice_slider,
                   self.longitude_slice_slider,
                   self.color_range_slider]

        return ipywidgets.VBox(sliders,
                               layout=ipywidgets.Layout(width='50%'))

    def initialize_sliders(self):

        layout = ipywidgets.Layout(width='80%')
        style = {'description_width': '150px'}

        self.spherical_slice_slider \
            = ipywidgets.widgets.FloatSlider(value=0.1001,
                                             min=0.1001,
                                             max=2.0,
                                             step=0.01,
                                             description='Radius [AU]:',
                                             layout=layout,
                                             style=style)

        self.color_range_slider \
            = ipywidgets.widgets.IntRangeSlider(value=[250.0, 750.0],
                                                min=0,
                                                max=2000,
                                                step=1,
                                                description='Value range: [km/s]',
                                                layout=layout, style=style)

        self.longitude_slice_slider \
            = ipywidgets.widgets.IntSlider(min=-180, max=180, step=1,
                                           description='Lon [deg]:',
                                           layout=layout, style=style)

        self.spherical_slice_slider.observe(self.on_radius_change, names='value')
        self.color_range_slider.observe(self.on_color_range_change, names='value')
        self.longitude_slice_slider.observe(self.on_longitude_change, names='value')

    def on_radius_change(self, s):
        self.updater.update_sphere_cut(self.data,
                                       origin=[0, 0, 0],
                                       radius=self.spherical_slice_slider.value,
                                       plot=self.spherical_slice,
                                       color_attribute=self.color_attribute)

    def on_longitude_change(self, s):
        lon = self.longitude_slice_slider.value
        normal = [-np.sin(lon*np.pi/180.0), np.cos(lon*np.pi/180.0), 0.0]
        self.updater.update_plane_cut(self.data, [0, 0, 0], normal, self.meridional_slice, self.color_attribute)

    def on_color_range_change(self, s):
        self.meridional_slice.color_range = s.new
        self.equatorial_slice.color_range = s.new
        self.spherical_slice.color_range = s.new

    def set_color_map(self, cmap):
        self.meridional_slice.color_map = cmap
        self.equatorial_slice.color_map = cmap
        self.spherical_slice.color_map = cmap

    def create(self, data):

        self.plot = k3d.plot()
        self.data = data

        # Equatorial slice
        self.equatorial_slice \
            = k3d.vtk_poly_data(serpentine.tools.extract_plane(data, [0, 0, 0], [0, 0, 1]),
                                color_attribute=self.color_attribute,
                                color_map=self.color_map)

        # Meridional slice
        self.meridional_slice \
            = k3d.vtk_poly_data(serpentine.tools.extract_plane(data, [0, 0, 0], [0, 1, 0]),
                                color_attribute=self.color_attribute,
                                color_map=self.color_map)

        # Spherical slice
        self.spherical_slice \
            = k3d.vtk_poly_data(serpentine.tools.extract_sphere(data, [0, 0, 0], 0.105),
                                color_attribute=self.color_attribute,
                                color_map=self.color_map)

        self.boundary_sphere = k3d.points([0, 0, 0], point_size=0.2, shader="mesh", color=0xffffff, mesh_detail=3)

        # Get rmin and rmax
        x, y, z = np.split(self.equatorial_slice.vertices.T, 1, axis=0)[0]
        rsqr = x**2 + y**2 + z**2
        self.r_bounds = (np.sqrt(min(rsqr)), np.sqrt(max(rsqr)))

        # Add to plot
        self.plot += self.equatorial_slice
        self.plot += self.meridional_slice
        self.plot += self.spherical_slice
        self.plot += self.boundary_sphere

        # Modify defaults
        self.plot.grid_auto_fit = False

        self.initialize_sliders()
