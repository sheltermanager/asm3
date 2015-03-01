#!/bin/bash

COUNT=0
rm -rf splash*.jpg

for i in *.jpg; do

    IN=$i
    OUT=splash$COUNT.jpg
    NAME=`basename $i .jpg`

    # Resize image to 400x200, retaining aspect ratio
    convert $IN -adaptive-resize 400x200 $OUT

    # Use seam carving to extend the image width
    convert $OUT -liquid-rescale 400x200! $OUT

    # Add the ASM logo
    composite -dissolve 45 -gravity southeast -format jpg -quality 75 $OUT overlay.png $OUT

    # Add a legend with the animal name
    # -undercolor '#00000080'
    convert $OUT -fill white -gravity southwest -stroke black -strokewidth 2 -annotate +5+5 $NAME -stroke none -annotate +5+5 $NAME $OUT
    
    let COUNT=COUNT+1

done
