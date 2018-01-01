ROOT = $(shell pwd)

data/raw/haunted_places.json:
	cd shadowlands_crawler && \
	scrapy crawl shadowlands_places_spider \
	--output-format jsonlines \
	--output $(ROOT)/data/raw/haunted_places.json