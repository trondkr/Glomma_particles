# This file is part of OpenDrift.
#
# OpenDrift is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, version 2
#
# OpenDrift is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with OpenDrift.  If not, see <https://www.gnu.org/licenses/>.
#
# Copyright 2020, Knut-Frode Dagestad, MET Norway

"""
SedimentDrift is an OpenDrift module for drift and settling of sediments.
Based on work by Simon Weppe, MetOcean Solutions Ltd.
"""

import numpy as np
from opendrift.models.oceandrift import Lagrangian3DArray
from opendrift.models.oceandrift import OceanDrift
from scipy.interpolate import interp1d
from iapws import IAPWS97


class SedimentElement(Lagrangian3DArray):
    variables = Lagrangian3DArray.add_variables([
        ('settled', {'dtype': np.int16,  # 0 is active, 1 is settled
                     'unit': '1',
                     'default': 0}),
        ('resuspended', {'dtype': np.int16,  # 0 is not, 1 is resuspended
                         'unit': '1',
                         'default': 0}),
        ('diameter', {'dtype': np.float32,
                      'units': 'm',
                      'default': 0.006546e-3}),
        ('density', {'dtype': np.float32,
                     'units': 'kg/L',
                     'default': 1500.0}),
        ('terminal_velocity', {'dtype': np.float32,
                               'units': 'm/s',
                               'default': 0.001})
    ])


class SedimentDrift(OceanDrift):
    """Model for sediment drift, under development
    """

    ElementType = SedimentElement

    required_variables = {
        'x_sea_water_velocity': {'fallback': 0},
        'y_sea_water_velocity': {'fallback': 0},
        'sea_surface_wave_significant_height': {'fallback': 0},
        'sea_ice_area_fraction': {'fallback': 0},
        'x_wind': {'fallback': 0},
        'y_wind': {'fallback': 0},
        'land_binary_mask': {'fallback': None},
        'sea_floor_depth_below_sea_level': {'fallback': 100},
        'ocean_vertical_diffusivity': {'fallback': 0.02, 'profiles': True},
        'sea_water_temperature': {'fallback': 10, 'profiles': True},
        'sea_water_salinity': {'fallback': 34, 'profiles': True},
        'surface_downward_x_stress': {'fallback': 0},
        'surface_downward_y_stress': {'fallback': 0},
        'turbulent_kinetic_energy': {'fallback': 0},
        'turbulent_generic_length_scale': {'fallback': 0},
        'upward_sea_water_velocity': {'fallback': 0},
        'sea_surface_wave_stokes_drift_x_velocity': {'fallback': 0},
        'sea_surface_wave_stokes_drift_y_velocity': {'fallback': 0}
    }

    def __init__(self, *args, **kwargs):
        """ Constructor of SedimentDrift module
        """

        super(SedimentDrift, self).__init__(*args, **kwargs)

        # By default, sediments do not strand towards coastline
        # TODO: A more sophisticated stranding algorithm is needed
        self._set_config_default('general:coastline_action', 'previous')

        # Vertical mixing is enabled as default
        self._set_config_default('drift:vertical_mixing', True)

        self._add_config({'vertical_mixing:update_terminal_velocity': {'type': 'bool', 'default': True,
                                                                   'description': 'Update terminal velocity',
                                                                   'level': self.CONFIG_LEVEL_ESSENTIAL}
                          })

    def update_terminal_velocity(self, Tprofiles=None, Sprofiles=None, z_index=None):
        #
        # Method that calculates sinking velocity according to Stokes law for any
        # sediment of a given diameter and density. The values of densities for sand and
        # clay are taken from literature while the diameters are taken from observations
        # done in Glomma June 2020. Particle sizes ranged from 0.0002 - 0.2 mm
        #
        # prepare interpolation of temp, salt
        if not (Tprofiles == None and Sprofiles == None):
            if z_index == None:
                z_i = range(Tprofiles.shape[0])  # evtl. move out of loop
                z_index = interp1d(-self.environment_profiles['z'], z_i, bounds_error=False)  # evtl. move out of loop
            zi = z_index(-self.elements.z)
            upper = np.maximum(np.floor(zi).astype(np.int), 0)
            lower = np.minimum(upper + 1, Tprofiles.shape[0] - 1)
            weight_upper = 1 - (zi - upper)

        # do interpolation of temp, salt if profiles were passed into this function,
        # if not, use reader by calling self.environment
        if Tprofiles == None:
            T0 = self.environment.sea_water_temperature
        else:
            T0 = Tprofiles[upper, range(Tprofiles.shape[1])] * weight_upper + Tprofiles[
                lower, range(Tprofiles.shape[1])] * (1 - weight_upper)
        if Sprofiles == None:
            S0 = self.environment.sea_water_salinity
        else:
            S0 = Sprofiles[upper, range(Sprofiles.shape[1])] * weight_upper + Sprofiles[
                lower, range(Sprofiles.shape[1])] * (1 - weight_upper)

        self.elements.terminal_velocity = \
            self.calc_terminal_velocity(self.elements.density, self.elements.diameter, T0, S0)

    # Separate the actual calculation so that we can use unit-testing
    # Returns terminal velocity in m/s
    def calc_terminal_velocity(self, density_p, diameter_p, T0, S0):
        density_w = self.sea_water_density(T=T0, S=S0)

        # The density difference between a clay/sand particle and the ambient water
        dr = density_w - density_p

        # water viscosity
        #   dynamic_viscosity = IAPWS97(T=T0[0], P=0.0)
        #  dynamic_viscosity = 0.001 * (1.7915 - 0.0538 * T0 + 0.007 * (T0 ** (2.0)) - 0.0023 * S0)
        dynamic_viscosity = 0.0014
        # ~0.0014 kg m-1 s-1

        g = 9.81  # ms-2
        return (diameter_p ** 2 * dr * g) / (18. * dynamic_viscosity)

    def update(self):
        """Update positions and properties of sediment particles.
        """

        # Advecting here all elements, but want to soon add
        # possibility of not moving settled elements, until
        # they are re-suspended. May then need to send a boolean
        # array to advection methods below
        if self.get_config('vertical_mixing:update_terminal_velocity') is True:
            self.update_terminal_velocity()

        self.advect_ocean_current()

        self.vertical_advection()

        self.advect_wind()  # Wind shear in upper 10cm of ocean

        self.stokes_drift()

        self.vertical_mixing()  # Including buoyancy and settling

        self.resuspension()

    def bottom_interaction(self, seafloor_depth):
        """Sub method of vertical_mixing, determines settling"""

        # Deactivate elements closer than 1m from seafloor.
        # Later these should not be deactivated, but rather marked
        # as settled, for possibly later resuspension.
        self.deactivate_elements(self.elements.z < seafloor_depth + 1,
                                 reason='settled')

    def resuspension(self):
        """Resuspending elements if current speed > .25 m/s"""
        resuspending = np.logical_and(self.current_speed() > .25, self.elements.moving == 0)
        if np.sum(resuspending) > 0:
            # Allow moving again
            self.elements.moving[resuspending] = 1
            self.elements.resuspended[resuspending] = 1
            # Suspend 1 cm above seafloor
            self.elements.z[resuspending] = self.elements.z[resuspending] + .05  # 5 cm
