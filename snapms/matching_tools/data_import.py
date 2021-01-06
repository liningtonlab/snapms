#

"""Tools to import peak lists or gnps networks to SNAP-MS"""

import os
import networkx as nx


def import_gnps_network(parameters):
    """Import the original GNPS network file (graphML) downloaded from the GNPS output site"""

    with open(parameters.file_path) as f:
        import_network = nx.read_graphml(f)

    if nx.is_directed(import_network):
        gnps_network = import_network.to_undirected()
    else:
        gnps_network = import_network

    return gnps_network


