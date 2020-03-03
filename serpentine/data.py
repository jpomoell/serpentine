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

"""Data loaders
"""

import vtk


class EUHFORIAData(object):
    """A simplifed EUHFORIA data-loader for the purposes of this demo.
    """

    def __init__(self, file_name=None):
        if file_name is not None:
            self.read(file_name)

    def read(self, file_name):
        """Loads the given .vts file
        """

        self.reader = vtk.vtkXMLStructuredGridReader()
        self.reader.SetFileName(file_name)
        self.reader.Update()
