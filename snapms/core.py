import csv

import pandas as pd

from snapms.config import Parameters, CYTOSCAPE_DATADIR
from snapms.matching_tools import match_compounds
from snapms.network_tools import create_networks
from snapms.network_tools import cytoscape as cy


def network_from_mass_list(atlas_df: pd.DataFrame, parameters: Parameters):
    """Tool to generate compound prediction network from a single mass list. Saves graphML file"""

    target_mass_list = []

    with open(parameters.file_path, encoding="utf-8") as f:
        csv_f = csv.reader(f)
        next(f)

        for row in csv_f:
            target_mass_list.append(float(row[0]))

    if parameters.remove_duplicates:
        target_mass_list = match_compounds.remove_mass_duplicates(
            target_mass_list, parameters.ppm_error
        )
    compound_list = match_compounds.compute_adduct_matches(
        target_mass_list, parameters, atlas_df
    )
    print(f"Found {len(compound_list)} candidate adduct masses")
    compound_network = create_networks.match_compound_network(compound_list)
    create_networks.annotate_top_candidates(compound_network)
    create_networks.export_masslist_graphml(compound_network, parameters)
    if cy.cyrest_is_available():
        print("Inserting mass list data into Cytoscape")
        # If there is a job_id in the params, use this to save the output file
        # For this to work, the snapms datadir should be mounted to the CYTOSCAPE_DATADIR
        # Else use a default
        if parameters.job_id is not None:
            output_path = CYTOSCAPE_DATADIR / parameters.job_id / "snapms.cys"
        else:
            output_path = CYTOSCAPE_DATADIR / "snapms.cys"
        create_networks.add_cluster_to_cytoscape(
            compound_network,
            "snapms_mass_list",
        )
        cy.cyrest_save_session(output_path)
        cy.cyrest_delete_session()
    else:
        print("WARNING - Cytoscape Unavailable!")


def create_gnps_network_annotations(atlas_df: pd.DataFrame, parameters: Parameters):
    """Function to predict identities of all clusters in GNPS graphML file using cluster mapping algorithm"""

    # Analyze each gnps subgraph to create predictions about possible compound families from atlas data.
    # This is the core function of this suite of tools.
    match_compounds.annotate_gnps_network(atlas_df, parameters)

    # Append all Atlas annotation networks to GNPS original network file
    # NOTE: GNPS network file must be open in Cytoscape for this to work
    # cytoscape_status = input("Is the Cytoscape file open? [y/n]")
    if cy.cyrest_is_available():
        print("Cytoscape detected - performing network annotation")
        create_networks.insert_atlas_clusters_to_cytoscape(parameters)
    else:
        print("WARNING - Cytoscape Unavailable!")
    if parameters.compress_output:
        create_networks.compress_gnps_graphml_outputs(parameters)
