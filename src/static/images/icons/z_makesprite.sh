#!/bin/bash

# uses imagemagick to stich together all images in a folder and
# then writes a css file with the correct offsets along with a
# test html page for verification that its all good

folder=.
prefix=asm
ext='*.png'
ext2=.png

#if [ 'x' != 'x'$4 ]
#then
#    ext2=.$4; # the extension to iterate over for input files
#else
#    ext2=".png"; # the extension to iterate over for input files
#fi

#if [ 'x' != 'x'$3 ]
#then
#    #ext="."$3; # the extension to iterate over for input files
#    ext=$3; # the extension to iterate over for input files
#else
#    ext=".gif"; # the extension to iterate over for input files
#fi

name=$folder; # output will be placed in a folder named this
classname=$prefix"-icon"
css="$name/$classname.css";
html="$name/test.html";
touch $css $html;

echo "Generating sprite file...";
#echo convert *$ext -append $name/$classname$ext;
echo executing: convert $ext -append $name/$classname$ext2;
convert $ext -append $name/$classname$ext2;

echo "Sprite complete! - Creating css & test output...";

echo -e "<html>\n<head>\n\t<link rel=\"stylesheet\" href=\"`basename $css`\" />\n</head>\n<body>\n\t<h1>Sprite test page</h1>\n" >> $html

gendate=`date +%Y%m%d%H%M%S`
echo -e ".$classname {\n\tbackground-image: url('static/images/icons/$classname$ext2?gen=$gendate'); display: inline-block; vertical-align: middle; \n}" >> $css;
echo -e ".$classname-bg {\n\tbackground-image: url('static/images/icons/$classname$ext2?gen=$gendate'); \n}" >> $css;
counter=0;
offset=0;
for file in $ext
do
    width=`identify -format "%[fx:w]" "$file"`;
    height=`identify -format "%[fx:h]" "$file"`;
    #idname=`basename "$file" $ext`;
    idname=`basename "$file" $ext2`;

    clean=${idname// /-}
    clean=asm-icon-$clean
    echo ".$clean {" >> $css;
    echo -e "\tbackground-position:0 -${offset}px;" >> $css;
    echo -e "\twidth: ${width}px;" >> $css;
    echo -e "\theight: ${height}px;\n}" >> $css;

    echo -e "<a href=\"#\" class=\"$classname $clean\"></a>\n" >> $html;

    let offset+=$height;
    let counter+=1;
    echo -e "\t#$counter done";
done

echo -e "<h2>Full sprite:</h2>\n<img src=\"$classname$ext2\" border=1/>" >> $html;
echo -e "</body>\n</html>" >> $html;

echo -e "\nComplete! - $counter sprites created";

