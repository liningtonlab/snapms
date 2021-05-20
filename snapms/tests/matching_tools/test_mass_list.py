from snapms.matching_tools.mass_list import remove_mass_duplicates


def test_remove_duplicates_no_overlap():
    mass_list = [
        420.1421,
        422.1585,
        438.1752,
        440.133,
        454.1481,
        474.2021,
        491.0763,
        492.213,
    ]
    assert remove_mass_duplicates(mass_list, 10.0) == mass_list


def test_remove_duplicates_overlap_large_ppm_error():
    mass_list = [
        420.1421,
        422.1585,
        438.1752,
        440.133,
        454.1481,
        474.2021,
        491.0763,
        492.213,
    ]
    expected = [420.1421, 438.1752, 454.1481, 474.2021, 491.0763]
    assert remove_mass_duplicates(mass_list, 5000.0) == expected
