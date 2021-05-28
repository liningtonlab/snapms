from pathlib import Path
from django_rq import job
from time import sleep
from snapms import Parameters, create_gnps_network_annotations, network_from_mass_list


@job("high")
def test_job():
    print("Waiting...")
    sleep(15)
    return 1 + 1


@job("high")
def run_snapms_masslist(params: Parameters, job_id: str) -> None:
    print("Running SnapMS for ", job_id)
    sleep(15)


@job("default")
def run_snapms_gnps(params: Parameters, job_id: str) -> None:
    print("Running SnapMS for ", job_id)
    sleep(15)
