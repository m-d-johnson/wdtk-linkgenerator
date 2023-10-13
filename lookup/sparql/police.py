"""Generate a CSV list of police force WhatDoTheyKnow IDs from Wikidata."""
from SPARQLWrapper import SPARQLWrapper, JSON


def get_local_police_forces_wikidata():
    """Query WikiData for police forces and generate a CSV file from the results."""
    # UK Local Police Forces
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setQuery("""
    SELECT DISTINCT ?item ?itemLabel ?website ?websiteLabel ?wdtkid WHERE {
      SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE]". }
      {
        SELECT DISTINCT ?item ?itemLabel ?website ?wdtkid WHERE {
          ?item p:P8167 ?statement0.
          ?statement0 ps:P8167 _:anyValueP8167.
          ?item wdt:P856 ?website;
            wdt:P8167 ?wdtkid.
          {
            ?item p:P31 ?statement1.
            ?statement1 (ps:P31/(wdt:P279*)) wd:Q3907564.
          }
        }
        LIMIT 5000
      }
    }
    """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    output_file = open("output/wikidata-localpolice.csv", "w")

    for result in results["results"]["bindings"]:
        row = ",".join([result["wdtkid"]["value"], result["website"]["value"]])
        row += "\n"
        output_file.write(row)

    output_file.close()


get_local_police_forces_wikidata()
