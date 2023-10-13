import json
from policeorganisation import PoliceOrganisation


def rebuild_dataset():
    emails = json.load(open("data/foi-emails.json", "r"))

    list_of_forces = []

    for entry in emails:
        force = PoliceOrganisation(entry, emails)
        list_of_forces.append(force.__dict__)

    outfile = open('data/generated-dataset.json', 'w')
    outfile.write(json.dumps(list_of_forces, indent=4))
    outfile.close()
