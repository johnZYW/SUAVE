## @ingroup Methods-Weights-Correlations-FLOPS
# systems.py
#
# Created:  May 2020, W. Van Gijseghem
# Modified:

# ----------------------------------------------------------------------
#  Imports
# ----------------------------------------------------------------------

from SUAVE.Core import Units, Data
import numpy as np


# ----------------------------------------------------------------------
#   Systems
# ----------------------------------------------------------------------
# Assumptions
# 1) No variable sweep, change VARSWP to 1 is variable sweep in aicraft
# 2) Hydraulic pressure is 3000 psf (HYDR)
# 3) 1 fuselage, change NFUSE is multiple fuselages

def systems_FLOPS(vehicle):
    """ Calculate the weight of the different engine systems on the aircraft

    Assumptions:
        1) No variable sweep, change VARSWP to 1 is variable sweep in aicraft
        2) Hydraulic pressure is 3000 psf (HYDR)
        3) 1 fuselage, change NFUSE is multiple fuselages

    Source:
        FLOPS

   Inputs:
        vehicle

   Outputs:
       output - a data dictionary with fields:
           wt_flt_ctrl - weight of the flight control system                                               [kilograms]
           wt_apu - weight of the apu                                                                      [kilograms]
           wt_hyd_pnu - weight of the hydraulics and pneumatics                                            [kilograms]
           wt_instruments - weight of the instruments and navigational equipment                           [kilograms]
           wt_avionics - weight of the avionics                                                            [kilograms]
           wt_opitems - weight of the optional items based on the type of aircraft                         [kilograms]
           wt_elec - weight of the electrical items                                                        [kilograms]
           wt_ac - weight of the air conditioning and anti-ice system                                      [kilograms]
           wt_furnish - weight of the furnishings in the fuselage                                          [kilograms]
           wt_anti_ice - weight of anti-ice system                                                         [kilograms]

    Properties Used:
        N/A
    """
    propulsor_name = list(vehicle.propulsors.keys())[0]
    propulsors = vehicle.propulsors[propulsor_name]
    NENG = propulsors.number_of_engines
    VMAX = vehicle.design_mach_number
    SFLAP = vehicle.wings['main_wing'].areas.reference * vehicle.flap_ratio / Units.ft ** 2
    DG = vehicle.mass_properties.max_takeoff / Units.lbs
    WSC = 1.1 * VMAX ** 0.52 * SFLAP ** 0.6 * DG ** 0.32

    XL = vehicle.fuselages['fuselage'].lengths.total / Units.ft
    WF = vehicle.fuselages['fuselage'].width / Units.ft
    FPAREA = XL * WF
    NPASS = vehicle.passengers
    WAPU = 54 * FPAREA ** 0.3 + 5.4 * NPASS ** 0.9

    if vehicle.passengers >= 150:
        NFLCR = 3
    else:
        NFLCR = 2

    FNEW = sum(propulsors.wing_mounted)
    FNAC = propulsors.nacelle_diameter / Units.ft
    FNEF = len(propulsors.wing_mounted) - FNEW
    WIN = 0.48 * FPAREA ** 0.57 * VMAX ** 0.5 * (10 + 2.5 * NFLCR + FNEW + 1.5 * FNEF)

    SW = vehicle.reference_area / Units.ft ** 2
    HYDR = 3000  # Hydraulic system pressure
    VARSWP = 0
    WHYD = 0.57 * (FPAREA + 0.27 * SW) * (1 + 0.03 * FNEW + 0.05 * FNEF) * (3000 / HYDR) ** 0.35 * \
           (1 + 0.04 * VARSWP) * VMAX ** 0.33

    NFUSE = len(vehicle.fuselages)
    WELEC = 92. * XL ** 0.4 * WF ** 0.14 * NFUSE ** 0.27 * NENG ** 0.69 * (1. + 0.044 * NFLCR + 0.0015 * NPASS)

    DESRNG = vehicle.design_range / Units.nmi
    WAVONC = 15.8 * DESRNG ** 0.1 * NFLCR ** 0.7 * FPAREA ** 0.43

    XLP = 0.8 * XL
    DF = vehicle.fuselages['fuselage'].heights.maximum / Units.ft
    WFURN = 127 * NFLCR + 112 * vehicle.NPF + 78 * vehicle.NPB + 44 * vehicle.NPT + 2.6 * XLP * (WF + DF) * NFUSE

    WAC = (3.2 * (FPAREA * DF) ** 0.6 + 9 * NPASS ** 0.83) * VMAX + 0.075 * WAVONC

    WAI = vehicle.wings['main_wing'].spans.projected / Units.ft \
          * 1. / np.cos(vehicle.wings['main_wing'].sweeps.quarter_chord) + 3.8 * FNAC * NENG + 1.5 * WF

    output = Data()
    output.wt_flt_ctrl = WSC * Units.lbs
    output.wt_apu = WAPU * Units.lbs
    output.wt_hyd_pnu = WHYD * Units.lbs
    output.wt_instruments = WIN * Units.lbs
    output.wt_avionics = WAVONC * Units.lbs
    output.wt_elec = WELEC * Units.lbs
    output.wt_ac = WAC * Units.lbs
    output.wt_furnish = WFURN * Units.lbs
    output.wt_anti_ice = WAI * Units.lbs
    output.wt_systems = WSC + WAPU + WIN + WHYD + WELEC + WAVONC + WFURN + WAC + WAI

    return output
