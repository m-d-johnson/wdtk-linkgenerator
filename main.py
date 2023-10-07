import argparse
import csv
import datetime
import json
import os
import pathlib
from datetime import datetime

import mdformat
import requests
from mysoc_dataset import get_dataset_url
from opml import OpmlDocument

# TODO: Non-Home Office forces: MDP, BTP, CNC, etc
# TODO: Get Disclosure Log URLs: Need to talk to MyDemocracy
# TODO: Reduce the replication in this script.


document: OpmlDocument = OpmlDocument(
    title='United Kingdom Police Forces and Associated Bodies',
    owner_name='Mike Johnson',
    owner_email='mdj.uk@pm.me')

# Prepare a file to use for the generated output
markdown_output_file = open('overview.md', 'wt')


def get_csv_dataset():
    # get the url of dataset
    url = get_dataset_url(repo_name="wdtk_authorities_list",
                          package_name="whatdotheyknow_authorities_dataset",
                          version_name="latest",
                          file_name="authorities.csv",
                          done_survey=True)
    r = requests.get(url)
    open('authorities.csv', 'wb').write(r.content)


def generate_header():
    body = "# Generated List of Police Forces (WikiData/WhatDoTheyKnow) \n\n"
    body += "*Depending on the sources from which it was generated, this list may not include certain forces* \n"
    body += "*It is generated from data provided by WhatDoTheyKnow. If there are inaccuracies, please contact* \n"
    body += "*them with corrections. The table below will then be corrected when the script is next run.* \n\n"
    body += "[OPML File Available](https://github.com/m-d-johnson/wdtk-linkgenerator/blob/master/police.opml) \n\n"
    body += "|Organisation Name|Website|WDTK Org Page|WDTK JSON|Atom Feed|JSON Feed|Publication Scheme| \n"
    body += "|-|-|-|-|-|-|-| "
    return body


def process_one_csv_file(csv_file_name):
    # Open CSV file and read it into the list of rows
    rows = []
    with open(csv_file_name, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            rows.append(row)

    markdown_output_file.write(generate_header() + "\n")

    # Iterate over all the entries in the CSV import, and generate a row in a
    # Markdown table
    results = []
    for row in rows:
        name_of_org = row[0]
        wdtk = row[1]
        url = f"https://www.whatdotheyknow.com/body/{wdtk}"
        response = requests.get(f"{url}.json")
        wdtk_data = response.json()

        # If they've provided a link to a publication scheme, use that. Else,
        # leave it set to the WDTK overview.
        if wdtk_data['publication_scheme']:
            pubscheme = wdtk_data['publication_scheme']
        else:
            pubscheme = url  # Just redirect to overview page

        # If they've provided a home page, use that. Else, leave it set to the
        # WDTK overview.
        if wdtk_data['home_page']:
            url = wdtk_data['home_page']

        # Construct the row in the Markdown table
        entry = ''
        entry += f"|{name_of_org} | "
        entry += f"[Website]({url})|"
        entry += f"[wdtk page](https://www.whatdotheyknow.com/body/{wdtk})|"
        entry += f"[wdtk json](https://www.whatdotheyknow.com/body/{wdtk}.json)|"
        entry += f"[atom feed](https://www.whatdotheyknow.com/feed/body/{wdtk})|"
        entry += f"[json feed](https://www.whatdotheyknow.com/feed/body/{wdtk}.json)|"
        entry += f"[Publication Scheme]({pubscheme})|"
        entry += "\n"

        # results[] is a list of these rows. Append to it.
        results.append(entry)

        # Also add it to the list of RSS feeds
        document.add_rss(f"{name_of_org} FOI Disclosures",
                         f"https://www.whatdotheyknow.com/feed/body/{wdtk}",
                         version='RSS2',
                         created=datetime.now())

    # For ease of reading, sort the rows alphabetically before
    # we proceed to writing them to a file.
    results.sort()
    # Then, write the rows to the file and close it. The header has already been
    # written.
    for i in results:
        markdown_output_file.write(str(i))


def process_one_json_file(json_file_name):
    fh = open(json_file_name, 'r')
    imported_json = json.load(fh)
    markdown_output_file.write(generate_header() + "\n")

    results = []
    for item in imported_json:
        name_of_org = str(item['itemLabel'])
        url = str(item['website'])
        wdtk = str(item['wdtk'])
        response = requests.get(f'https://www.whatdotheyknow.com/body/{wdtk}.json')
        wdtk_data = response.json()
        if wdtk_data['publication_scheme']:
            pubscheme = wdtk_data['publication_scheme']
        else:
            pubscheme = f"https://whatdotheyknow.com/body/{wdtk}"

        entry = f"|{name_of_org} | "
        entry += f"[Website]({url})|"
        entry += f"[wdtk page](https://www.whatdotheyknow.com/body/{wdtk})|"
        entry += f"[wdtk json](https://www.whatdotheyknow.com/body/{wdtk}.json)|"
        entry += f"[wdtk atom feed](https://www.whatdotheyknow.com/feed/body/{wdtk})|"
        entry += f"[wdtk json feed](https://www.whatdotheyknow.com/feed/body/{wdtk}.json)|"
        entry += f"[Publication Scheme]({pubscheme})|"
        entry += "\n"

        results.append(entry)

        document.add_rss(f"{name_of_org} FOI Disclosures",
                         f"https://www.whatdotheyknow.com/feed/body/{wdtk}",
                         version='RSS2',
                         created=datetime.now())

    results.sort()
    for i in results:
        markdown_output_file.write(str(i))


def cleanup(retain):
    document.dump('police.opml', pretty=True)
    filepath = pathlib.Path("overview.md")
    mdformat.file(filepath)

    if os.path.exists("authorities.csv") and retain is True:
        print("Not deleting the authorities file")
    elif os.path.exists("authorities.csv") and retain is False:
        os.remove("authorities.csv")
    else:
        print("The WDTK CSV file does not exist, so could not be deleted.")

    if os.path.exists('out.md'):
        os.unlink('out.md')
    os.link('overview.md', 'out.md')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate overview of police forces.')
    parser.add_argument('--mode',
                        dest='mode',
                        choices=['csv', 'json'],
                        default='csv',
                        action='store')
    parser.add_argument('-j',
                        dest='jsonfile',
                        action='store')
    parser.add_argument('-r', '--retain',
                        action='store_true',
                        dest='retain', default=False)
    args = parser.parse_args()

    if args.mode == 'json' and args.jsonfile != '':
        print("JSON mode selected")
        process_one_json_file(args.jsonfile)
    elif args.mode == 'csv':
        print("CSV mode selected")
        # NB. While it looks like this script should download a file from WDTK
        # and use that as input, it doesn't yet do this. That's why there's a
        # hardcoded file path below and a file checked into the git repository.
        get_csv_dataset()
        process_one_csv_file('data/wdtk-police.csv')
    markdown_output_file.close()

    cleanup(args.retain)
