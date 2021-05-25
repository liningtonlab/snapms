from pathlib import Path
from typing import List

# Defaults
DEFAULT_ADDUCT_LIST = [
    "m_plus_h",
    "m_plus_na",
    "m_plus_nh4",
    "m_plus_h_minus_h2o",
    "m_plus_k",
    "2m_plus_h",
    "2m_plus_na",
]


class Parameters:
    """Class containing all of the setup parameters from SNAP-MS"""

    def __init__(
        self,
        file_path: Path,
        atlas_db_path: Path,
        output_path: Path,
        ppm_error: int = 10,
        adduct_list: List[str] = DEFAULT_ADDUCT_LIST,
        remove_duplicates: bool = True,
        min_gnps_size: int = 3,
        max_gnps_size: int = 5000,
        min_atlas_size: int = 3,
        min_group_size: int = 3,
    ):
        self.file_path = file_path
        # pathlib.Path gives convenient methods for getting name and extension
        self.file_name = file_path.stem
        self.file_type = file_path.suffix.lstrip(".").lower()
        self.reference_db = atlas_db_path
        self.output_path = output_path
        self.sample_output_path = self.sample_output_directory_path()
        self.ppm_error = ppm_error
        self.adduct_list = adduct_list
        self.remove_duplicates = remove_duplicates
        self.min_gnps_cluster_size = min_gnps_size
        self.max_gnps_cluster_size = max_gnps_size
        self.min_atlas_annotation_cluster_size = min_atlas_size
        self.min_compound_group_count = min_group_size

    def sample_output_directory_path(self) -> Path:
        file_path = self.output_path / f"{self.file_name}_output"
        file_path.mkdir(exist_ok=True, parents=True)
        return file_path
