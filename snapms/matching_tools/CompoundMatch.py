import re
from dataclasses import dataclass


@dataclass
class CompoundMatch:
    """Class for handling compound matches between query adduct mass and NP Atlas"""

    npaid: str
    exact_mass: float
    smiles: str
    name: str
    mass: float
    compound_number: int
    adduct: str

    @property
    def npatlas_url(self) -> str:
        return f"https://www.npatlas.org/explore/compounds/{self.npaid}"

    def friendly_name(self) -> str:
        """JvS - This should no longer be required with unicode normalization on atlas import
        but there are still some issues
        Elementree has some problems reading special characters from the Atlas input because the input is
        occasionally not clean UTF-8. This if/ else statement cleans up names to eliminate crashes due to string
        parsing failure from the graphML file."""
        if re.match(
            "^[A-Za-z0-9 α-ωΑ-Ω\-‐~,\"'$&*()±\[\]′’+./–″<>−{}|_:;]+$", self.name
        ):
            return self.name
        else:
            return ""
