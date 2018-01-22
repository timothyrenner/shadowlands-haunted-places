import click
import elasticsearch
import logging

from csv import DictReader
from elasticsearch.helpers import bulk
from time import time
from toolz import curry, iterate

HAUNTED_PLACE_TYPE = "haunted_place"
HAUNTED_PLACES_BODY = {
    "mappings": {
        HAUNTED_PLACE_TYPE: {
            "properties": {
                "city": {
                    "type": "keyword"
                },
                "country": {
                    "type": "keyword"
                },
                "description": {
                    "type": "text"
                },
                "location": {
                    "type": "text"
                },
                "state": {
                    "type": "keyword"
                },
                "state_abbrev": {
                    "type": "keyword"
                },
                "longitude": {
                    "type": "float"
                },
                "latitude": {
                    "type": "float"
                },
                "city_longitude": {
                    "type": "float"
                },
                "city_latitude": {
                    "type": "float"
                },
                "location_geo": {
                    "type": "geo_point"
                },
                "city_location_geo": {
                    "type": "geo_point"
                }
            }
        }
    }
}


def make_haunted_place_action(index, doc_id, doc):
    return {
        "_id": doc_id,
        "_op_type": "index",
        "_index": index,
        "_type": HAUNTED_PLACE_TYPE,
        "_source": {
            **doc,
            "location_geo": [
                float(doc["longitude"]),
                float(doc["latitude"])
            ] if doc["longitude"] else None,
            "city_location_geo": [
                float(doc["city_longitude"]),
                float(doc["city_latitude"])
            ] if doc["city_longitude"] else None
        }
    }


@click.command()
@click.argument('input_file', type=click.File('r'))
@click.option('--index', '-i', type=str, default="haunted_places")
def main(input_file, index):

    log_fmt = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    logger = logging.getLogger(__name__)


    client = elasticsearch.Elasticsearch()
    indices_client = client.indices

    if indices_client.exists(index):
        logger.info("{} already exists. Deleting.".format(index))
        indices_client.delete(index)
        logger.info("{} deleted.".format(index))

    logger.info("Creating {}.".format(index))
    indices_client.create(
        index=index,
        body=HAUNTED_PLACES_BODY
    )
    logger.info("{} created.".format(index))


    reader = DictReader(input_file)

    haunted_place_actions = curry(make_haunted_place_action)(index)

    # Zip the reader with an infinite incrementor for the IDs.
    reader_actions = map(
        haunted_place_actions,
        iterate(lambda x: x+1, 0),
        reader
    )

    start = time()
    logger.info("Indexing documents from {} into {}.".format(
        input_file.name,
        index
    ))
    num_ok,num_fail = bulk(client, reader_actions)
    logger.info("Done. Documents indexed in {:.2f}s.".format(time() - start))


if __name__ == "__main__":
    main()