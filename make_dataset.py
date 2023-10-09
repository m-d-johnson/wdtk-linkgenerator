import json
import requests
from bs4 import BeautifulSoup

emails = json.load(open("data/foi-emails.json", "r"))


class PoliceOrganisation:
    """Creates a new WDTK body from a WDTK ID and a dict containing FOI emails.

    The FOI emails dict has keys with the value of the WDTK ID and values of
    """
    def __init__(self, wdtk_id, emails):
        """Creates a WDTK Body from a WDTK ID."""
        self.WDTK_Org_JSON_URL = f"https://www.whatdotheyknow.com/body/{wdtk_id}.json"
        wdtk_data = requests.get(self.WDTK_Org_JSON_URL).json()
        self.Name = wdtk_data["name"]
        self.WDTK_ID = wdtk_id
        self.Home_Page_URL = wdtk_data["home_page"]
        self.WDTK_Org_Page_URL = f"https://www.whatdotheyknow.com/body/{wdtk_id}"
        self.WDTK_Atom_Feed_URL = f"https://www.whatdotheyknow.com/feed/body/{wdtk_id}"
        self.WDTK_JSON_Feed_URL = (
            f"https://www.whatdotheyknow.com/feed/body/{wdtk_id}.json"
        )
        self.Publication_Scheme_URL = wdtk_data["publication_scheme"]
        self.FOI_Email_Address = emails[wdtk_id]

        for tag in wdtk_data["tags"]:
            if tag[0] == "dpr":
                self.Data_Protection_Registration_Identifier = tag[1]
            if tag[0] == "wikidata":
                self.WikiData_Identifier = tag[1]
            if tag[0] == "lcnaf":
                self.LoC_Authority_ID = tag[1]

        soupreq = requests.get(self.WDTK_Org_Page_URL)
        soup = BeautifulSoup(soupreq.text, "html.parser")
        for link in soup.find_all("a"):
            if link.getText() == "Disclosure log":
                self.Disclosure_Log_URL = link.get("href")


list_of_forces = []

for entry in emails:
    force = PoliceOrganisation(entry, emails)
    list_of_forces.append(force.__dict__)

outfile = open('data/generated-dataset.json', 'w')
outfile.write(json.dumps(list_of_forces, indent=4))
outfile.close()