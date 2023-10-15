import requests


class PoliceOrganisation:
    """Creates a new WDTK body from a WDTK ID and a dict containing FOI emails.

    The FOI emails dict is required, and has keys matching the WDTK 'URL name'
    and values of the email address of the FOI officer/department.
    See `data/foi-emails.json`
    e.g.

    {
     "the_met": "dpo@met.police.pnn.uk",
     "gmp": "dpo@gmp.police.pnn.uk"
     etc.
    }

    """

    def __init__(self, wdtk_id, emails):
        """Creates a WDTK Body from a WDTK ID."""
        # Defaults
        self.Is_Defunct = False
        # Attributes derived from the WDTK Url Name:
        self.WDTK_ID = wdtk_id
        self.WDTK_Org_JSON_URL = f"https://www.whatdotheyknow.com/body/{wdtk_id}.json"
        self.WDTK_Atom_Feed_URL = f"https://www.whatdotheyknow.com/feed/body/{wdtk_id}"
        self.WDTK_Org_Page_URL = f"https://www.whatdotheyknow.com/body/{wdtk_id}"
        self.WDTK_JSON_Feed_URL = (
            f"https://www.whatdotheyknow.com/feed/body/{wdtk_id}.json"
            )

        # Attributes obtained from querying the site API:
        wdtk_data = requests.get(self.WDTK_Org_JSON_URL).json()
        self.Disclosure_Log_URL = wdtk_data["disclosure_log"]
        self.Home_Page_URL = wdtk_data["home_page"]
        self.Name = wdtk_data["name"]
        self.Publication_Scheme_URL = wdtk_data["publication_scheme"]

        for tag in wdtk_data["tags"]:
            if tag[0] == "dpr":
                self.Data_Protection_Registration_Identifier = tag[1]
            if tag[0] == "wikidata":
                self.WikiData_Identifier = tag[1]
            if tag[0] == "lcnaf":
                self.LoC_Authority_ID = tag[1]
            if tag[0] == "defunct":
                self.Is_Defunct = True

        # Email addresses come from a different place.
        self.FOI_Email_Address = emails[wdtk_id]
