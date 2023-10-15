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
from tabulate import tabulate

import make_dataset

# TODO: Non-Home Office forces: MDP, BTP, CNC, etc
# - Partially done - querying from CSV file works but wikidata queries need work
# TODO: Reduce the replication in this script.
# - Doing this ad-hoc while I decide whether to maintain this or refactor it


document = OpmlDocument(
    title='FOI: UK Police Forces and Associated Bodies',
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

    r = requests.get(url)
    tmpfile = open('authorities.csv', 'wb')
    tmpfile.write(r.content)
    tmpfile.close()


def generate_header():
    body = """
    # Generated List of Police Forces (WikiData/WhatDoTheyKnow) \n\n
    
    **This list is generated from data provided by WhatDoTheyKnow.**
    **If there are inaccuracies, please contact with corrections.**
    **This table will then be corrected when the script next runs**
    
    [OPML File]("https://github.com/m-d-johnson/wdtk-linkgenerator/blob
    /master/police.opml)
    
    
    Police authorities in England and Wales were abolished in November 2012, 
    and 
    replaced with directly elected police and crime commissioners. Those in 
    Scotland
    were merged in April 2013 to form the Scottish Police Authority as part 
    of the
    creation of Police Scotland, the single police force for Scotland.
    The Police Service of Northern Ireland is overseen by the Northern Ireland 
    Policing Board, and two of the three UK-wide UK-wide special police forces 
    continue to be overseen by individual police authorities. Oversight of 
    the two
    police forces serving London continues to be implemented via other 
    arrangements.
    
    |Body|Website|WDTK Page|JSON|Feed: Atom|Feed: JSON|Publication Scheme|Email|
    |-|-|-|-|-|-|-|-|
    """
    return body


def process_mysociety_dataset():
    """This function does nothing useful. Is not used."""
    # Open CSV file and read it into the list of rows
    print("Process mysociety dataset")
    rows = []
    with open('authorities.csv', 'r', encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        # extracting each data row one by one
        for row in csvreader:
            rows.append(row)

    # markdown_output_file.write(generate_header() + "\n")

    output_rows = []
    rowheaders = ['Name', 'WDTK ID', 'Tags']

    for row in rows:
        thisrow = []
        tags_list = re.split(r"\|", row['tags'])
        tags_list_flattened = str(tags_list)
        thisrow.append(row['name'])
        thisrow.append(row['url-name'])
        thisrow.append(str(tags_list_flattened))
        output_rows.append(thisrow)

    all_orgs = open("output/all-mysociety.md", "w", encoding="utf-8")
    all_orgs.write(tabulate(output_rows, headers=rowheaders, tablefmt="github"))
    all_orgs.flush()


def make_table_from_generated_dataset():
    json_input_file = open('data/generated-dataset.json', 'r')
    dataset = json.load(json_input_file)

    markdown_output_file.write(generate_header())
    results = []
    for force in dataset:
        if not force['Is_Defunct']:
            markup = f"|{force['Name']} | "
            markup += f"[Website]({force['Home_Page_URL']})|"
            markup += f"[wdtk page]({force['WDTK_Org_Page_URL']})|"
            markup += f"[wdtk json]({force['WDTK_Org_JSON_URL']})|"
            markup += f"[atom feed]({force['WDTK_Atom_Feed_URL']})|"
            markup += f"[json feed]({force['WDTK_JSON_Feed_URL']})|"
            markup += f"[Link]({force['Publication_Scheme_URL']})|"
            markup += f"[Email](mailto:{force['FOI_Email_Address']})|"
            markup += f"\n"

            results.append(markup)

            document.add_rss(f"{force['Name']} FOI Disclosures",
                             f"{force['WDTK_Atom_Feed_URL']}",
                             version='RSS2',
                             created=datetime.now())

    # For ease of reading
    results.sort()

    for row_of_markup in results:
        markdown_output_file.write(str(row_of_markup))


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


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Generate overview of police forces.')
    parser.add_argument('--generate',
                        dest='generate',
                        default='True',
                        action='store_true',
                        help='Generate a dataset from the emails file, '
                             'then build table.')
    parser.add_argument('--refresh',
                        dest='refresh',
                        default='False',
                        action='store_true',
                        help='Rebuilds a dataset from the emails file, '
                             'then build table.')
    parser.add_argument('-r', '--retain',
                        action='store_true',
                        dest='retain', default=False,
                        help='Keep the authorities file from MySociety.')
    parser.add_argument('-w', '--wikidata',
                        action='store_true',
                        dest='wikidata', default=False,
                        help='Get a listing of local forces from wikidata.')
    parser.add_argument('--mysociety',
                        action='store_true',
                        dest='mysociety', default=False,
                        help='Get all the mysociety data and create a table.')
    args = parser.parse_args()

    if args.mysociety:
        get_csv_dataset_from_mysociety()
        process_mysociety_dataset()
        sys.exit()
    if args.refresh:
        make_dataset.rebuild_dataset()
        make_table_from_generated_dataset()
        markdown_output_file.close()
        cleanup(args.retain)
        sys.exit()
    if args.generate:
        make_table_from_generated_dataset()
        markdown_output_file.close()
        cleanup(args.retain)
        sys.exit()
