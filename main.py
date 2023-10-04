import json
import sys


def process_one_file(json_file_name):
    fh = open(json_file_name, 'r')
    imported_json = json.load(fh)
    print("# Generated List of Police Forces (WikiData/WhatDoTheyKnow)")
    print("*This list of of Home Office (Territorial) Forces and does not yet include certain forces*")
    print("\n")
    print("|Organisation Name|Website|WDTK Org Page|WDTK JSON|Atom Feed|JSON Feed|")
    print("|-|-|-|-|-|-|")
    results = []
    for item in imported_json:
        name_of_org = str(item['itemLabel'])
        url = str(item['website'])
        wdtk = str(item['wdtk'])
        row = f"|{name_of_org} | "
        row += f"[Website]({url})|"
        row += f"[wdtk page](https://www.whatdotheyknow.com/body/{wdtk})|"
        row += f"[wdtk json](https://www.whatdotheyknow.com/body/{wdtk}.json)|"
        row += f"[wdtk atom feed](https://www.whatdotheyknow.com/feed/body/{wdtk})|"
        row += f"[wdtk json feed](https://www.whatdotheyknow.com/feed/body/{wdtk}.json)|"
        # print(row)
        results.append(row)

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
