import datetime
import json
import sys
import requests
from datetime import datetime
import csv
from mysoc_dataset import get_dataset_url, get_dataset_df
import pandas as pd


def get_dataset():
    # get the url of dataset
    url = get_dataset_url(
        repo_name="wdtk_authorities_list",
        package_name="whatdotheyknow_authorities_dataset",
        version_name="latest",
        file_name="authorities.csv",
    )

    # # get a pandas dataframe
    # df = get_dataset_df(
    #     repo_name="wdtk_authorities_list",
    #     package_name="whatdotheyknow_authorities_dataset",
    #     version_name="latest",
    #     file_name="authorities.parquet",
    # )
    r = requests.get(url)
    open('authorities.csv', 'wb').write(r.content)

    with open('authorities.csv', 'rt', encoding="utf8") as csvfile:
        data = pd.read_csv(csvfile)
        org_dataset = data.to_dict('records')

    for org in org_dataset:
        # id,               name,       short-name,
        # tags,             home-page,  publication-scheme
        # disclosure-log,   notes,      created-at
        # updated-at,       version,    defunct
        # categories,       url-name,   top-level-categories
        #                               single-top-level-category
        name = org['name']
        home_page = str(org['home-page'])
        url_name = org['url-name']
        disclosure_log = str(org['disclosure-log'])
        print(name, home_page, url_name, disclosure_log)


# TODO: Non-Home Office forces: MDP, BTP, CNC, etc
# TODO: Get Disclosure Log URLs: Need to talk to MyDemocracy
# TODO: Reduce the replication in this script: It's a quick and dirty tool for something.

from opml import OpmlDocument

document = OpmlDocument(
    title='United Kingdom Home Office (Territorial) Police Forces and Associated Bodies',
    owner_name='Mike Johnson',
    owner_email='mdj.uk@pm.me'
)


def print_header():
    print("# Generated List of Police Forces (WikiData/WhatDoTheyKnow)")
    print("*This list may not yet include certain forces*")
    print("\n")
    print("[OPML File Available](https://github.com/m-d-johnson/wdtk-linkgenerator/blob/master/police.opml)")
    print("\n")

    print("|Organisation Name|Website|WDTK Org Page|WDTK JSON|Atom Feed|JSON Feed|Publication Scheme|")
    print("|-|-|-|-|-|-|-|")


def process_one_csv_file(csv_file_name):
    rows = []
    results = []
    # reading csv file
    with open(csv_file_name, 'r') as csvfile:
        # creating a csv reader object
        csvreader = csv.reader(csvfile)
        # extracting each data row one by one
        for row in csvreader:
            rows.append(row)
    print_header()
    for row in rows:
        name_of_org = row[0]
        wdtk = row[1]
        url = f"https://www.whatdotheyknow.com/body/{wdtk}"
        pubscheme = url
        response = requests.get(f"https://www.whatdotheyknow.com/body/{wdtk}.json")
        wdtk_data = response.json()
        if wdtk_data['publication_scheme']:
            pubscheme = wdtk_data['publication_scheme']
        else:
            pubscheme = "https://whatdotheyknow.com/"
        if wdtk_data['home_page']:
            url = wdtk_data['home_page']
        else:
            url = "https://whatdotheyknow.com/"

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


# wdtk page: https://www.whatdotheyknow.com/body/{name_of_org}
# wdtk atom feed: https://www.whatdotheyknow.com/feed/body/{name_of_org}
# wdtk json feed: https://www.whatdotheyknow.com/feed/body/{name_of_org}.json


def process_one_json_file(json_file_name):
    fh = open(json_file_name, 'r')
    imported_json = json.load(fh)

    results = []
    print_header()
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


# wdtk page: https://www.whatdotheyknow.com/body/{name_of_org}
# wdtk atom feed: https://www.whatdotheyknow.com/feed/body/{name_of_org}
# wdtk json feed: https://www.whatdotheyknow.com/feed/body/{name_of_org}.json

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    for filename in sys.argv[1:]:
        # process_one_json_file(filename)
        # process_one_csv_file(filename)
        get_dataset()
