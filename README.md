# snapms
core code for the SNAP MS platform for predicting identities of natural products from MS data

# Installation
Full instructions coming soon.

One key installation detail is that you must modify py2cytoscape to make it compatible with modern versions of networkx. Open util_networkx.py and on line 108 change ‘g.node‘ to ‘g.nodes’
Another detail is that there is currently (05012020) a bug in the latest version of networkx (2.5) that stops graph files from opening properly. Works if you install 2.4 instead