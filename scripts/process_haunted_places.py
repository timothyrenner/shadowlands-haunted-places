import click
import json
import logging
import csv

from toolz import get_in

STATE_TO_ABBREV = {
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


def load_location_cache(location_cache_file):
    return {
        (c[0], c[1], c[2]): get_in(
            ['results',0,'geometry','location'],
            json.loads(c[3]),
            None
        )
        for c in csv.reader(location_cache_file)
    }    


def load_city_cache(city_cache_file):
    return {
        (c[0], c[1]): get_in(
            ['results',0,'geometry','location'],
            json.loads(c[2]),
            None
        )
        for c in csv.reader(city_cache_file)
    }


@click.command()
@click.argument('haunted_place_file', type=click.File('r'))
@click.argument('location_cache_file', type=click.File('r'))
@click.argument('city_cache_file', type=click.File('r'))
@click.option(
    '-o', '--output-file',
    type=click.File('w'),
    default='haunted_places.csv'
)
def main(
    haunted_place_file,
    location_cache_file,
    city_cache_file,
    output_file
):
    
    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger(__name__)
    
    # Load the location cache.
    logger.info(
        "Loading location cache from {}.".format(location_cache_file.name)
    )

    location_cache = load_location_cache(location_cache_file)

    logger.info(
        "Cache loaded: {} locations cached.".format(len(location_cache))
    )

    # Load the city cache.
    logger.info(
        "Loading city cache from {}.".format(city_cache_file.name)
    )

    city_cache = load_city_cache(city_cache_file)

    logger.info(
        "Cache loaded: {} cities cached.".format(len(city_cache))
    )

    haunted_place_reader = csv.DictReader(haunted_place_file)
    haunted_place_writer = csv.DictWriter(
        output_file,
        fieldnames=haunted_place_reader.fieldnames + [
            "state_abbrev",
            "longitude",
            "latitude",
            "city_longitude",
            "city_latitude"    
        ]
    )
    haunted_place_writer.writeheader()

    for row in haunted_place_reader:
        longitude = get_in(
            [(row["state"], row["city"], row["location"]), "lng"],
            location_cache,
            None
        )
        latitude = get_in(
            [(row["state"], row["city"], row["location"]), "lat"],
            location_cache,
            None
        )

        city_longitude = get_in(
            [(row["state"], row["city"]), "lng"],
            city_cache,
            None
        )
        city_latitude = get_in(
            [(row["state"], row["city"]), "lat"],
            city_cache,
            None
        )

        haunted_place_writer.writerow(
            {
                **row,
                "state_abbrev": STATE_TO_ABBREV[row["state"]],
                "longitude": longitude,
                "latitude": latitude,
                "city_longitude": city_longitude,
                "city_latitude": city_latitude
            }
        )
    

if __name__ == "__main__":
    main()