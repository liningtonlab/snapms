FROM condaforge/mambaforge

WORKDIR /usr/src/app

COPY environment.yml ./
RUN mamba env create -f environment.yml
# RUN mamba install -n snapms gunicorn

COPY snapms /usr/src/app/snapms
COPY snapms_site /usr/src/app/snapms_site
COPY manage.py .

# Required environment variables with some recommended defaults
# Requires mounting the datadir to /usr/src/app/data
ENV CYTOSCAPE_DATADIR=/root/data
ENV CYTOSCAPE_BASEURL=http://localhost:1234/v1
ENV NPATLAS_FILE=/usr/src/app/data/NPAtlas_download.json
ENV COCONUT_FILE=/usr/src/app/data/COCONUT_download.json
ENV REDIS_URI=redis://localhost:6379/0
ENV SNAPMS_DATADIR=/usr/src/app/data

EXPOSE 8000
CMD [ "mamba", "run", "-n", "snapms", "--no-capture-output", "python", "manage.py", "runserver", "0.0.0.0:8000" ]