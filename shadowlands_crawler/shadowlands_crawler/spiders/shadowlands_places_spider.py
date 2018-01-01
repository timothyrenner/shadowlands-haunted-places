# -*- coding: utf-8 -*-
import scrapy
import re
from toolz import dissoc, get

class ShadowlandsPlacesSpider(scrapy.Spider):
    name = 'shadowlands_places_spider'
    allowed_domains = ['theshadowlands.net']
    start_urls = ['http://theshadowlands.net/places/']


    def parse(self, response):

        newline_re = re.compile(r"\n")
        field_entries = {
            "District of Columbia": ["location", "description"]
            # Leaving this dict open to adding the international stuff.
            # It's _very_ inconsistent and will be challenging to effectively
            # scrape, but I want to leave the door open just in case.
        }

        location_tables = response.xpath('//table')[2:]

        us_locations = location_tables[0].xpath('tbody/tr/td/b/a')
        
        for location_link in us_locations:

            prime_location = newline_re.sub(
                " ",
                location_link.xpath('./text()').extract()[0]
            ).strip()

            fields = get(
                prime_location,
                field_entries,
                ["city", "location", "description"]
            )

            if prime_location == "District of Columbia":
                yield response.follow(
                    location_link,
                    self.parse_place_page,
                    meta={
                        "city": prime_location,
                        "state": "Washington DC",
                        "country": "United States",
                        "fields": fields
                    }
                )
            elif prime_location in {"California", "Texas"}:
                yield response.follow(
                    location_link,
                    self.parse_place_index_page,
                    meta={
                        "state": prime_location,
                        "country": "United States",
                        "fields": fields
                    }
                )
            else:
                yield response.follow(
                    location_link,
                    self.parse_place_page,
                    meta={
                        "state": prime_location,
                        "country": "United States",
                        "fields": fields
                    }
            )

        
    def extract_record(self, text, fields):
        """ Extracts the record information from a list of strings into a dict
            with the provided keys.

            text - A list of strings.
            fields - A list of strings representing the fields to extract into.
                If the number of fields is less than the number of elements
                in the list all remaining text gets merged into one string and
                put into the last field.
        """

        if len(text) < len(fields):
            return {
                # Always assign the last element of text to the last field.
                fields[-1]: text[-1].strip(),
                # Assign any remaining fields 
                **{
                    field: val.strip()
                    for field,val in zip(fields, text[:-1])
                }
            }
        else:
            return {
                # The structured fields except the last one.
                **{
                    field: val.strip()
                    for field,val in zip(fields[:-1], text)
                },
                # All the other fields are dumped into the last provided key.
                fields[-1]: " - ".join(text[(len(fields)-1):]).strip()
            }

    
    def parse_place_index_page(self, response):
        links = response.xpath('//b/font/font/font/a')
        index_re = re.compile(r"\(.*\)")
        newline_re = re.compile(r"\n")

        for link in links:
            link_text = \
                newline_re.sub(" ", link.xpath('./text()').extract()[0])
            
            if index_re.match(link_text):
                yield response.follow(
                    link,
                    self.parse_place_page,
                    meta = dissoc(
                        response.meta,
                        "download_slot",
                        "download_latency",
                        "download_timeout",
                        "depth"
                    )
                )


    def parse_place_page(self, response):

        # Regular expression helpers.
        tag_re = re.compile(r"<[^>]+>")
        newline_re = re.compile(r"\n")
        location_re = re.compile(r"(.*?) - (.*?) - (.*)")
        
        # Extract the fields to extract from the metadata.
        fields = response.meta["fields"]

        # This is a list of all the text between the "breaks".
        # Next task will be to filter out the ones that are the actual 
        # places, then parse out the city / place / description.
        # Can't lean on xpath here because the font tags are borked as hell.
        places = \
            newline_re.sub(" ", response.xpath('.').extract()[0])\
            .split("<br>")

        for place in places:
            # Skip empty tags.
            if not place.strip(): continue
            
            # Strip out the HTML tags. This is simple because all we need to do
            # is remove them, not extract anything from them.
            place_cleaned = tag_re.sub("", place)
            # Now replace all of the newlines with spaces.
            place_cleaned_space = newline_re.sub(" ", place_cleaned)

            # Now extract with the regex.
            location_match = location_re.match(place_cleaned_space)

            # Skip if there isn't a real place. This is usually for junk
            # tag closures.
            if not location_match: continue

            yield {
                **self.extract_record(location_match.groups(), fields),
                # All the metadata except fields gets put in the record.
                **dissoc(
                    response.meta,
                    "fields",
                    "download_slot",
                    "download_latency",
                    "download_timeout",
                    "depth"
                )
            }