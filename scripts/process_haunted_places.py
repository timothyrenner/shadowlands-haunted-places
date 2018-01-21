import click
import json
import logging
import csv

from toolz import get_in


def load_location_cache(location_cache_file):
    return {
        (c[0], c[1], c[2]): get_in(
            ['results',0,'geometry','location'],
            json.loads(c[3]),
            None
        )
        for c in csv.reader(location_cache_file)
    }    


@click.command()
@click.argument('haunted_place_file', type=click.File('r'))
@click.argument('location_cache_file', type=click.File('r'))
@click.option(
    '-o', '--output-file',
    type=click.File('w'),
    default='haunted_places.csv'
)
def main(haunted_place_file, location_cache_file, output_file):
    
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

    haunted_place_reader = csv.DictReader(haunted_place_file)
    haunted_place_writer = csv.DictWriter(
        output_file,
        fieldnames=haunted_place_reader.fieldnames + ["longitude", "latitude"]
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

        haunted_place_writer.writerow(
            {
                **row,
                "longitude": longitude,
                "latitude": latitude
            }
        )
    

if __name__ == "__main__":
    main()