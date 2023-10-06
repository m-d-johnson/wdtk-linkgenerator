import datetime
import json
import sys
import requests
from datetime import datetime
import csv
from mysoc_dataset import get_dataset_url, get_dataset_df
import pandas as pd
import mdformat
import pathlib

from opml import OpmlDocument


def get_csv_dataset():
    # get the url of dataset
    url = get_dataset_url(
        repo_name="wdtk_authorities_list",
        package_name="whatdotheyknow_authorities_dataset",
        version_name="latest",
        file_name="authorities.csv",
    )
    r = requests.get(url)
    open('authorities.csv', 'wb').write(r.content)

    # with open('authorities.csv', 'rt', encoding="utf8") as csvfile:
    #     data = pd.read_csv(csvfile)
    #     org_dataset = data.to_dict('records')

    # for org in org_dataset:


# id,               name,       short-name,
# tags,             home-page,  publication-scheme
# disclosure-log,   notes,      created-at
# updated-at,       version,    defunct
# categories,       url-name,   top-level-categories
#                               single-top-level-category
# name = org['name']
# home_page = str(org['home-page'])
# url_name = org['url-name']
# disclosure_log = str(org['disclosure-log'])


# TODO: Non-Home Office forces: MDP, BTP, CNC, etc
# TODO: Get Disclosure Log URLs: Need to talk to MyDemocracy
# TODO: Reduce the replication in this script: It's a quick and dirty tool for something.


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
    # Prepare a file to put the out
    table_output_file = open('overview.md', 'wt')
    rows = []
    results = []
    # reading csv file
    with open(csv_file_name, 'r') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            rows.append(row)
    document: OpmlDocument = OpmlDocument(
        title='United Kingdom Home Office (Territorial) Police Forces and Associated Bodies',
        owner_name='Mike Johnson',
        owner_email='mdj.uk@pm.me'
    )
    table_output_file.write(generate_header() + "\n")

    for row in rows:
        name_of_org = row[0]
        wdtk = row[1]
        url = f"https://www.whatdotheyknow.com/body/{wdtk}"
        pubscheme = url  # Setting this to fall back upon if it's not provided.
        response = requests.get(f"{url}.json")
        wdtk_data = response.json()

        if wdtk_data['publication_scheme']:
            pubscheme = wdtk_data['publication_scheme']
        else:
            pubscheme = url  # Just redirect to overview page

        # If they've provided a home page, use that. Else, leave it set to the WDTK overview.
        if wdtk_data['home_page']:
            url = wdtk_data['home_page']

        entry = ''
        entry += f"|{name_of_org} | "
        entry += f"[Website]({url})|"
        entry += f"[wdtk page](https://www.whatdotheyknow.com/body/{wdtk})|"
        entry += f"[wdtk json](https://www.whatdotheyknow.com/body/{wdtk}.json)|"
        entry += f"[atom feed](https://www.whatdotheyknow.com/feed/body/{wdtk})|"
        entry += f"[json feed](https://www.whatdotheyknow.com/feed/body/{wdtk}.json)|"
        entry += f"[Publication Scheme]({pubscheme})|"
        entry += "\n"
        results.append(entry)

        feed = document.add_rss(
            f"{name_of_org} FOI Disclosures",
            f"https://www.whatdotheyknow.com/feed/body/{wdtk}",
            version='RSS2',
            created=datetime.now()
        )

    document.dump('police.opml', pretty=True)

    results.sort()
    for i in results:
        table_output_file.write(str(i))
        table_output_file.flush()
    table_output_file.close()

    filepath = pathlib.Path("overview.md")
    mdformat.file(filepath)




def process_one_json_file(json_file_name):
    fh = open(json_file_name, 'r')
    imported_json = json.load(fh)

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
            pubscheme = "https://whatdotheyknow.com/"

        row = f"|{name_of_org} | "
        row += f"[Website]({url})|"
        row += f"[wdtk page](https://www.whatdotheyknow.com/body/{wdtk})|"
        row += f"[wdtk json](https://www.whatdotheyknow.com/body/{wdtk}.json)|"
        row += f"[wdtk atom feed](https://www.whatdotheyknow.com/feed/body/{wdtk})|"
        row += f"[wdtk json feed](https://www.whatdotheyknow.com/feed/body/{wdtk}.json)|"
        row += f"[Publication Scheme]({pubscheme})|"
        results.append(row)

        feed = document.add_rss(
            f"{name_of_org} FOI Disclosures",
            f"https://www.whatdotheyknow.com/feed/body/{wdtk}",
            version='RSS2',
            created=datetime.now()
        )

    document.dump('police.opml', pretty=True)

    results.sort()
    for i in results:
        print(i)


if __name__ == '__main__':
    for filename in sys.argv[1:]:
        if filename.endswith('.json'):
            process_one_json_file(filename)
        elif filename.endswith('.csv'):
            get_csv_dataset()
            process_one_csv_file(filename)
