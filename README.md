# wdtk-linkgenerator: Generate an overview of certain organisations that [WhatDoTheyKnow](https://whatdotheyknow.com) monitors.

## Purpose

This repo contains some scripts that work with data provided by [MySociety](https://www.mysociety.org/). It generates an
overview of police forces in the United Kingdom.

There is also some code in here that provides minimal support for generating overview tables of the entire WDTK list of
public bodies. It is not yet suitable for use.

It also generates an OPML file which can be imported to a Feed Reader to monitor all FOI requests and updates that the
WDTK site knows about.

This set of scripts has been written for a specific project and will likely not be maintained.

## Usage

- Not on PyPI, clone this repo and run the scripts.
- Please install `requirements.txt` dependencies first.
- Developed using Python 3.8 on Windows 11.
- `python3 ./main.py --generate` - Rebuilds tables from existing `generated-dataset.json`.
- `python3 ./main.py --refresh` - Rebuilds `generated-dataset.json` from the `foi-emails.json` file and rebuilds tables.

## Output Files

- output/overview.md: Overview of UK Police Forces.
- output/police.opml: OPML files containing RSS feeds for all forces in the generated table.
- output/all-mysociety.md: Simple table of all public bodies on WhatDoTheyKnow.

## Input Files

- data/foi-emails.json: Maps FOI email addresses to WDTK organisations by their 'URL Names'. Manually curated and
  required to regenerate the `generated-dataset.json` file.
- data/police.json: Data from WikiData on UK Police Forces in JSON format.
- data/wdtk-police.csv: Mapping of full names of police forces to the `URL Name` (Unmaintained).
- data/wikidata-police-forces.json: Simple JSON mapping WikiData IDs to WDTK `URL Name`s (unmaintained).
- output/wikidata-localpolice.csv: From WikiData - Mapping homepages to WDTK `URL Name`s.

## Information derived from the WDTK 'URL Name'

Much of the information listed in the tables is simply derived from the unique ID that WDTK uses - a string they call
the `URL Name` as it's used in the URL. It's a unique identifier as far as I can tell, or at least has been for this
purpose. A simple substitution yields the correct information for:

- The body's page on the WDTK site: https://www.whatdotheyknow.com/body/{name_of_org}
- The Atom feed of requests, updates, etc for a particular body: https://www.whatdotheyknow.com/feed/body/{name_of_org}
- A JSON representation of metadata about the body: https://www.whatdotheyknow.com/feed/body/{name_of_org}.json

# Other information

- Tags are available from the JSON data available per-body and also in the CSV that's downloaded from MySociety.
- FOI Emails are not programmatically available and are kept in a file.