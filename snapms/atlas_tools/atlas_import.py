#!/usr/bin/env python3

"""Tools to import and reformat NP Atlas data"""

import pandas as pd


def import_atlas(parameters):
    """Import Atlas data from Advanced search output, and reformat as a pandas df with cleaned headers and additional
    adducts (if selected)

    """

    input_df = pd.read_csv(parameters.reference_db, sep='\t', header=0)
    clean_headers(input_df)
    input_df = extend_adducts(input_df)
    print("Finished NP Atlas data import")

    return input_df


def clean_headers(dataframe):
    """Tidy up headers in dataframe containing whitespace"""

    dataframe.columns = dataframe.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '') \
        .str.replace(')', '')

    return dataframe


def extend_adducts(atlas_df):
    """Tool to include additional adducts in Atlas dataframe, beyond m_plus_h and m_plus_na provided in Atlas download

    """

    atlas_df['compound_m_plus_nh4'] = atlas_df['compound_accurate_mass'] + 18.033823
    atlas_df['compound_m_plus_h_minus_h2o'] = atlas_df['compound_accurate_mass'] - 17.00328
    atlas_df['compound_m_plus_k'] = atlas_df['compound_accurate_mass'] + 38.963158
    atlas_df['compound_2m_plus_h'] = (2 * atlas_df['compound_accurate_mass']) + 1.007276
    atlas_df['compound_2m_plus_na'] = (2 * atlas_df['compound_accurate_mass']) + 22.989218

    return atlas_df
