#!/usr/bin/env python3

"""Tools to clean and/or modify input mass lists"""
from typing import List
from snapms.matching_tools import match_compounds


def remove_mass_duplicates(mass_list: List[float], ppm_error: float) -> List[float]:
    """Remove masses in mass list within ppm error of existing masses
    Keeps the first.
    """

    deduplicated_mass_list = []

    for mass in mass_list:
        insert_mass = True
        mass_error = match_compounds.calculate_error(mass, ppm_error)
        for deduplicated_mass in deduplicated_mass_list:
            if mass - mass_error <= deduplicated_mass <= mass + mass_error:
                insert_mass = False
        if insert_mass:
            deduplicated_mass_list.append(mass)

    return deduplicated_mass_list
