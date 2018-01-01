import click
import json

from csv import DictWriter

state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Washington DC": "DC",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY"
}


def add_state_abbrev(record):
    return {
        **record,
        "state_abbrev": state_to_abbrev[record["state"]]
    }


@click.command()
@click.argument('raw_json_input_file', type=click.File('r'))
@click.argument('output_file', type=click.File('w'))
def main(raw_json_input_file, output_file):
    
    # Parse the JSON.
    raw_records = map(json.loads, raw_json_input_file)

    # Add the state abbreviation.
    records_state_abbrev = map(add_state_abbrev, raw_records)

    # TODO: geocode.

    # Initialize the writer.
    writer = DictWriter(output_file, fieldnames=[
        "location",
        "state",
        "country",
        "city",
        "description",
        "state_abbrev"
    ])

    writer.writeheader()

    for record in records_state_abbrev:
        writer.writerow(record)

if __name__ == "__main__":
    main()