import csv
import json
from pathlib import Path

from django.conf import settings
from django.http import HttpRequest, HttpResponse
from django.http.response import HttpResponseBadRequest, HttpResponseNotAllowed
from django.shortcuts import render
from django.utils.datastructures import MultiValueDictKeyError

from snapms.config import Parameters

from .models import Job, Status
from .tasks import run_snapms_gnps, run_snapms_masslist


def docs(request: HttpRequest) -> HttpResponse:
    """View for docs page"""
    context = dict(page_name="SnapMS Documentation")
    return render(request, "docs.html", context)


def dashboard(request: HttpRequest) -> HttpResponse:
    """View for dashboard page"""
    context = dict(page_name="SnapMS")
    return render(request, "dashboard.html", context)


def handle_snapms(request: HttpRequest) -> HttpResponse:
    """Handle post of SnapMS passing to handler function"""
    if request.method == "POST":
        return handle_snapms_request(request)
    return HttpResponseNotAllowed(["POST"])


### Helper functions
def handle_snapms_request(request: HttpRequest) -> HttpResponse:
    """Method for handling work of creating a new job and passing to worker queue"""
    # from collections import defaultdict

    # data = defaultdict(str)
    data = json.loads(request.POST["metadata"])
    # Try to get the file
    try:
        upload_file = request.FILES["file"]
    except MultiValueDictKeyError:
        upload_file = None
    # Create Job
    job = Job.objects.create(
        inputfile=upload_file or "masslist",
        parameters=json.dumps(data),
    )
    job_id = str(job.id)
    # Setup job directory
    job_dir = Path(settings.SNAPMS_DATADIR) / job_id
    job_dir.mkdir()
    # If no upload_file, convert masslist to csv file
    # If upload_file, save to jobdir
    if upload_file is not None:
        input_file = job_dir.joinpath(upload_file.name)
        with input_file.open("wb") as f:
            for chunk in upload_file.chunks():
                f.write(chunk)
    else:
        input_file = save_convert_masslist(data["masslist"], job_dir)

    parameters = Parameters(
        file_path=input_file,
        atlas_db_path=settings.NPATLAS_FILE,
        output_path=job_dir / "output",
        ppm_error=data["ppm_error"],
        adduct_list=data["adduct_list"],
        remove_duplicates=data["remove_duplicates"],
        min_gnps_size=data["min_gnps_size"],
        max_gnps_size=data["max_gnps_size"],
        min_atlas_size=data["min_atlas_size"],
        min_group_size=data["min_group_size"],
    )
    if parameters.file_type == "csv":
        run_snapms_masslist.delay(parameters, job_id)
    elif parameters.file_type == "graphml":
        run_snapms_gnps.delay(parameters, job_id)
    elif parameters.file_type == "cys":
        return HttpResponseBadRequest("Cytoscape import is not yet supported")
    else:
        return HttpResponseBadRequest("Input file format not supported")
    job_id = "FAKE"
    return HttpResponse(json.dumps(dict(success=True, job_id=job_id)))


def save_convert_masslist(masslist: str, job_dir: Path) -> Path:
    """Take a masslist for the front end and convert to a CSV file, returning the Path"""
    mfile = job_dir / "mass_list.csv"
    with mfile.open("w") as f:
        csvwriter = csv.writer(f)
        csvwriter.writerow(["m/z"])
        csvwriter.writerows([[float(x)] for x in masslist.split("\n") if x])
    return mfile
