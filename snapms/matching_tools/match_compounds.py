#!/usr/bin/env python3

"""Tools to match masses from mass list to compounds from Atlas"""

import networkx as nx

from rdkit import Chem

from snapms.matching_tools import data_import
from snapms.network_tools import create_networks


def calculate_error(mass, mass_error):
    """Calculate ppm error for a given mass and error"""

    return round((mass * mass_error)/1000000, 4)


def return_compounds(mass_list, parameters, atlas_df):
    """Tool to search the Atlas for a given mass, and return all compounds with that mass as a specific adduct,
    within a given mass error

    mass_list should be a list of masses accurate to four decimal places
    ppm error should be the required parts per million error. Modern spectrometers are accurate to sub-two ppm.
    Five or ten are conservative values
    adduct list should be a list of adducts that are present in the Atlas dataframe. By default only 'H' and 'Na' are
    present
    atlas_df is the dataframe from data_import.advanced_export after clean_headers has been applied


    """
    output_list = []
    for index, mass in enumerate(mass_list):
        mass_error = calculate_error(mass, parameters.ppm_error)

        for adduct in parameters.adduct_list:
            selected_compounds = atlas_df[atlas_df[adduct].between(mass - mass_error, mass + mass_error)][['npaid'
                , 'compound_accurate_mass', 'compound_smiles']]
            if not selected_compounds.empty:
                selected_compounds['mass'] = mass
                selected_compounds['compound_number'] = index + 1
                selected_compounds['adduct'] = adduct
                output_list += selected_compounds.values.tolist()

    return output_list


def annotate_gnps_network(atlas_df, parameters):
    """Tool to create structure class predictions from GNPS clusters by identifying the compound classes with the
    highest prevalence in the GNPS network.

    remove_node_duplicates is a bool flag that optionally filters the nodes in each GNPS cluster and removes nodes with
    very similar masses. This eliminates repetition of sets of compound matches from the Atlas, decreases the number
    of compound groups, and prevents 'annotation bloat' where many nodes become interconnected because they are
    repeated compounds, but in different compound groups (and so get edges added in annotation network).
    Leads to cleaned results files. Recommended default is True

    """

    gnps_network = data_import.import_gnps_network(parameters)

    for cluster in nx.connected_components(gnps_network):
        if len(cluster) >= parameters.min_gnps_cluster_size:
            target_mass_list = []
            cluster_id = gnps_network.nodes[list(cluster)[0]]["componentindex"]
            # Create gnps mass list
            for node in cluster:
                node_mass = gnps_network.nodes[node]["parent mass"]
                if parameters.remove_duplicates:
                    # Only add unique masses to the mass list
                    insert_mass = True
                    for mass in target_mass_list:
                        if mass - parameters.duplicate_mass_error <= node_mass <= mass + \
                                parameters.duplicate_mass_error:
                            insert_mass = False
                    if insert_mass:
                        target_mass_list.append(node_mass)
                else:
                    # else add all masses
                    target_mass_list.append(node_mass)
            # if gnps mass list contains appropriate number of members, perform Atlas annotation
            if parameters.min_gnps_cluster_size <= len(target_mass_list) <= parameters.max_gnps_cluster_size:
                atlas_compound_list = return_compounds(target_mass_list, parameters, atlas_df)
                compound_network = create_networks.match_compound_network(atlas_compound_list)
                if len(list(compound_network.nodes)) > 0:
                    create_networks.export_gnps_graphml(compound_network, cluster_id, parameters)
            print("Finished Atlas annotation for GNPS cluster " + str(cluster_id))


