#!/bin/sh
TOKEN=$1

for species in Cat Dog Rabbit Horse;
do
  curl --fail-with-body --silent --show-error \
    --get \
    -H "Authorization: Token token=${TOKEN}" \
    -H "Accept: application/json" \
    -H "Content-Type: application/json" \
    --data-urlencode "species_name=${species}" \
    --output "${species}.json" \
    --write-out "${species}: HTTP %{http_code}, %{size_download} bytes\n" \
    "https://www.petrescue.com.au/api/v2/breeds"
done

