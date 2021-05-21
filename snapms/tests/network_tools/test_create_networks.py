from pathlib import Path

import networkx as nx
import pytest
from snapms.network_tools import create_networks

CWD = Path(__file__).parent


def load_test_graph() -> nx.Graph:
    """Load the test dataset file into a networkx graph"""
    return nx.read_graphml(CWD / "test_snapms.graphml")


def test_load_test_graph():
    """Test the helper function"""
    G = load_test_graph()
    assert isinstance(G, nx.Graph)
    assert len(G.nodes) == 63


def test_compound_group_counter_all_the_same():
    """Tests counting of compound groups when all values the same"""
    nodes = [
        (1, dict(compound_group=1)),
        (2, dict(compound_group=1)),
        (3, dict(compound_group=1)),
    ]
    G = nx.Graph()
    G.add_nodes_from(nodes)
    assert create_networks.compound_group_counter(G) == 1


def test_compound_group_counter_all_different():
    """Tests counting of compound groups when all values are different"""
    nodes = [
        (1, dict(compound_group=1)),
        (2, dict(compound_group=2)),
        (3, dict(compound_group=3)),
    ]
    G = nx.Graph()
    G.add_nodes_from(nodes)
    assert create_networks.compound_group_counter(G) == 3


def test_compound_group_counter_mixed():
    """Tests counting of compound groups when not some values are the same"""
    nodes = [
        (1, dict(compound_group=1)),
        (2, dict(compound_group=2)),
        (3, dict(compound_group=1)),
    ]
    G = nx.Graph()
    G.add_nodes_from(nodes)
    assert create_networks.compound_group_counter(G) == 2


def test_get_compound_group_count():
    """Tests the counting of unique compound_group's in the test dataset"""
    G = load_test_graph()
    counts = create_networks.get_compound_group_count(G)
    # fmt: off
    expected = {0: 1, 1: 1, 2: 1, 3: 1, 4: 1, 5: 2, 6: 1, 7: 1, 8: 3, 9: 1, 10: 1, 11: 1, 12: 2, 13: 2, 14: 1, 15: 1, 16: 1, 17: 1, 18: 1, 19: 2, 20: 1, 21: 2, 22: 3, 23: 1, 24: 1, 
25: 1, 26: 1, 27: 1, 28: 1, 29: 1, 30: 1, 31: 1, 32: 1, 33: 2, 34: 1, 35: 1, 36: 1, 37: 1, 38: 1, 39: 1, 40: 1}
    # fmt: on
    assert counts == expected


def test_annotate_top_candidates():
    """Test the annotation of a real dataset based on the rules surrounding top candidates"""
    G = load_test_graph()
    counts = create_networks.get_compound_group_count(G)
    expected_top_candidates = (8, 22)
    create_networks.annotate_top_candidates(G, counts)
    # make sure only the correct subgraphs were annotated
    candidate_data = nx.get_node_attributes(G, "top_candidate")
    for idx, sg in enumerate(nx.connected_components(G)):
        if idx in expected_top_candidates:
            assert all(candidate_data[c] == True for c in sg)
        else:
            assert all(candidate_data[c] == False for c in sg)


def test_extract_cluster_id():
    """Test extraction of cluster id from output filename"""
    fp = Path("GNPS_componentindex_1.graphml")
    assert create_networks.extract_cluster_id(fp) == 1


def test_extract_cluster_id_fails():
    """This function is expected to fail if the graphml file name does not end in an int"""
    fp = Path("GNPS_componentindex_AA.graphml")
    with pytest.raises(ValueError):
        assert create_networks.extract_cluster_id(fp)
