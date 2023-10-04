import datetime
import json
import sys
import requests
from datetime import datetime

# TODO: Non-Home Office forces
# TODO: Get Disclosure Log URLs

from opml import OpmlDocument

document = OpmlDocument(
    title='United Kingdom Police Forces and Associated Bodies',
    owner_name='Mike Johnson',
    owner_email='mdj.uk@pm.me'
)


def process_one_file(json_file_name):
    fh = open(json_file_name, 'r')
    imported_json = json.load(fh)
    print("# Generated List of Police Forces (WikiData/WhatDoTheyKnow)")
    print("*This list of Home Office (Territorial) Forces and does not yet include certain forces*")
    print("\n")
    print("[OPML File Available](https://github.com/m-d-johnson/wdtk-linkgenerator/blob/master/police.opml)")
    print("\n")

    print("|Organisation Name|Website|WDTK Org Page|WDTK JSON|Atom Feed|JSON Feed|Publication Scheme|")
    print("|-|-|-|-|-|-|-|")
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


# wdtk page: https://www.whatdotheyknow.com/body/{name_of_org}
# wdtk atom feed: https://www.whatdotheyknow.com/feed/body/{name_of_org}
# wdtk json feed: https://www.whatdotheyknow.com/feed/body/{name_of_org}.json

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    for filename in sys.argv[1:]:
        process_one_file(filename)
