# snapms
core code for the SNAP MS platform for predicting identities of natural products from MS data

## Installation

Minimally, `conda env create -f environment.yml` will create a new conda environment named snapms.

Requires Python 3.8 or greater.

~~One key installation detail is that you must modify py2cytoscape to make it compatible with modern versions of networkx. Open util_networkx.py and on line 108 change ‘g.node‘ to ‘g.nodes’.~~ (Fixed by writing own cytoscape module)


~~Another detail is that there is currently (05012020) a bug in the latest version of networkx (2.5) that stops graph files from opening properly. Works if you install 2.4 instead.~~ (Patched)

## Changelog

- Changed os.path -> pathlib
- Changed Atlas TSV -> JSON
- Stripped "compound_" from Atlas download columns
- Changed "accurate_mass" to "exact_mass" (Exact = theoretical calculated)

## Django App

This repo includes an example Django App for Snap MS. Some configuration is required.

Environment file (`.env`)
```
REDIS_URI=redis://localhost:6379/0
CYTOSCAPE_DATADIR=/root/data
SNAPMS_DATADIR=/home/jvansan/git/snapms/data
NPATLAS_FILE=/home/jvansan/git/snapms/data/atlas_input/npatlas_v202006.json
```

The `SNAPMS_DATADIR` MUST exist already and the `NPATLAS_FILE` MUST also be available.

Running the development server requires two instances.

1. Django App

```
dotenv run ./manage.py runserver
```

2. RQ worker

```
dotenv run ./manage.py rqworker high default low
```

## Requirements

1. Redis - Docker

You can easily start Redis in a docker container locally with 

```
docker run -itd -p 6379:6379 --name snapms-redis redis
```

2. Cytoscape

Cytoscape automation requires a running instance. You can run it on the desktop, but on a server
it will be easier to run it in a docker container. The CyREST runs on port 1234.

For cytoscape session file serving to work, the mounted volume should point to the same place as the 
`SNAPMS_DATADIR`.

In development, I often use the `./data` as my `SNAPMS_DATADIR`.

```
docker run --name cy -itd -v $(pwd)/data/testing:/root/data -p 1234:1234 jvansan/cytoscape-desktop-headless:latest
```

## Docker deployment

In this repo is a `docker-compose.yml` file which shows how to deploy this example app using Traefik as a reverse proxy.
In a real production environment, you should NOT use the build in Django `runserver`.

__TODO:__

- Change 