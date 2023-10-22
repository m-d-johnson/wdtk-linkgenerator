import argparse
import csv
import json
import os
import pathlib
import re
import sys

import mdformat
import requests
from mysoc_dataset import get_dataset_url
from opml import OpmlDocument
from tabulate import tabulate

import make_dataset
import reports

# TODO: Reduce the replication in this script.
# - Doing this ad-hoc while I decide whether to maintain this or refactor it


document = OpmlDocument(
    title="WhatDoTheyKnow FOI: UK Police Forces and Associated Bodies",
    owner_name="Mike Johnson",
    owner_email="mdj.uk@pm.me",
    )

# Prepare a file to use for the generated output
markdown_output_file = open("output/overview.md", "wt")


def get_csv_dataset_from_mysociety():
    # get the url of dataset
    url = get_dataset_url(
        repo_name="wdtk_authorities_list",
        package_name="whatdotheyknow_authorities_dataset",
        version_name="latest",
        file_name="authorities.csv",
        done_survey=True,
        )

    r = requests.get(url)
    tmpfile = open("authorities.csv", "wb")
    tmpfile.write(r.content)
    tmpfile.close()


def generate_header():
    body = "# Generated List of Police Forces (WhatDoTheyKnow)\n\n\n"
    body += "**Generated from data provided by WhatDoTheyKnow. Please contact\n"
    body += "them with corrections. This table will be corrected when the "
    body += "script next runs.**\n\n"
    body += "[OPML File](police.opml)\n\n"
    body += (
        "|Body|Website|WDTK Page|JSON|Feed: Atom|Feed: JSON|Publication "
        "Scheme|Disclosure Log|Email|\n"
        )
    body += "|-|-|-|-|-|-|-|-|-|\n"
    return body


def process_mysociety_dataset():
    """This function does nothing useful. Is not used."""
    # Open CSV file and read it into the list of rows
    print("Process mysociety dataset")
    rows = []
    with open("authorities.csv", "r", encoding="utf-8") as csvfile:
        csvreader = csv.DictReader(csvfile)
        # extracting each data row one by one
        for row in csvreader:
            rows.append(row)

    # markdown_output_file.write(generate_header() + "\n")

    output_rows = []
    rowheaders = ["Name", "WDTK ID", "Tags"]

    for row in rows:
        thisrow = []
        tags_list = re.split(r"\|", row["tags"])
        tags_list_flattened = str(tags_list)
        thisrow.append(row["name"])
        thisrow.append(row["url-name"])
        thisrow.append(str(tags_list_flattened))
        output_rows.append(thisrow)

    all_orgs = open("output/all-mysociety.md", "w", encoding="utf-8")
    all_orgs.write(tabulate(output_rows, headers=rowheaders, tablefmt="github"))
    all_orgs.flush()


def make_table_from_generated_dataset():
    json_input_file = open("data/generated-dataset.json", "r")
    dataset = json.load(json_input_file)

    markdown_output_file.write(generate_header())
    results = []
    for force in dataset:
        if not force["Is_Defunct"]:
            markup = f"|{force['Name']} | "
            markup += f"[Website]({force['Home_Page_URL']})|"
            markup += f"[wdtk page]({force['WDTK_Org_Page_URL']})|"
            markup += f"[wdtk json]({force['WDTK_Org_JSON_URL']})|"
            markup += f"[atom feed]({force['WDTK_Atom_Feed_URL']})|"
            markup += f"[json feed]({force['WDTK_JSON_Feed_URL']})|"
            if force["Publication_Scheme_URL"]:
                markup += f"[Link]({force['Publication_Scheme_URL']})|"
            else:
                markup += f"Missing|"
            if force["Disclosure_Log_URL"]:
                markup += f"[Link]({force['Disclosure_Log_URL']})|"
            else:
                markup += f"Missing|"
            markup += f"[Email](mailto:{force['FOI_Email_Address']})|"
            markup += f"\n"

            results.append(markup)

            document.add_rss(
                f"{force['Name']} FOI Disclosures",
                f"{force['WDTK_Atom_Feed_URL']}",
                version="RSS2",
                )

    # For ease of reading
    results.sort()

    for row_of_markup in results:
        markdown_output_file.write(str(row_of_markup))


def cleanup(retain):
    document.dump("output/police.opml", pretty=True)
    filepath = pathlib.Path("output/overview.md")
    mdformat.file(filepath)

    if os.path.exists("output/authorities.csv") and retain is True:
        print("Not deleting the authorities file")
    elif os.path.exists("output/authorities.csv") and retain is False:
        os.remove("output/authorities.csv")
    else:
        print("The WDTK CSV file does not exist, so could not be deleted.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate overview of police forces.")
    parser.add_argument(
        "--report",
        dest="report",
        default="False",
        action="store_true",
        help="Generate a report of missing Pub Scheme and Disc. Log URLs.",
        )
    parser.add_argument(
        "--generate",
        dest="generate",
        default="True",
        action="store_true",
        help="Generate a dataset from the emails file, then build table.",
        )
    parser.add_argument(
        "--refresh",
        dest="refresh",
        default="False",
        action="store_true",
        help="Rebuilds a dataset from the emails file, then build table.",
        )
    parser.add_argument(
        "-r",
        "--retain",
        action="store_true",
        dest="retain",
        default=False,
        help="Keep the authorities file from MySociety.",
        )
    parser.add_argument(
        "-w",
        "--wikidata",
        action="store_true",
        dest="wikidata",
        default=False,
        help="Get a listing of local forces from wikidata.",
        )
    parser.add_argument(
        "--mysociety",
        action="store_true",
        dest="mysociety",
        default=False,
        help="Get all the mysociety data and create a table.",
        )
    args = parser.parse_args()

    print("Args: report = ", args.report)
    print("Args: mysociety = ", args.mysociety)
    print("Args: refresh = ", args.refresh)
    print("Args: generate = ", args.generate)

    if args.report is True:
        reports.generate_problem_reports()
        sys.exit()
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
    if args.generate is True:
        make_table_from_generated_dataset()
        markdown_output_file.close()
        cleanup(args.retain)
        sys.exit()

