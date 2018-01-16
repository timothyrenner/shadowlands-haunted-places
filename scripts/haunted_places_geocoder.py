import click
import csv
import pandas as pd
import numpy as np
import os

from dotenv import load_dotenv, find_dotenv
from toolz import curry

GOOGLE_MAPS_ENDPOINT = \
    "https://maps.googleapis.com/maps/api/geocode/json?address={}&key={}"

def load_geo_cache(cache_file):
    """ Returns a set of what's already in the cache as a state,city,location
        tuple.
    """
    return {
        (c[0], c[1], c[2]) for c in cache_file
    }


def _create_geo_request(google_api_key, state, city, location):

    address = ",".join([location, city, state])

    return GOOGLE_MAPS_ENDPOINT.format(address, google_api_key)

@click.command()
@click.argument('haunted_place_file', type=click.File('r'))
@click.option('--cache-file', '-c', type=click.File('r'), default=None)
@click.option('--output-file', '-o', type=click.File('w'), default='-')
def main(haunted_place_file, cache_file, output_file):

    load_dotenv(find_dotenv())

    google_api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
    
    geo_cache = set()
    if cache_file:
        geo_cache = load_geo_cache(csv.reader(cache_file))

    haunted_places = pd.read_csv(haunted_place_file)

    null_state = haunted_places.state.isnull()
    null_city = haunted_places.city.isnull()
    null_location = haunted_places.location.isnull()

    haunted_place_locations = haunted_places.loc[
        ~null_state & ~null_city & ~null_location,
        ['state','city','location']
    ].drop_duplicates()

    create_geo_request = curry(_create_geo_request)(google_api_key)

    writer = csv.writer(output_file)

    for _,row in haunted_place_locations.iterrows():
        # Skip if it's already in the cache.
        if (row["state"], row["city"], row["location"]) in geo_cache: continue
        
        # Otherwise write it to file.
        writer.writerow([
            row["state"],
            row["city"],
            row["location"],
            create_geo_request(row["state"], row["city"], row["location"])
        ])


if __name__ == "__main__":
    main()