#!/bin/sh

# builds a css stylesheet that contains all the icon images
# as base64 encoded data uris

css=asm-icon.css

echo ".asm-icon { display: inline-block; vertical-align: middle; width: 16px; height: 16px; background-size: 16px 16px;}" > $css

for i in *.png; do
    b64=`base64 -w 0 < $i`
    echo ".asm-icon-`basename $i .png` { background-image: url(\"data:image/png;base64,$b64\"); }" >> $css
done

exit 0 # We don't have svgs any more

for i in *.svg; do
    b64=`base64 -w 0 < $i`
    echo ".asm-icon-`basename $i .svg` { background-image: url(\"data:image/svg+xml;base64,$b64\"); }" >> $css
done

