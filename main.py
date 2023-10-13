import argparse
import csv
import datetime
import json
import os
import pathlib
import re
import sys
from datetime import datetime

import mdformat
import requests
from mysoc_dataset import get_dataset_url
from opml import OpmlDocument

import lookup.sparql.police
import make_dataset

# TODO: Non-Home Office forces: MDP, BTP, CNC, etc
# - Partially done - querying from CSV file works but wikidata queries need work
# TODO: Get Disclosure Log URLs: Have Emailed MyDemocracy
# TODO: Reduce the replication in this script.
# - Doing this ad-hoc while I decide whether to maintain this or refactor it


document: OpmlDocument = OpmlDocument(
    title='United Kingdom Police Forces and Associated Bodies',
    owner_name='Mike Johnson',
    owner_email='mdj.uk@pm.me')

# Prepare a file to use for the generated output
markdown_output_file = open('output/overview.md', 'wt')


def get_csv_dataset_from_mysociety():
    # get the url of dataset
    url = get_dataset_url(repo_name="wdtk_authorities_list",
                          package_name="whatdotheyknow_authorities_dataset",
                          version_name="latest",
                          file_name="authorities.csv",
                          done_survey=True)
    if args.devmode:
        print(url)

    r = requests.get(url)
    tmpfile = open('authorities.csv', 'wb')
    tmpfile.write(r.content)
    tmpfile.close()


def generate_header():
    body = "# Generated List of Police Forces (WikiData/WhatDoTheyKnow) \n\n"
    body += "**Depending on the sources from which it was generated, this list may not include certain forces** \n"
    body += "**It is generated from data provided by WhatDoTheyKnow. If there are inaccuracies, please contact** \n"
    body += "**them with corrections. The table below will then be corrected when the script is next run.** \n\n"
    body += "[OPML File Available](https://github.com/m-d-johnson/wdtk-linkgenerator/blob/master/police.opml) \n\n"
    body += "|Organisation Name|Website|WDTK Org Page|WDTK JSON|Atom Feed|JSON Feed|Publication Scheme|FOI Email| \n"
    body += "|-|-|-|-|-|-|-|-| "
    return body


def process_mysociety_dataset():
    # Open CSV file and read it into the list of rows
    print("Process mysociety dataset")
    rows = []
    with open('authorities.csv', 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        for row in csvreader:
            rows.append(row)

        all_orgs = open("all.md", "w", encoding="utf-8")
        all_orgs.write(f"|Long Name|Short Name|Tags|")
        all_orgs.write(f"\n")
        # all_orgs.write("|-|-|-|")
    for row in rows:
        tags_list = re.split(r"\|", row[4])
        long_name = row[1]
        short_name = row[3]
        tags_list_flattened = str(tags_list)
        all_orgs.write(f"|{long_name}|{short_name}|{tags_list_flattened}|")

        # for i in tags_list:
        #     print(i)
        # print(tags_list[1])

    # id,           name,               short-name,         url-name,     tags
    # home-page,    publication-scheme, disclosure-log,     notes,
    # created-at,   updated-at,         version,            defunct,
    # categories,   top-level-categories,   single-top-level-category


def make_table_from_generated_dataset():
    json_input_file = open('data/generated-dataset.json', 'r')
    json_dataset = json.load(json_input_file)

    markdown_output_file.write(generate_header() + "\n")
    results = []
    for force in json_dataset:
        entry = f"|{force['Name']} | "
        entry += f"[Website]({force['Home_Page_URL']})|"
        entry += f"[wdtk page]({force['WDTK_Org_Page_URL']})|"
        entry += f"[wdtk json]({force['WDTK_Org_JSON_URL']})|"
        entry += f"[wdtk atom feed]({force['WDTK_Atom_Feed_URL']})|"
        entry += f"[wdtk json feed]({force['WDTK_JSON_Feed_URL']})|"
        entry += f"[Publication Scheme]({force['Publication_Scheme_URL']})|"
        entry += f"[FOI Email](mailto:{force['FOI_Email_Address']})|"
        entry += "\n"

        results.append(entry)

        document.add_rss(f"{force['Name']} FOI Disclosures",
                         f"{force['WDTK_Atom_Feed_URL']}",
                         version='RSS2',
                         created=datetime.now())

    results.sort()
    for i in results:
        markdown_output_file.write(str(i))


def cleanup(retain):
    document.dump('output/police.opml', pretty=True)
    filepath = pathlib.Path("output/overview.md")
    mdformat.file(filepath)

    if os.path.exists("output/authorities.csv") and retain is True:
        print("Not deleting the authorities file")
    elif os.path.exists("output/authorities.csv") and retain is False:
        os.remove("output/authorities.csv")
    else:
        print("The WDTK CSV file does not exist, so could not be deleted.")

    if os.path.exists('output/out.md'):
        os.unlink('output/out.md')
    os.link('output/overview.md', 'output/out.md')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate overview of police forces.')
    parser.add_argument('--generate',
                        dest='automatic',
                        default='True',
                        action='store_true',
                        help='Generate a dataset from the emails file, then build table.')
    parser.add_argument('--regenerate',
                        dest='regenerate',
                        default='False',
                        action='store_true',
                        help='Rebuilds a dataset from the emails file, then build table.')
    parser.add_argument('-r', '--retain',
                        action='store_true',
                        dest='retain', default=False,
                        help='Keep the authorities file from MySociety.')
    parser.add_argument('-w', '--wikidata',
                        action='store_true',
                        dest='wikidata', default=False,
                        help='Get a listing of local forces from wikidata.')
    args = parser.parse_args()

    if args.regenerate:
        make_dataset.rebuild_dataset()
        make_table_from_generated_dataset()
        markdown_output_file.close()
        cleanup(args.retain)
        sys.exit()
    if args.automatic:
        make_table_from_generated_dataset()
        markdown_output_file.close()
        cleanup(args.retain)
        sys.exit()
    if args.wikidata:
        lookup.sparql.police.get_local_police_forces_wikidata()
