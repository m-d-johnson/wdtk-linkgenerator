import argparse
import csv
import datetime
import json
import os
import pathlib
import re
import sys
from datetime import datetime
from tabulate import tabulate
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


document = OpmlDocument(
    title='United Kingdom Home Office (Territorial) Police Forces and Associated Bodies',
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
    body = "# Generated List of Police Forces (WikiData/WhatDoTheyKnow) \n\n"

    body += "**Depending on the sources from which it was generated, this list may not include certain forces** \n"
    body += "**It is generated from data provided by WhatDoTheyKnow. If there are inaccuracies, please contact** \n"
    body += "**them with corrections. The table below will then be corrected when the script is next run.** \n\n"

    body += "[OPML File Available](https://github.com/m-d-johnson/wdtk-linkgenerator/blob/master/police.opml) \n\n"

    body += "Police authorities in England and Wales were abolished in November 2012, and replaced with directly \n"
    body += "elected police and crime commissioners, and those in Scotland were merged in April 2013 to form the \n"
    body += "Scottish Police Authority as part of the creation of Police Scotland, the single police force for \n"
    body += "Scotland. The Police Service of Northern Ireland is overseen by the Northern Ireland Policing Board, \n"
    body += "and two of the three UK-wide special police forces continue to be overseen by individual police \n"
    body += "authorities. The oversight of the two police forces serving London continues to be implemented via \n"
    body += "unique arrangements.\n\n"

    body += "|Organisation Name|Website|WDTK Org Page|WDTK JSON|Atom Feed|JSON Feed|Publication Scheme|FOI Email| \n"
    body += "|-|-|-|-|-|-|-|-| "
    return body


def process_mysociety_dataset():
    """This function is not used."""
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

    # 0. id
    # 1. name
    # 2. short-name
    # 3. url-name
    # 4. tags
    # 5. home-page
    # 6. publication-scheme
    # 7. disclosure-log
    # 8. notes
    # 9. created-at
    # 10. updated-at
    # 11. version
    # 12. defunct
    # 13. categories
    # 14. top-level-categories
    # 15. single-top-level-category


def make_table_from_generated_dataset():
    json_input_file = open('data/generated-dataset.json', 'r')
    json_dataset = json.load(json_input_file)

    markdown_output_file.write(generate_header() + "\n")
    results = []
    for force in json_dataset:
        if not force['Is_Defunct']:
            entry = f"|{force['Name']} | "
            entry += f"[Website]({force['Home_Page_URL']})|"
            entry += f"[wdtk page]({force['WDTK_Org_Page_URL']})|"
            entry += f"[wdtk json]({force['WDTK_Org_JSON_URL']})|"
            entry += f"[atom feed]({force['WDTK_Atom_Feed_URL']})|"
            entry += f"[json feed]({force['WDTK_JSON_Feed_URL']})|"
            entry += f"[Link]({force['Publication_Scheme_URL']})|"
            entry += f"[Email](mailto:{force['FOI_Email_Address']})|"
            entry += "\n"

            results.append(entry)

            document.add_rss(f"{force['Name']} FOI Disclosures",
                             f"{force['WDTK_Atom_Feed_URL']}",
                             version='RSS2',
                             created=datetime.now())

    # For ease of reading, sort the rows alphabetically before
    # we proceed to writing them to a file.
    results.sort()
    # Then, write the rows to the file and close it. The header has already been
    # written.
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

    if os.path.exists('output/out.md'):
        os.unlink('output/out.md')
    os.link('output/overview.md', 'output/out.md')
    results.sort()
    for i in results:
        markdown_output_file.write(str(i))


# wdtk page: https://www.whatdotheyknow.com/body/{name_of_org}
# wdtk atom feed: https://www.whatdotheyknow.com/feed/body/{name_of_org}
# wdtk json feed: https://www.whatdotheyknow.com/feed/body/{name_of_org}.json

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate overview of police forces.')
    parser.add_argument('--generate',
                        dest='generate',
                        default='True',
                        action='store_true',
                        help='Generate a dataset from the emails file, then build table.')
    parser.add_argument('--refresh',
                        dest='refresh',
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
    if args.wikidata:
        lookup.sparql.police.get_local_police_forces_wikidata()
