#!/bin/sh

TOKEN=$1
SPECIES="Cat Dog Rabbit Horse"

for i in $SPECIES; do
    curl -H "Content-Type: application/json"  "https://www.petrescue.com.au/api/v2/breeds?species_name=$i&token=$TOKEN" > $i.json
done
