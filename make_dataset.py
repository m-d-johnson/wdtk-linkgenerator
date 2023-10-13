import json
from policeorganisation import PoliceOrganisation


def rebuild_dataset():
    # Generates a JSON dataset from two pieces of information - the WDTK ID and
    # the list of FOI email addresses. The rest of the information can be either
    # derived from the WDTK ID or scraped using the WDTK ID.
    emails = json.load(open("data/foi-emails.json", "r"))
    list_of_forces = []

    for entry in emails:
        force = PoliceOrganisation(entry, emails)
        list_of_forces.append(force.__dict__)

    outfile = open('data/generated-dataset.json', 'w')
    outfile.write(json.dumps(list_of_forces, indent=4))
    outfile.close()
