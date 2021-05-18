#!/usr/bin/env python3

"""Tools to import and reformat NP Atlas data"""

import unicodedata
from typing import List

import pandas as pd


def import_atlas(parameters):
    """Import Atlas data from Advanced search output, and reformat as a pandas df with cleaned headers and additional
    adducts (if selected)
    """
    # input_df = pd.read_csv(
    #     parameters.reference_db, sep="\t", header=0, encoding="utf-8"
    # )
    input_df = normalize_dataframe(pd.read_json(parameters.reference_db))
    # clean_headers(input_df) # shouldn't be needed
    clean_names(input_df)
    extend_adducts(input_df)
    # add back url
    input_df["npaid"] = input_df.npaid.apply(lambda x: f"NPA{x:06d}")
    input_df["npatlas_url"] = input_df.npaid.apply(
        lambda x: f"https://www.npatlas.org/explore/compounds/{x}"
    )
    print("Finished NP Atlas data import")
    print(input_df.head(2))
    return input_df


def normalize_dataframe(
    df: pd.DataFrame, cols: List[str] = ["origin_reference", "origin_organism"]
):
    """Normalize columns for nested JSON/dict data inside a dataframe"""
    df = df.copy()
    for c in cols:
        a = pd.json_normalize(df[c], sep="_")
        names = [f"{c}_{x}" for x in a.columns]
        df[names] = a
        del df[c]
    return df


def clean_names(df: pd.DataFrame, name_col: str = "name") -> None:
    """Perform unicode normalization on compound names"""
    df[name_col] = [unicodedata.normalize("NFKC", n) for n in df[name_col]]


def clean_headers(df: pd.DataFrame) -> None:
    """Tidy up headers in dataframe containing whitespace"""

    df.columns = (
        c.strip().lower().replace(" ", "_").replace("(", "").replace(")", "")
        for c in df.columns
    )


def extend_adducts(atlas_df: pd.DataFrame) -> None:
    """Tool to include additional adducts in Atlas dataframe, beyond m_plus_h and m_plus_na provided in Atlas download"""

    atlas_df["m_plus_nh4"] = atlas_df["exact_mass"] + 18.033823
    atlas_df["m_plus_h_minus_h2o"] = atlas_df["exact_mass"] - 17.00328
    atlas_df["m_plus_k"] = atlas_df["exact_mass"] + 38.963158
    atlas_df["2m_plus_h"] = (2 * atlas_df["exact_mass"]) + 1.007276
    atlas_df["2m_plus_na"] = (2 * atlas_df["exact_mass"]) + 22.989218
