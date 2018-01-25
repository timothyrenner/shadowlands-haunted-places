# Haunted Places

This repository contains code for scraping, cleaning and geocoding data from [The Shadowlands Haunted Places Index](http://www.theshadowlands.net/places/).
Currently this dataset only contains the US locations.
The non-US places don't have a standard schema and will be a challenge to scrape.

## The Dataset

The dataset itself is a CSV file with the following columns:

| column         | type   | description                                                  |
| -------------- | ------ | ------------------------------------------------------------ |
| description    | string | A textual description with details of the haunting.          |
| location       | string | A more detailed description of the haunted place's location. |
| longitude      | float  | The longitude of the location (geocoded dataset only).       |
| latitude       | float  | The latitude of the location (geocoded dataset only).        |
| city           | string | The city of the haunted place.                               |
| city_longitude | float  | The longitude of the city (geocoded dataset only).           |
| city_latitude  | float  | The latitude of the city (geocoded dataset only).            |
| state          | string | The state of the haunted place.                              |
| state_abbrev   | string | The abbreviated state.                                       |
| country        | string | The country of the haunted place. Currently only US.         |

## Getting the Data Yourself

The data will be available on data.world soon.

The makefile contains the entire data processing pipeline, and is reproducible.
The only real rub here is that you'll need to hit Google's geocoding service and that isn't free.
Alternatively you can scrape just the site and put that in `data/interim/haunted_places.csv`.
See below for details.

```bash
# Install the conda environment.
# You might need to tweak the environment.yml if anaconda's not in ~/anaconda.
conda env create -f environment.yml

# Use the package manager of your choice here.
brew install jq
brew install mlr

# Activate the environment.
source activate shadowlands-haunted-places

# This makes the non-geocoded dataset, and is completely free.
make data/interim/haunted_places.csv

# This one requires you to give money to Google for using their geocoder.
make data/processed/haunted_places.csv
```

## Other Stuff

I like to use Elasticsearch for quick data exploration and visualization, so there's a script for loading the haunted places into a local Elasticsearch instance: `scripts/load_elasticsearch.py`.