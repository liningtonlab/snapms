#!/usr/bin/env python3

"""Tools to import and reformat NP Atlas data"""

import unicodedata
from typing import List

import pandas as pd

from snapms.config import Parameters
from snapms.exceptions import AdductNotFound


def import_atlas(parameters: Parameters):
    """Import Atlas data from Advanced search output, and reformat as a pandas df with cleaned headers and additional
    adducts (if selected)
    """
    # input_df = pd.read_csv(
    #     parameters.reference_db, sep="\t", header=0, encoding="utf-8"
    # )
    input_df = normalize_dataframe(pd.read_json(parameters.reference_db))
    # clean_headers(input_df) # shouldn't be needed with JSON input
    input_df = clean_names(input_df)
    input_df = extend_adducts(input_df, parameters.adduct_list)
    print("Finished NP Atlas data import")
    return input_df


def normalize_dataframe(
    df: pd.DataFrame, cols: List[str] = ["origin_reference", "origin_organism"]
) -> pd.DataFrame:
    """Normalize columns for nested JSON/dict data inside a dataframe
    NOTE: These data are currently not used by snapms.
    """
    df = df.copy()
    for c in cols:
        a = pd.json_normalize(df[c], sep="_")
        names = [f"{c}_{x}" for x in a.columns]
        df[names] = a
        del df[c]
    return df


def clean_names(df: pd.DataFrame, name_col: str = "name") -> pd.DataFrame:
    """Perform unicode normalization on compound names"""
    df[name_col] = [unicodedata.normalize("NFKC", n) for n in df[name_col]]
    return df


def clean_headers(df: pd.DataFrame) -> pd.DataFrame:
    """Tidy up headers in dataframe containing whitespace"""
    df.columns = (
        c.strip().lower().replace(" ", "_").replace("(", "").replace(")", "")
        for c in df.columns
    )
    return df


def adduct_compute(exact_mass: pd.Series, name: str) -> pd.Series:
    """Compute the adduct mass given and pandas series.
    To add new adducts, simply add a new `if name == 'new_adduct_name'` statement.
    Returns a new series.

    This method should also work for pure floats/ints or numpy arrays, but is not tested for them.

    Raises AdductNotFound if adduct name not recognized.
    """
    if name == "m_plus_nh4":
        return exact_mass + 18.033823
    if name == "m_plus_h_minus_h2o":
        return exact_mass - 17.00328
    if name == "m_plus_k":
        return exact_mass + 38.963158
    if name == "2m_plus_h":
        return (2 * exact_mass) + 1.007276
    if name == "2m_plus_na":
        return (2 * exact_mass) + 22.989218
    raise AdductNotFound("Adduct not recognized")


def extend_adducts(atlas_df: pd.DataFrame, adduct_list: List[str]) -> pd.DataFrame:
    """Tool to include additional adducts in Atlas dataframe, beyond m_plus_h and m_plus_na provided in Atlas download"""
    for adduct_name in adduct_list:
        # skip pre-computed values
        if adduct_name in ["m_plus_h", "m_plus_na"]:
            continue
        atlas_df[adduct_name] = adduct_compute(atlas_df["exact_mass"], adduct_name)
    return atlas_df
