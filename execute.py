#!/usr/bin/env python3

""" An application to identify groups of natural products by comparing grouped mass spectrometry features and compound
groups from chemical similarity methods

"""

import csv
import os
from sys import exit

from snapms.atlas_tools.atlas_import import import_atlas
from snapms.matching_tools import match_compounds
from snapms.matching_tools import mass_list
from snapms.network_tools import create_networks


class Parameters:
    """Class containing all of the setup parameters from SNAP-MS"""
    def __init__(self, file_path, atlas_db_path, output_path):
        self.file_path = file_path
        self.file_name = self.extract_file_name(file_path)
        self.file_type = self.extract_file_type(file_path)
        self.reference_db = atlas_db_path
        self.output_path = output_path
        self.sample_output_path = self.sample_output_directory_path()
        self.ppm_error = 10
        self.adduct_list = ["compound_m_plus_h",
                            "compound_m_plus_na",
                            "compound_m_plus_nh4",
                            "compound_m_plus_h_minus_h2o",
                            "compound_m_plus_k",
                            "compound_2m_plus_h",
                            "compound_2m_plus_na"]
        self.remove_duplicates = True
        self.duplicate_mass_error = 0.05     # NOTE: DO WE NEED SEPARATE ERRORS FOR PPM AND DUPLICATES?
        self.min_gnps_cluster_size = 4
        self.max_gnps_cluster_size = 5000
        self.min_atlas_annotation_cluster_size = 3

    def extract_file_name(self, file_path):
        """Extracts file name from file path"""

        return str(os.path.basename(file_path)).rsplit(".")[0]

    def extract_file_type(self, file_path):
        """ Extracts file suffix from file path"""

        extension = os.path.splitext(file_path)

        return extension[1][1:]

    def sample_output_directory_path(self):

        return os.path.join(self.output_path, self.file_name + "_output")


def network_from_mass_list(atlas_df, parameters):
    """Tool to generate compound prediction network from a single mass list. Saves graphML file"""

    target_mass_list = []

    with open(parameters.file_path) as f:
        csv_f = csv.reader(f)
        next(f)

        for row in csv_f:
            target_mass_list.append(float(row[0]))

    if parameters.remove_duplicates:
        target_mass_list = mass_list.remove_mass_duplicates(target_mass_list, parameters)
    compound_list = match_compounds.return_compounds(target_mass_list, parameters, atlas_df)
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
        exit()


if __name__ == "__main__":

    source_ms_data = os.path.join("snapms", "data", "ms_input", "mass_list.csv")
    # source_ms_data = os.path.join("snapms", "data", "ms_input", "METABOLOMICS-SNETS-V2-d909a4dc-download_cytoscape_data-main.graphml")
    atlas_data = os.path.join("snapms", "data", "atlas_input", "npatlas_all_20201210.tsv")
    output_directory = os.path.join("snapms", "data", "output")
    parameters = Parameters(source_ms_data, atlas_data, output_directory)

    # Load Atlas data as Pandas dataframe
    atlas_df = import_atlas(parameters)

    if parameters.file_type == "csv":
        network_from_mass_list(atlas_df, parameters)
    elif parameters.file_type == "graphML" or parameters.file_type == "graphml":
        create_gnps_network_annotations(atlas_df, parameters)
    else:
        print("ERROR: This file type is not supported. Supported types include csv (for simple peak lists) and graphML "
              "(for standard GNPS output)")
        exit()