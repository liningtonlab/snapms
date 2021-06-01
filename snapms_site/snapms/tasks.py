import shutil
from django_rq import job
from time import sleep
from snapms import (
    Parameters,
    create_gnps_network_annotations,
    network_from_mass_list,
    import_atlas,
)
from .models import Job, Status


def cleanup_job(params: Parameters, status: Status = Status.completed):
    # remove input file
    params.file_path.unlink()
    if status == Status.failed:
        shutil.rmtree(params.output_path)


def mark_status(job_id: str, status: Status):
    job = Job.objects.get(id=job_id)
    job.status = status.value
    job.save()


def run_snapms(snapms_fn, params, job_id):
    print("Running SnapMS for ", job_id)
    atlas = import_atlas(params)
    try:
        snapms_fn(atlas, params)
        cleanup_job(params)
        sleep(5)
        print("Completed SnapMS for ", job_id)
        mark_status(job_id, Status.completed)
    except Exception as e:
        print("SnapMS failed for ", job_id)
        print(e)
        mark_status(job_id, Status.failed)
        cleanup_job(params, Status.failed)


@job("high")
def run_snapms_masslist(params: Parameters, job_id: str) -> None:
    run_snapms(network_from_mass_list, params, job_id)


@job("default")
def run_snapms_gnps(params: Parameters, job_id: str) -> None:
    run_snapms(create_gnps_network_annotations, params, job)
