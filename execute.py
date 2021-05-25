#!/usr/bin/env python3

""" An application to identify groups of natural products by comparing grouped mass spectrometry features and compound
groups from chemical similarity methods
"""

import sys
from pathlib import Path

from snapms.atlas_tools.atlas_import import import_atlas
from snapms.config import Parameters
from snapms.core import create_gnps_network_annotations, network_from_mass_list

# current working directory for data file paths
CWD = Path(__file__).parent


def main():
    DATADIR = CWD / "data"
    assert DATADIR.exists()

    #### CONFIG
    source_ms_data = DATADIR / "ms_input" / "mass_list.csv"
    # source_ms_data = DATADIR / "ms_input" / "NIH_Natural_Products_1_And_2.graphml"
    # atlas_data = DATADIR / "atlas_input" / "npatlas_all_20201210.tsv"
    atlas_data = DATADIR / "atlas_input" / "npatlas_v202006.json"
    output_directory = DATADIR / "output"
    # TODO: Add all optional params explicitly for example script
    parameters = Parameters(source_ms_data, atlas_data, output_directory)

    # Load Atlas data as Pandas dataframe
    atlas_df = import_atlas(parameters)

    if parameters.file_type == "csv":
        network_from_mass_list(atlas_df, parameters)
    elif parameters.file_type == "graphml":
        create_gnps_network_annotations(atlas_df, parameters)
    else:
        print(
            "ERROR: This file type is not supported. Supported types include csv (for simple peak lists) and graphML "
            "(for standard GNPS output)"
        )
        sys.exit(-1)


if __name__ == "__main__":
    main()
