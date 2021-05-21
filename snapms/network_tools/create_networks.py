#!/usr/bin/env python3

"""Tools to create networks of various types for SNAP-MS platform"""

from pathlib import Path
from typing import List, Dict

import networkx as nx
import numpy as np

from rdkit import Chem, DataStructs
from rdkit.Chem import AllChem
from snapms.matching_tools.CompoundMatch import CompoundMatch
from snapms.network_tools import cytoscape as cy


def tanimoto_matrix(smiles_list: List[str]) -> List[List[float]]:
    """Creates square matrix of Tanimoto scores for all SMILES strings in the input list"""
    fingerprints = [
        AllChem.GetMorganFingerprint(Chem.MolFromSmiles(compound), 2)
        for compound in smiles_list
    ]
    matrix = [DataStructs.BulkDiceSimilarity(fp, fingerprints) for fp in fingerprints]

    return matrix


def match_compound_network(compound_match_list: List[CompoundMatch]) -> nx.Graph:
    """Tool to create a network illustrating relatedness of candidate structures for masses in a GNPS cluster
    Requires the output list from matching_tools.match_compounds.return_compounds

    """

    # Similarity score required to create an edge in the network graph
    tanimoto_cutoff = 0.66

    # Create a list of just the SMILES strings, for the Tanimoto grid generation
    smiles_list = [c.smiles for c in compound_match_list]

    tanimoto_grid = tanimoto_matrix(smiles_list)

    # Create network graph
    compound_graph = nx.Graph()

    # Add compound nodes. index_group_dict indicates which compound group each compound derives from.
    # Used to prevent inclusion of edges between compounds from the same group
    # (i.e. candidates for the same original mass)
    node_list = []
    index_group_dict = {}
    for index, compound in enumerate(compound_match_list):
        node_list.append(
            (
                index,
                {
                    "npaid": compound.npaid,
                    "exact_mass": compound.exact_mass,
                    "smiles": compound.smiles,
                    "compound_name": compound.friendly_name(),
                    "npatlas_url": compound.npatlas_url,
                    "original_gnps_mass": compound.mass,
                    "compound_group": compound.compound_number,
                    "adduct": compound.adduct,
                },
            )
        )
        index_group_dict[index] = compound.compound_number
    compound_graph.add_nodes_from(node_list)

    # Add edges if above Dice threshold and not between compounds in the same compound group
    # (i.e. compounds that are included because they are candidates for the same original mass from GNPS)
    edge_list = []
    for row_idx, row in enumerate(tanimoto_grid):
        for col_idx, value in enumerate(row):
            if row_idx == col_idx:
                continue
            if (
                value >= tanimoto_cutoff
                and index_group_dict[row_idx] != index_group_dict[col_idx]
            ):
                edge_list.append((row_idx, col_idx))
    compound_graph.add_edges_from(edge_list)

    return compound_graph


def export_graphml(graph, parameters):
    """Exports networkx graph from match_compound_network as graphML for use in external visualization tools"""

    if graph_size_check(graph, parameters):
        output_filename = f"{parameters.file_name}_snapms_output.graphml"
        nx.write_graphml(graph, parameters.output_path / output_filename)


def export_gnps_graphml(graph, cluster_id, parameters):
    """Exports networkx graph from match_compound_network for each gnps cluster, with cluster id in filename as graphML"""

    # Pathlib
    parameters.sample_output_path.mkdir(exist_ok=True)

    nx.write_graphml(
        graph,
        parameters.sample_output_path / f"GNPS_componentindex_{cluster_id}.graphml",
    )


def insert_atlas_clusters_to_cytoscape(parameters):
    """Tool to create a new collection in an existing Cytoscape file, and to append all Atlas GNPS annotation networks
    as separate network views.

    Currently the GNPS file to which networks will be added must be open in the Cytoscape desktop program in a single
    session.
    Tested with Cytoscape 3.8

    """
    # Open connection to cytoscape client
    # cy = CyRestClient()

    # Start new session (currently not implemented)

    # Import original gnps network (currently not implemented)

    # Open each Atlas annotation network in turn. Glob function includes [0-9] in order to exclude the modified original
    # gnps network (if present)
    for network in sorted(
        parameters.sample_output_path.glob("*[0-9].graphml"),
        key=extract_cluster_id,
    ):
        with open(network, encoding="utf-8") as f:
            atlas_graph = nx.read_graphml(f)

        network_title = Path(network).stem
        print("Starting insertion of " + network_title + " to GNPS network file")

        if graph_size_check(atlas_graph, parameters):
            # Remove subgraphs that do not have the minimum required number of nodes. Useful for removing large
            # numbers of small clusters containing just one or two Atlas compounds
            nodes_to_include = []
            for subgraph in nx.connected_components(atlas_graph):
                if len(subgraph) >= parameters.min_atlas_annotation_cluster_size:
                    nodes_to_include.extend(subgraph)
            nodes_to_remove = np.setdiff1d(atlas_graph.nodes(), nodes_to_include)
            for removed_node in nodes_to_remove:
                atlas_graph.remove_node(removed_node)

            # Insert atlas annotation graphs in to cytoscape file, provided they are still an appropriate size
            if graph_size_check(atlas_graph, parameters):
                # Annotate subgraphs to find those subgraphs which are top candidates for the correct compound
                # family
                annotate_top_candidates(atlas_graph)

                # Insert Atlas annotation graph to Cytoscape file
                # insert_network = cy.network.create_from_networkx(
                #     atlas_graph,
                #     name=network_title,
                #     collection="NP Atlas GNPS annotation collection",
                # )
                # cy.layout.apply(name="hierarchical", network=insert_network)

                # undirected = cy.style.create("Undirected")
                max_compound_group = int(
                    max(dict(atlas_graph.nodes(data="compound_group")).values())
                )
                # Update graph
                # undirected.update_defaults(new_defaults)
                # Apply mapping
                # undirected.create_passthrough_mapping(column='name', col_type='String', vp='NODE_LABEL')
                # color_gradient = StyleUtil.create_3_color_gradient(
                #     min=1,
                #     mid=mid_compound_group,
                #     max=max_compound_group,
                #     colors=("#fbe723", "#21918C", "#440256"),
                # )
                # undirected.create_continuous_mapping(
                #     column="compound_group",
                #     vp="NODE_FILL_COLOR",
                #     col_type="String",
                #     points=color_gradient,
                # )
                # cy.style.apply(undirected, network=insert_network)
            else:
                print(
                    "After sub-graph size filter, no clusters remain that possess the minimum number of nodes. "
                    "Skipping network insertion"
                )
        else:
            print(
                f"ERROR: Atlas annotation graph {network_title} either too small or too large. "
                "Skipping insert."
            )


def extract_cluster_id(filepath):
    """Tool to extract the GNPS componentindex (i.e. cluster id) from the Atlas annotation cluster filename.
    Used to sort the Atlas networks so that they are processed and inserted into the Cytoscape file in numerical order

    """
    filename = Path(filepath).stem
    cluster_id = int(filename.rsplit("_")[-1])
    return cluster_id


def graph_size_check(G: nx.Graph, parameters) -> bool:
    """Assess overall size of networkx graphs. Used to skip graphs that are too small or too large, or that have become
    too small after filtering steps

    """

    max_node_count = 2000
    max_edge_count = 10000

    # Assess the results graph to make sure that at least one subgraph contains the minimum number of compound groups
    # and that the nodes and edges do not violate max limits
    group_counts = get_compound_group_count(G)
    max_compound_group_count = max(group_counts.values())
    if (
        max_compound_group_count >= parameters.min_compound_group_count
        and parameters.min_atlas_annotation_cluster_size
        <= len(nx.nodes(G))
        < max_node_count
        and len(nx.edges(G)) < max_edge_count
    ):
        return True
    else:
        return False


def compound_group_counter(G: nx.Graph) -> int:
    """Count the number of unique compound groups in any graph or subgraph
    Makes sure the graph nodes have compound_group values
    """
    compound_groups = set(
        nd
        for _, node_data in G.nodes(data=True)
        if (nd := node_data.get("compound_group")) is not None
    )

    return len(compound_groups)


def get_compound_group_count(G: nx.Graph) -> Dict[int, int]:
    """Compute the compound group count in any subgraph in the main graph.

    Returns a dictionary with subgraph index key and count value
    """
    counts = {}
    for idx, subgraph in enumerate(nx.connected_components(G)):
        S = G.subgraph(subgraph)
        counts[idx] = compound_group_counter(S)
    return counts


def annotate_top_candidates(G: nx.Graph, group_counts: Dict[int, int]) -> None:
    """Annotate subgraphs as top candidate answers, based on maximum compound group counts within each subgraph
    in the network. In other words, if three answers all have four compound groups and this is the highest compound
    group count, then these three answers are all equally likely to be correct.

    Requires graph and pre-computed group count dictionary.
    """
    # globally set top_candidate attribute to False
    nx.set_node_attributes(G, values=False, name="top_candidate")

    max_group_count = max(group_counts.values())
    for idx, subgraph in enumerate(nx.connected_components(G)):
        if group_counts[idx] == max_group_count:
            print(f"Subgraph {idx} is a top candidate")
            nx.set_node_attributes(
                G, values={nid: True for nid in subgraph}, name="top_candidate"
            )
