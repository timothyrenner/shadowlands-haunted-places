ROOT = $(shell pwd)

data/raw/haunted_places.json:
	cd shadowlands_crawler && \
	scrapy crawl shadowlands_places_spider \
	--output-format jsonlines \
	--output $(ROOT)/data/raw/haunted_places.json

data/external/cities.csv:
	wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-City-CSV.zip
	unzip GeoLite2-City-CSV.zip
	mv GeoLite2-City-CSV_* data/external/geolite_city
	mv GeoLite2-City-CSV.zip data/external/
	python scripts/make_cities.py \
		data/external/geolite_city/GeoLite2-City-Locations-en.csv \
		data/external/geolite_city/GeoLite2-City-Blocks-IPv4.csv \
		--output-file data/external/cities.csv

data/processed/haunted_places.csv: data/raw/haunted_places.json
	python scripts/process_haunted_places.py \
		data/raw/haunted_places.json \
		data/processed/haunted_places.csv