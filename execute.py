#!/usr/bin/env python3

""" An application to identify groups of natural products by comparing grouped mass spectrometry features and compound
groups from chemical similarity methods
"""

import csv
import sys
from pathlib import Path
from typing import List

from snapms.atlas_tools.atlas_import import import_atlas
from snapms.matching_tools import mass_list, match_compounds
from snapms.network_tools import create_networks

# current working directory for data file paths
CWD = Path(__file__).parent


# Defaults
DEFAULT_ADDUCT_LIST = [
    "m_plus_h",
    "m_plus_na",
    "m_plus_nh4",
    "m_plus_h_minus_h2o",
    "m_plus_k",
    "2m_plus_h",
    "2m_plus_na",
]


class Parameters:
    """Class containing all of the setup parameters from SNAP-MS"""

    def __init__(
        self,
        file_path: Path,
        atlas_db_path: Path,
        output_path: Path,
        ppm_error: int = 10,
        adduct_list: List[str] = DEFAULT_ADDUCT_LIST,
        remove_duplicates: bool = True,
        min_gnps_size: int = 3,
        max_gnps_size: int = 5000,
        min_atlas_size: int = 3,
        min_group_size: int = 3,
    ):
        self.file_path = file_path
        # pathlib.Path gives convenient methods for getting name and extension
        self.file_name = file_path.stem
        self.file_type = file_path.suffix.lstrip(".").lower()
        self.reference_db = atlas_db_path
        self.output_path = output_path
        self.sample_output_path = self.sample_output_directory_path()
        self.ppm_error = ppm_error
        self.adduct_list = adduct_list
        self.remove_duplicates = remove_duplicates
        self.min_gnps_cluster_size = min_gnps_size
        self.max_gnps_cluster_size = max_gnps_size
        self.min_atlas_annotation_cluster_size = min_atlas_size
        self.min_compound_group_count = min_group_size

    def sample_output_directory_path(self) -> Path:
        file_path = self.output_path / f"{self.file_name}_output"
        file_path.mkdir(exist_ok=True, parents=True)
        return file_path


def network_from_mass_list(atlas_df, parameters):
    """Tool to generate compound prediction network from a single mass list. Saves graphML file"""

    target_mass_list = []

    with open(parameters.file_path) as f:
        csv_f = csv.reader(f)
        next(f)

        for row in csv_f:
            target_mass_list.append(float(row[0]))

    if parameters.remove_duplicates:
        target_mass_list = mass_list.remove_mass_duplicates(
            target_mass_list, parameters
        )
    compound_list = match_compounds.return_compounds(
        target_mass_list, parameters, atlas_df
    )
    compound_network = create_networks.match_compound_network(compound_list)
    create_networks.annotate_top_candidates(compound_network)
    create_networks.export_graphml(compound_network, parameters)


def create_gnps_network_annotations(atlas_df, parameters):
    """Function to predict identities of all clusters in GNPS graphML file using cluster mapping algorithm"""

    # Analyze each gnps subgraph to create predictions about possible compound families from atlas data.
    # This is the core function of this suite of tools.
    match_compounds.annotate_gnps_network(atlas_df, parameters)

    # Append all Atlas annotation networks to GNPS original network file
    # NOTE: GNPS network file must be open in Cytoscape for this to work
    cytoscape_status = input("Is the Cytoscape file open? [y/n]")
    if cytoscape_status == "y":
        create_networks.insert_atlas_clusters_to_cytoscape(parameters)
    else:
        print("OK, bye!")
        sys.exit()


if __name__ == "__main__":
    DATADIR = CWD / "data"
    assert DATADIR.exists()

    #### CONFIG
    source_ms_data = DATADIR / "ms_input" / "mass_list.csv"
    # source_ms_data = DATADIR / "ms_input" / "NIH_Natural_Products_1_And_2.graphml"
    # atlas_data = DATADIR / "atlas_input" / "npatlas_all_20201210.tsv"
    atlas_data = DATADIR / "atlas_input" / "npatlas_v202006.json"
    output_directory = DATADIR / "output"
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
        sys.exit()
