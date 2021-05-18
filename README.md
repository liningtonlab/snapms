# snapms
core code for the SNAP MS platform for predicting identities of natural products from MS data

## Installation

Minimally, `conda env create -f environment.yml` will create a new conda environment named snapms.

One key installation detail is that you must modify py2cytoscape to make it compatible with modern versions of networkx. Open util_networkx.py and on line 108 change ‘g.node‘ to ‘g.nodes’.

~~Another detail is that there is currently (05012020) a bug in the latest version of networkx (2.5) that stops graph files from opening properly. Works if you install 2.4 instead.~~ (Fixed)

## Changelog

- Changed os.path -> pathlib
- Changed Atlas TSV -> JSON
- Stripped "compound_" from Atlas download columns
- Changed "accurate_mass" to "exact_mass" (Exact = theoretical calculated)