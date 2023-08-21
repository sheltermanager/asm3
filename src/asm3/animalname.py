
"""
Module for generating random pet names from a large set.
call get_random_name()
"""

import random

NAMES = """
Abbey Moon 
Abby 
Abel 
Abigail 
Abigale 
Abihu 
Able 
Abner 
Aboo 
Abster 
ACDC 
Ace 
Achak 
Acorn 
Acrobat 
Adam Ant 
Adamall 
Adele 
Adelheid Hildegard 
Adelor 
Adia 
Adoc 
Adoc Peregrin 
Adora 
Adrien 
Aerial 
Aero 
Afternoon 
Agamemnon 
Aggy 
Agnes 
Ahab 
Ahktar 
AJ 
Aja 
Ajax 
Ajay 
Akasha 
Akeyra 
Al 
Ala 
Alaska 
Alastair 
Albert 
Albert Einstein 
Albus 
Al Capone 
Alcatraz 
Aldrea 
Alec Guinness 
Alea 
Aleksandr Nikolai 
Alex 
Alexander 
Alexandia 
Alexei 
Alexi 
Alexis 
Alexis Winkle Wriggle Sexy Rexy Rooser Bruiser WOO! WOO! 
Alfie 
Alfonso 
Alfonzo 
Algea B Eater 
Algernon 
Algonquin Nepoltian Hamy the 8th 
Alice 
Alicia 
Alisha 
Allegra 
Alley 
Allie 
Allister 
Ally 
Alpha 
Alphabites 
Alphalpha 
Alpo 
Alska (Al) 
Alt 
Amalia 
Amaluck 
Amanda 
Amber 
Ambi-Pur 
Ambrosia 
Amelie 
Amera 
Amethyst 
Amiboshi 
Amora 
Amoray 
Amos 
Amos Moses 
Amuletta (Amy for Short) 
Amun Ra 
Amy 
Amy Stickerpants 
Anabell 
Anais 
Anastasia 
AndAnd 
Andes 
Andre 
Andromeda 
Andy 
Angel 
Angela 
Angel Blossom 
Angeles 
Angelic 
Angelica 
Angelina 
Angel Timon Crabbe 
Angie 
Angora 
Ani 
Anja 
Anna 
Annabell 
Annabelle 
Anne 
Anne Shirley 
Annie 
Ant 
Anthrax 
Antigone (pronounced Ann-tig-o-nee) 
Anubis 
Anushka 
Anxious 
Apache 
Aphideites 
Aphrodite 
Apirl 
Apple 
Applecheeks 
Apollo 
Appollo 
April 
Aqua (pronounced "Ogua") 
Aqua Marie 
Arabella 
Aragon 
Aramis 
Arcamedis 
Archer 
Archie 
Archimetes 
Ardie 
Ardihn 
Arf 
Argos 
Ariadnae 
Arial 
Arianna 
Arie 
Arieal 
Ariel 
Aries 
Aristotle 
Arlian 
Arlo 
Arman 
Arnie 
Arnold 
Arrowhead 
Arther 
Arthur 
Artie 
Arwen 
Ash 
Asha 
Ashanti 
Ashes 
Ashley 
Ashton 
Asia 
Asmodeus 
Aspen 
Asper 
Asti 
Astra 
Astrid 
Astro 
Athena 
Atlas 
Attla 
Aubrey 
Auburn 
Audrey 
Auggie 
Augustine 
Aunt 
Aurora 
Aurthor 
Austin 
Australopithecus 
Autumn 
Ava 
Avah 
Avalanche 
Avalon 
Avaranah 
Avatar 
Avi 
Avonlea 
Awall 
Axe 
Axel 
Axle 
Aylott 
Azilia 
Aziza 
Azizi 
Azul 
Azz 
Azzi
Babby 
Babe 
Babel 
Babes 
Babooshka 
Babs 
Baby 
Baby Boy 
BabyCakes 
Baby Cindy 
Baby Girl 
Baby Goat 
Baby Golliya Fredrick Edwin Howard the Second (Baby Golli) 
Baby Hallie 
Baby Laura 
Baby Precious 
Babylon 
Bacardi 
Bacchus 
Bachi (Backie) 
Backhoe 
Backspace 
Bacon 
Bacon Bit 
Badge 
Badger 
Badger-face 
Bailey 
Baileys 
Bailona 
Bait 
Baja 
Baku 
Baldrick 
Balls 
Baloo 
Balthazar 
Bam 
Bama 
Bambam 
Bam Bam or Bam-Bam 
Bambi 
Bambina 
Banana 
Banda 
Bandette 
Bandis 
Bandit 
Bandito 
Bane 
Bangles 
Baracuda 
Barakka 
Barbie 
Barkley 
Barnabas 
Barnaby 
Barney 
Baron 
Barrett 
Barry Manilow 
Bart 
Bartleby 
Bartles 
Bashful 
Basil 
Basilisk 
Bat 
Batman 
Batwing 
Baxter 
Bay 
Bay-Ann 
Bayou 
Bazal 
Bazel 
Bazoo 
BB 
Bea 
Beach 
Bea Honey 
Beaker 
Beamer 
Beanie 
Beans 
Bear 
Bearen 
Bear Man 
Beast 
Beastie 
Beatrice 
Beau 
Beautiful 
Beauty 
Beauty Baby Venom 
Beba 
Bebe Le Rue (Baby Grace) 
Beck 
Beckham 
Bee 
Beebee 
Beebo 
Bee Bop 
Beeker 
Beetlejuice 
Beetovan 
Bela 
Belinda 
Bell 
Bella 
Belle 
Belle Star 
Bellows 
Belly 
Belka 
Belt 
Ben 
Bender 
Benelli 
Ben-ji 
Benny 
Benson 
Bentley 
Beowulf (pronounced bay-oh-wolf) 
Berkley 
Bernadette 
Bernard St Giles 
Bernie 
Berry 
Bertha 
Bertram 
Bertus 
Berty 
Beryl 
Bessie 
Beth 
Betsy 
Betty 
Betty Boop 
Betty Lou 
Bessie 
Bessy 
Beulah 
Bhitcher 
Bianca 
Bibbity 
Bibbles 
Big Boy 
Big Boy-Baby Maker 
Big Daddy 
BigFish 
Bigger 
Biggie 
Biggles 
Big Mac 
Big Mama 
Big Mama Charlotte 
Big Mo 
Big Mumma 
Bigon 
Big Red 
Big Sister 
Bigun' 
Bigwig 
Bijou 
Biker Boy 
Bilbo 
Billabong 
Billie 
Billie Jo
Billy 
Billy Bob 
Billy-Bob 
Billy-Bob-Joe 
Bindi 
Bindy 
Bingo 
Binker 
Binky 
Binney 
Bippity 
Birdee 
Birdy 
Biscotti 
Biscuit 
Bismark 
Bissel 
Bisto 
Bit 
Bitsy 
Biskit 
BJ 
Blabbo 
Black Jack 
Black Magic 
Blackavar 
Blackberry 
Blackie 
Blackjack 
Blackitty 
BlackPrincess 
Blade 
Blaine 
Blake 
Blakeley 
Blana 
Blanca 
Blanche 
Blanco 
Blastoise 
Blayz 
Blaze 
Blaze-of-Light 
Blaze Pascal 
Blazer 
Bling 
Blinker 
Blinkin' 
Blinky 
Blinx 
Blister 
Blitz 
Blitza 
Blitzer 
Bliz 
Blizard 
Blizz 
Blizzard 
Bloat 
Blonde Mother 
Blondie 
Blossom 
Blu 
Blubeard 
Bludger 
Blue 
Blue Blinker 
Blue Streak 
Bluebeard 
Bluebell 
Blueberry 
Blues 
Bluto 
Bo 
Boardwalk 
Bob 
Bobbie 
Bobbit 
Bobby B. Bunnicula 
Bobby Boucher 
Bobert 
BoBo 
Bobo 
Bo Bo 
Bocephus 
Boffo 
Bogart 
Bogavich 
Bogey 
Boggy 
Boh 
Bohemian Tightsqueeze 
Bojangles 
Bolo 
Bolt 
Bomarange
Bon-Bon 
Bongo 
Bonkers 
Bonnie 
Bono 
Boo 
Boo Berry 
BooBoo 
Boo Boo 
Booger 
Boo Ickles 
Booker T 
Booma 
Boomer 
Boomerang 
Boomqueda 
Boonie 
Bonsai 
Boot 
Boots 
Bootsy 
Boozer 
Boppity 
Bopsy 
Boress 
Boris 
Borris 
Bosko 
Bossy 
Boston 
Botan 
Bounce 
Bowen 
Bowie 
Bows 
Bowser 
Boxwood 
Boy-Boy 
Bradley 
Bradly 
Brain 
Brainard 
Brandi 
Brandy 
Brandy Wu 
Brasen Lake 
Brat 
Brat Girl 
Bray 
Breezy 
Brenda 
Brendan 
Brian 
Briar 
Bridget 
Bridgett 
Bright Eyes 
Brillo 
Brisbie 
Brisby 
Britney 
Brittany 
Brittni 
Broccoli 
Bronson 
Brounswick 
Browni 
Brownie 
Browniz 
Bruce 
Bruce Lee 
Bruce-Lee 
Bruiser 
Brunhilda 
Bruno 
Bruskie 
Brutal 
Brutinie 
Brutus 
BrutusCrabCakes 
b.t. 
Bu 
Bubba 
Bubble 
Bubble Gum 
Bubblegum 
Bubbles 
Bubbly 
Bubby 
Bubo 
Bubonic 
Buc 
Buck 
Bucket 
Buckles 
Buckskin 
Buckthorn 
Bucktooth 
Buckwheat 
Bucky 
Bud 
Budda 
Buddha 
Buddy 
Buddy Love 
Buddy T. Bunnion 
Budong 
Buffy 
Bug 
Bugs 
Bugster 
Bugsy 
Bull 
Bull-Buddy 
Bull-Dog 
Bullet 
Bullwinkle 
Bully 
Bulma 
Bumble 
Bumper 
Bun Bun 
Bungie 
Bunky 
Bunnicula Marie 
Bunny 
Bunny Bunny 
Bunny Face 
Bunny Foo Foo 
Buntie 
Burberry 
Burrito 
Burt 
Burtis 
Busta 
Buster 
Butch 
Butt Man 
Butter 
Butterbean 
Buttercup 
Butterfinger 
Butterfly 
Butters 
Butterscotch 
Butter Scotch 
Butterstuff 
Buttons 
Buun 
Buzby 
Byron
Caboodles 
Cackle 
Cadberry 
Cadburry 
Cadbury 
Cadera 
Cael 
Caesar 
Cain 
Cairo 
Cake 
Calamity 
Callest 
Calley 
Calico 
Callie 
Caligula 
Caliguar 
Calista 
Callie Kisses 
Cally 
Calum 
Calvin 
Calypso 
Cameo 
Camere 
Cami 
Camira 
Camomile 
Camron 
Canada 
Candy 
Canibus Sativa 
Cannoli 
Canouah (pronounced ka-no-ah)
Capone 
Cappy 
Capri 
Caprice (aka Cappy) 
Caps 
Captain Hook 
Captain Jack Sparrow 
Captain Midnight 
Caramel 
Cari 
Carina 
Carissa 
Carl 
Carley 
Carlonia 
Carlos 
Carlose 
Carly 
Carlzander 
Carma 
Carmel 
Carmella 
Carolina 
Carpet Shark 
Carrie 
Carrot 
Carrot Top 
Cartman 
Cas 
Casandra 
Casey 
Caseymoo 
Cash 
Cashew 
Casper 
Cassandra 
Cassi 
Cassidy 
Cassidy (Hopalong) 
Cassie 
Cassy 
Castor 
Catia 
Cat Food 
Cayenne Pepper Lou Pupper Devil Dog 
CC 
C. C. Bear 
C.D. 
Ceasar 
Cecile 
Cember 
Cera 
Ceru 
Chab 
Cha-Cha 
Chacha Lapin 
Chachi 
Chacaro 
Chad 
Chadwick 
Chairon 
Chakotay 
Chalupa 
Champ 
Champagne 
Chan 
Chance 
Chanco 
Chandler 
Chandra 
Chanel 
Chantal 
Chantey 
Chaos 
Charger 
Charity 
Charlemagne 
Charles 
Charleston 
Charley Brown 
Charlie 
Charlie Brown 
Charlotte 
Charly 
Charmander 
Charroh 
Charry 
Chase 
Chasey 
Chatter 
Chatters 
Chaz 
Checkers 
Cheddar 
Cheech 
Cheech n' Chong 
Cheek 
Cheekers 
Cheeko 
Cheeks 
Cheerio 
Cheese 
Cheesel 
Cheese Nip 
Cheetah 
Cheeto 
Chee-to 
Cheko 
Chella 
Chelsea 
Chenzie 
Cherokee 
Cher 
Cherry 
Cherub 
Chesney 
Chester 
Chesterfield 
Chesty 
Chewie 
Chewy 
Chevy 
Cheyanne 
Cheyenne 
Cheza 
Chica 
Chicha 
Chi Chi 
ChiChi 
Chi-Chi 
Chichiri 
Chicklet 
Chickpea 
Chico 
Chief 
Chihira 
Chile 
Chili 
Chilli 
China 
Chinchi 
Chingy 
Chino 
Chinstrap 
Chip 
Chipper 
Chiriko 
Chives 
Chizewer 
Chlavel 
Chloe 
Choad 
Chochee 
Choco 
Chocolate 
Chocolate Chip 
Chok 
Chokotah 
Chombo 
Chomper 
Chompy 
Chong 
Chopper 
Chops 
Chopsticks 
Chris 
Christie 
Christina 
Christmas 
Chubbs 
Chubby 
Chub Chub 
Chubs 
Chu-Chu 
Chuchundra 
Chuck 
Chuckles 
Chucky 
Chum 
Chumley 
Chunk 
Chunks 
Chunky 
ChunkyButt 
Chowder 
Church 
Churchie 
Chyna 
Ciba 
Cicero 
Cicily 
Cilla 
Cinder 
Cinderella 
Cinna 
Cinnabar 
Cinnabon 
Cinna Bun 
Cinnabunn 
Cinnamon 
Cinny 
Circe 
Clancy 
Clang 
Clarah 
Clarence Augustus 
Clarice 
Clarisse 
Clark 
Clash 
Claudia 
Claws 
Cledus 
Clementine 
Cleo 
Cleopatchra 
Cleopatra 
Cletis 
Cletus 
Clever 
Clifford 
Climber 
Cling 
Clinker 
Clint 
Clinton 
Clive 
Cloe 
Cloriece 
Cloud 
Clouds 
Cloudy 
Clover 
Clown 
Clyde 
Cobo 
Coby 
Cocktail 
Cocky 
Co Co 
Co-Co 
CoCo 
Coco 
Cocoa 
Coconut 
Coda 
Cody 
Coewy 
Coffee 
Coffee Bean 
Coke 
Cola 
Cole 
Coley 
Colin 
Colour Ball 
Columbia 
Combat 
Comet 
Comit 
Commanche 
Conan 
Conejo 
Confutious 
Conner 
Connie 
Cook Cook 
Cookie 
Cookie Dough 
Cookies N Cream 
Cookers 
Cookster 
Cool and the Gang (group of fish!) 
Coolio 
Cooper 
Copernicus 
Copper 
Coral 
Corey 
Corky 
Cornelius 
Cornflakes 
Cornolio 
Corny 
Corona 
Corrie 
Corsica 
Cortez 
Cory 
Cosette 
Cosmo 
Cosy 
Coto 
Cotten Candy 
Cotton 
Cotton Ball 
Cotton Candy 
Cottontail 
Cougar 
Could 
Cowboy 
Cowboy Bebop 
Cowry 
Coya 
Cozmo 
Crabanasty 
Crabina 
Crackers 
Crane 
Crash 
Crazy Daisy 
CreamPuff 
Creme-Puff 
Creo 
Cricket 
Crikey 
Crimson 
Crisco 
Cristail 
Cristy 
Critter 
Croak 
Cronk 
Crue 
Cruella 
Cruella DeVille 
Cruiser 
Crumpet 
Crunch 
Crush 
Crusher 
Cruz 
Crystal 
Cubby 
Cuddles 
Cuddles Wagner 
Cueball 
Cuffs 
Cuite 
Cujo 
Cuka 
Cumulus Nimbus ("Nimby") 
Cup 
Cupcake 
Cupid 
Cuppa 
Cuppu 
Curious George 
Curly 
Curly-Cue Ratus 
Curry 
Custard 
Cutie 
Cutie Pie 
Cutiepie 
Cushy 
Cuzco 
Cy 
Cyclone 
Cyclops 
Cygnus 
Cynthia
Dabblit 
Dachi (pronounced Duh-chee) 
Daf 
Daffodil 
Dafny 
Dag n' Norm 
Daily 
Dainty 
Daisy 
Daisy Belle 
Daisy Mae 
Daizy 
Dakki 
Dakota 
Dale JR 
Dali 
Dalilah 
Dallas 
Dallee 
Dallie 
Dama 
Damian 
Damien 
Damion 
Dan 
Dana 
Dandelion 
Dandy 
Danger 
Dangermouse 
Daniel 
Danielle 
Danni 
Danny 
Danny Boy 
Dante 
Dany 
Daphne 
Daquiri 
Dara 
Darby 
Dare Devil 
Daredevil 
Dargo 
Darka 
Darla 
Dart 
Darth Vader 
Darvarus 
Darwin 
Daryl 
Dash 
Dasher 
Da Tank 
Dave 
David 
DaVinci 
Davon 
Day-day 
Dazie Chilla 
Dazzle 
DC 
Deb 
Debeli (pronounced Deb-a-lee)
Dean 
Dec 
Deca 
DeDee 
Dedra 
Degu 
Deianara (pronounced Dayanara) 
Deigo 
Deja Vu 
Dej-roo 
Delboy 
Deliah 
Delilah 
Delores 
Delphine 
Delsea 
Dementia 
Demil 
Demon 
Demon Dog 
Demonicus 
Dende 
De Niro 
Denver 
Deogee Shawna White Wolf 
Deogi 
Deshret 
Destination 
Destiny 
Deuce 
Devil 
Dexter 
DG 
Dharma 
Dharma Louise 
Diablo 
Diago (Deeago) 
Diamond 
Diamond Lil 
Diana 
Diane 
Dice 
Dieb (pronounced Deeb) 
Dieg 
Diego 
Diesel 
Digby 
Digger 
Digger Dan 
Digglet 
Dillon 
Dilly 
Dingo 
Dinky 
Dinner 
Dino 
Dippy 
Dipstick 
Dirty 
Dirty Man 
Divit 
Dixie 
Dixie Trix 
Dizzer 
Dizzy 
Dizzy Dough 
DJ 
D.J. 
DJ Steelwool 
Dmitri 
Dobey (pronounced Doe-bee)
Doc 
Dodger 
Doe 
Dog 
Dogerz 
Dog Food 
Dolly 
Dominick 
Domino 
Donatello 
Donkey 
Donna 
Donny 
Doo 
Doobie 
Doodles 
Dooey 
Doogle 
Doorknob 
Doormouse 
Dopey 
Dora 
Dora the Explorer 
Dork 
Dorie 
Dorothy 
Dorothy (Dottie) Boldy 
Dory 
Dory Anne 
Dosia 
Dot 
Dottie 
Dotty 
Double 
007 
Doug 
Doughby 
Doughnut 
Dova 
Doyal 
Dozer 
Draco 
Dracula 
Dragar 
Drago 
Dragonbait 
Dr. Bunny 
Dr. Evil 
Drake 
Dream 
Dreamweaver 
Drifter 
Duane 
Duce 
Duchess 
Ducki 
Ducks 
Ducky 
Dude 
Dudley 
Duffy 
Dug 
Duke 
Dumbbell 
Dumbo 
Dum Dum 
Dumpling 
Duncan 
Duncan McFerret 
Dundee 
Dunkin's Coffee & Cream (CC) 
Duo 
Duobe 
Duo-Sama 
Durango 
Durageo 
Dust Bunny 
Duster 
Dustin 
Dusty 
Dusty Rose 
Dustyroo 
Dutch 
Dutchess 
Dylan
E2 
Earl 
Earnhardt 
EatsALot 
Ebby 
Ebenezer 
Ebi 
Ebony 
Echo 
Eclipse 
Ed 
Edd 
Eddie 
Eddie Izzard 
Edgar-Allen Crow 
Edie 
Edison 
Edith 
Edmund 
Edward 
Edward Scissorhands
Edward Wong Hau Pepelu Tirvrusky 4th 
Ef-one 
Egbert 
Egwene 
Egypt 
Eightball 
Eiji 
Ein (pronounced "Eye-na") 
Einstien 
Einstein 
EJ 
Eki 
Elaith 
Elephant 
Elf 
E.L. Fudge 
Elijah 
Elisa 
Eliza Rose 
Ella 
Elle 
Ellie 
Elly 
Elmer 
Elmo 
Elphie 
Elsia 
Elsie 
Elsiey 
Elvis 
Elvissa 
Elwood 
Em-em 
Emil 
Emilee 
Emilleo 
Emily 
Emma 
Emmah 
Emmaline McKafis 
Emmo 
Emmy 
Emmy Lou 
Emril 
Endora 
Endymion 
Enkil 
Enter 
Enya 
Eran 
Eric 
Erida (pronounced Air-e-da) 
Erma Jane 
Ernest 
Ernesto 
Ernie 
Erte' 
Escape 
Esmerelda 
Estella 
Ethan 
Ethel 
Ethyl 
Eureka 
Eva 
Eve 
Evie 
Evil 
Evo 
Evra 
Evros (pronounced Ever-os) 
Excalibird 
Excalibur 
Executioner (Q for short) 
Exotica 
Eyed 
Ezra
4x4 
Fabian 
Fagan 
Faith 
Falcor 
Fancy 
Fang 
Fangel 
Fanny 
Fa-neenee 
Fantasma 
Fany 
Farah Ferret 
Farley 
Fast Freddie 
Fat Albert 
Fathead 
Fatso 
Fat Tony 
Fatty Rabbit 
Faun 
Fauna 
Favre 
Fawn 
Faye 
Faye Valentine (also Cowboy Bebop) 
Feasel 
Feather 
Feathers 
Febu 
Feisty 
Feivel 
Felicette 
Felicity 
Felipe (pronounced Felip-ay) 
Felix 
Feliz 
Fenix 
Fenoderee 
Fergie 
Fern 
Fernando 
Ferret Bueller 
Ferris 
Festus 
Fetch 
Fez 
Fezzick 
Fibi 
Fiddle 
Fido 
Fidget 
Fiesty 
Fievel 
Fifi 
FiFi 
Figaro 
Figi 
Filbert 
Fina 
Finch 
Finches 
Finley 
Fiona 
Fire 
Fireball 
Fish 
Fishy Swa 
Fishy Wishy 
Fiver 
Fizgig 
Fizz 
Fizzgig 
Flakey 
Flash 
Flash Quicksilver 
Flatcap 
Fletcher 
Flexi 
Flint 
Flip 
Fliperz 
Flipflop 
Flippy 
Flit 
Flitter Mouse 
Flo 
Floppy 
Floppy Puff Puff 
Flops 
Flopsy 
Flor 
Flora 
Florence (Flo) 
Flotsam 
Flounder 
Flow 
Flower 
Floyd 
Floyde 
Flubber 
Fluff 
Fluffanutter 
Fluffernutter 
FlufferNutter 
Flufflebunny 
Fluff Puff 
Fluffy 
Fluffycake 
Fluffy Girl 
Flurry 
Flute 
Flutterbup 
Flyswatter 
Focker 
Foosie 
Footsie 
Forrest 
Fortner 
Fortune 
Fossil 
Founder 
Four Socks 
Fox 
Foxglove 
Fox Mulder 
Foxy 
Foxy Baby 
Fraidie Water 
Francesca 
Francis 
Frank 
Frankie 
Franklin 
Franklin Tigger 
Franky 
Frannie 
Fran the Nanny 
Frappacinno 
Frappaccino 
Frappucino 
Fraser 
Freakazoid 
Freckles 
Fred 
Freddie 
Freddy 
Fred E. Bear 
Fredrick 
Freedom 
Freeway 
Friar Tuck 
Frickles 
Frida 
Friday 
Frisk 
Friskett 
Friskey 
Frisky 
Frito 
Frito Pie 
Fritz 
Frizzle 
Frizzy 
Frodo 
Frog 
Froggie 
Froggy 
Frolick 
Frost 
Frosty 
Froth 
Frumpie 
Fubu 
Fudge 
Fudgie 
Fue 
Fuer 
Fuego 
Fujiko 
Fu-Man-Chu 
Fundevogel 
Fungo 
Fuogo 
Furball 
Furbbit 
Furbert 
Furbie 
Furby 
Furman 
Furret 
Fury 
Fuzz-z-Finch 
Fuzzball 
Fuzzbucket 
Fuzzbutt 
Fuzzies 
Fuzzy 
Fuzzy Buddy 
Fuzzy McFuzz 
Fwagle 
FX
Gabbrille 
Gabby 
Gabriele 
Gadget 
Gainsborough 
Galadriel 
Galileo 
Gallegher 
Gambler 
Gamecocks 
Gandolph 
Garfield 
Garret the Ferret 
Garth 
Garth Buneon 
Gary 
Gato 
Gator 
Gaylord 
G-Baby 
Geekers 
Geico 
Gem 
Gemini 
General Finn 
General Tsao 
General Tso 
Genkai 
Genie 
Gerald "Jerry" Sleep-N-Eat 
Gerbily 
Geo 
George 
Georgi 
Georgie 
Georgia 
Georgeious Scratticus (George) 
Geppetto 
Gerald 
Geraden 
Geronimo 
Gertie 
Gertrude 
Ghandee 
Ghoma 
Ghost 
Gia 
Giblit 
Gidget 
Giggles 
Giggs 
Giggsey 
Gil (pronounced Jill) 
Gilbert 
Gilda 
Gilligan 
Gilly 
Gimes 
Gimli 
Gin 
Ginger 
Gingerbread 
Ginger Fish 
Gingi 
Gino 
Giraffe 
Girdy 
Girlie Girl
Girly 
Girov 
Git-R-Done 
Gitter 
Giza 
Gizmo 
Gizmonics Murdock 
Gizzi 
Gizzie 
Gizzy 
Gladden T. Hart 
Gladys 
Gladys Night 
Gladys Night's Little Pip, Squeak (Squeak) 
Gloria 
Gnarly Britches Face-Head 
Gnasher 
Godiva 
Godzilla 
Gohan 
Goku 
Goldenia 
Goldenier 
Goldie 
Goldy 
Goliath 
Gollum 
Golly 
Gonzales 
Gonzo 
Gomez 
Goober 
Goofey 
Goofy 
Google 
Googles 
Goose 
Gorbash 
Gorderan 
Gordon 
Gordy 
Gorf 
Goten 
Gotti 
Grace 
Gracie 
Graeme 
Grafitti 
Graham 
Graham Cracker 
Granny 
Grant 
Grapes 
Gras 
Grasshopper 
Green 
Green Tentacle 
Greg 
Gregory 
Gremlin 
Greta 
Gretchen 
Gretta 
Gretzky 
Grey 
Griffey 
Grinch 
Grizabella 
Grommit 
Groucho 
Grover 
Grumpus 
Grumpy 
Gucci 
Guido 
Guinea 
Guiness 
Guinevere 
Gumbie 
Gummo 
Gumpo 
Gunther 
Gur 
Gurselton 
Gus 
Gus-Gus 
Guss Guss 
Gustav 
Gutata 
Guy 
Gwydyon 
Gypsy
Haagen-Daz 
Hades 
Hadley 
Hado 
Hagedis ("Dis") 
Hagrid 
Hagen 
Hailey 
Hailie 
Hairy 
Hala 
Haldir 
Haley 
Half & Half 
Halfpint 
Halfy Twins 
Halla 
Halle 
Hally 
Hambert 
Hamham 
Hamilton 
Hamina Habitha Hornyak 
Hamish 
Hamlet 
Hammer 
Hammy 
Hampton 
Hampy Dexter 
Hamsta 
Hamtaro 
Hana 
Hane 
Hank 
Hannah 
Hannibal 
Hannibird 
Hannible 
Hans 
Hanukah 
Haolie 
Happy 
Hare 
Hardy 
Harlequin 
Harley 
Harold 
Harper 
Harpo 
Harpy 
Harriet 
Harriette 
Harrington 
Harriot 
Harry 
Harry Potter 
Harry Zorro Spiderman 
Haru 
Harvest 
Harvey 
Harvy 
Has en peffer 
Hastings 
Hatchi 
Hathor 
Havoc 
Hawk 
Hawkbit 
Hawk Shaw Hawkins 
Hayden 
Hayley 
Haystack 
Hazel 
Hazelnut 
Hazel-rah 
Hazy 
Hearty 
Heathcliff 
Heather 
Heath Matthew 
Hebe 
Hector 
Hedda 
Hedgebert McPricklesworth 
Hedwig 
Heero 
Heero-Chan 
Hefner 
Heidi 
Helen 
Heli 
Helio (pronounced Ehleo) 
Helix 
Hellfire 
Hemana 
Hendrix 
Hennessy 
Henry 
Her 
Hera 
Herb 
Herbert 
Herberta 
HerbertSherbert 
Herbie 
Herb Williams 
Hercule 
Hercules 
Herman 
Hermi 
Hermie 
Hermikey 
Hermilia 
Hermione 
Hermione Hamhock 
Hermoine 
Hermone 
Hermy 
Heroo 
Hershey 
Hester 
Hiawatha 
Hibbean 
Hibiscus 
Hidey 
Hiei 
Hieme 
Higgins 
Highpie (pronounced Hy-pee) 
Hillary 
Him 
Hines Ward, Jr 
Hip 
Hip Hop 
Hip-Hop 
Hippie 
Hippo 
Hippy 
Hirudoki 
Hissss 
Hissy 
Hissyfit 
Hi-Ya! 
Hobart 
Hobbes 
Hoek 
Hogarth 
Holli 
Holliwood 
Holly 
Hollywood 
Holyfield 
Homa 
Homer 
Homero 
Homie 
Honey 
HoneyBun 
Honeybunches 
Honey Bunny 
Honor 
Honydrops 
Hooch 
Hoodie 
Hootie 
Hooty 
Hoover 
Hop 
Hop Along Cassidy 
Hope 
Hophop 
Hoppa's Marquessa 
Hopper 
Hoppy 
Hopscotch 
Hopup 
Horace 
Hornless 
Horsepower 
Horus 
Hoss 
Hotdog 
Hotflip 
Hotohori 
Hot Rod 
Hottie 
Hoover 
Houdini 
Houdini Buddy Magoo 
Houston 
Howie 
Hubcap 
Hudini 
Huey 
Huggy 
Hugh Hefner 
Hugo 
Hugs 
Humor 
Hungry Jack Biscuit 
Hunnybunny 
Hunny Nut 
Hunter 
Hunter X 
Hurcules 
Hurley 
Husker 
Hwoarang 
Hyacinth 
Hyde nor Hare 
Hydra 
Hyperion 
Hypollita 
Hyzenthlay
Iago 
Iano (pronounced Yahno) 
Iberia 
Icey 
Ichoris 
Ickiss 
Icy Stare 
Idaho 
Ida May 
Idgie 
Ifrit 
Iggy 
Igloo 
Ignatz 
Igor 
Igus 
Ike 
Iki 
IM2AK9 (M2 for short) 
Ima 
Ima Ferret 
Imo 
Imona 
Imotep 
Inca 
Incubus 
Indiana 
Indiana Stone 
Indica 
Indie 
Indigo 
Indira 
Indonesia 
Indy 
Infinity 
Inigo 
Ink 
Inky 
Inspector Gadget 
Inuyasha 
Iodine 
Ione 
Iori 
Irene 
Iris 
Irish 
Irwin 
Isabeaux 
Isabell 
Isabella 
Isabelle 
Isabelle Antoinette 
Isaiah 
Isela 
Ishi 
Ishmael 
Isis 
Iso 
Istral 
Itsy 
Itty Bitty 
Itty Bitty Angel 
Ity Bity 
Iuka 
Ivan 
Ivory 
Ivy 
Izma 
Izzard 
Izzi 
Izzy
J 
Jabba 
Jack 
Jackaroo (Jack for short) 
Jackie 
Jackie Chan 
Jackpot 
Jackson 
Jacky 
Jacob 
Jacob Starr 
Jacques 
Jacquese 
Jade 
Jaded 
Jaden 
Jade Orkid 
Jafar 
Jaffa 
Jager the Jagermeister 
JaJa 
Jaja 
Jakari 
Jake 
Jakey 
Jambo 
James 
Jamesey 
Jamie 
Jane 
Janet 
Janie 
Janis 
Janka 
Jaques 
Jaques Coustou 2 
JarJar 
Jas 
Jasa 
Jasmine 
Jason 
Jasper 
Java 
Jaws 
Jax 
Jay 
Jaydey 
Jay Jay 
Jay Bird 
Jaydn Savannah 
Jaymes 
Jazz 
Jazzie 
Jax 
JD 
Jeb 
Jeanie 
Jeebus 
Jefferson 
Jeffery 
Jeffy-Pooh 
Jelly 
Jelly Bean 
Jemima 
Jemma 
Jen 
Jenabell 
Jenabella 
Jenna 
Jennie 
Jenny 
Jeremiah 
Jeremy 
Jericho 
Jermaine 
Jerry 
Jersey 
Jess 
Jessamine 
Jesse 
Jesse James 
Jessica 
Jessie 
Jessie the Body Ventura 
Jessimbo 
Jester 
Jesus 
Jesus-Freak 
Jesus-Rat 
Jeszy 
Jet 
Jetsam 
Jett 
Jewel 
Jewels 
Jezabelle 
Jianna 
Jiggly Puff 
Jigz 
Jiffy 
Jill 
Jilly 
Jim 
Jimi Hendrix 
Jimmy 
Jin 
Jingles 
Jinn 
Jinx 
Jissa 
Jive 
Jizell 
JJ 
J.J. 
Jodi 
Jodie 
Jody 
Joe 
Joe Cool 
Joey 
Joey Fenthick 
Joeyson 
John 
Johnny 
Johnny Bravo 
Johnny Vegas 
Johnson 
Jo Jo 
Jo-Jo 
JoJo 
Jojo 
JoLee 
Jonah 
Jonaz 
Jonny Sleek 
Jono 
Jordan 
Jorge (pronounced Hor-hay) 
Jorgy 
Jormungand 
Jose 
Joselyn 
Josh 
Josh's Brown Sand Shrew 
Joshua 
Josie 
Journey 
Joy 
Jr. 
J.R. 
JR 
JT 
Juanita 
Judah 
Judge Judy 
Juice 
Juicey 
Ju Ju 
JuJu 
Jujube 
Juke Box 
Jules 
Julie 
Juliet 
Julio 
Julius 
Julliet 
July 
June 
Junebug 
Jungle Jim 
Junior 
Juniper 
Juno 
Jumper 
Jupiter 
Jurell 
Justice 
Justin 
J.ust R.at 
Jynx
Kaa 
Kabato 
Kaia 
Kaiden 
Kaiser 
Kaci 
Kagome 
Kahlua 
Kako 
Kaleidoscope 
Kaley 
Kali 
Kalilicious 
Kallie 
Kaluck (aka Kally) 
Kalulu 
Kalvin 
Kamar 
Kamikaze 
Kammanche 
Kamyle 
Kane 
Kanga 
Kani 
Kanye (pronounced Con-Yae) 
Kaos 
Kappiddi 
Kapu 
Karamel 
Karamella 
Karat 
Karen 
Karma 
Karmen 
Karrey 
Kasey 
Kasper 
Kassidi 
Kassidy 
Kassy 
Kat 
Katana 
Katara 
Katie 
Kato 
Katriena 
Katy 
Kayleigh 
Kaytee 
Kazi 
KC 
Keade 
Keahi 
Kealer 
Keegan Xavier 
Keenah 
Kefa 
Keifer 
Keily (pronounced Kee-ly) 
Keira 
Keko 
Kelala 
Kellogg 
Kelly 
Kendra 
Kendrick 
Kenia 
Kenny 
Kenny Rogers 
Ken-Oki 
Kensington 
Kenya 
Keravny 
Kermie 
Kermit 
Kermit the Hermit 
Kernel 
Kerry 
Kewi 
Kewpie Doll 
Key 
Kezia 
Kia 
Kiara 
Kiarra 
Kiba 
Kicker 
Kif 
Kiki 
Kikyo 
Kila 
Killer 
Killian 
Kim 
Kimba 
King 
Kinga 
Kingki 
Kingkong 
King's Chocolate Ransom 
King Solomon 
King Tiggleswick 
King Tut 
Kinky 
Kino 
Kiowa 
Kip 
Kipper 
Kipu 
Kira 
Kirbi 
Kirby 
Kirra 
Kiss 
Kisses 
Kit 
Kit Kat 
Kitoby 
Kittara 
Kitten 
Kitty 
Kitty Bartholomew 
Kitty Bob 
Kitty Food 
Kitty Krueger 
Kitty Puff 
Kiwi 
KJ 
Kleenex 
Klingon 
Klondike 
Knabbel 
Knarla 
Knees Up 
Knight 
Knobby 
Knot 
Koara 
Kobe 
Kobe Bear 
Kobi 
Kocomojo 
Koda 
Kodiak 
Kody 
Koenma 
Kooku 
Kojak 
KoKo 
Komel 
Kona 
Koosani 
Kopeck 
Korah 
Korbel (actually Anthony Korbel Jr) 
Korbon 
Kosher 
Koshi 
Kota 
Kotten 
Kotter 
Kraken 
Krabby Patty 
Kreacher 
Krillen 
Krim 
Krull Dragonslayer 
Krycek 
Kuddles 
Kujo 
Kuka 
Kumana Kira 
Kumasi 
Kunzite 
Kurama 
Kurma 
Kwanzaa 
Kyle 
Kylie 
Kyoke 
Kyrie
Lacey 
Lacy 
Lady 
Lady Godiva 
Lady Juniper Draonfly Babbette Koko Hiers 
Lady Macbeth 
Lady Meaghan McTavish II 
Lady Quinn 
Lady Pryditor 
Lady Sadie Bella of Nottingham 
Lady Sierra Sea-Glowstar 
Lady Treptova 
Laila 
LaiLah 
Lala 
LaMans 
Lamb Chops 
Lambeau 
Lamia 
Lancalot 
Lancer 
Lane 
Larry 
Larson 
Lasca 
Laser 
Lasher 
Latasha 
Latonka 
Latoya 
Latte 
Laura 
Laurel 
Laurence 
Lavern 
Layla 
Layton Jr. 
LBC (Little Black Cat, Large Black Cat) 
LD 
Leapy 
Leda 
Lee Lee 
Leena 
Leevii 
Lefty 
Legolas 
Lei 
Leia 
Leilani 
Lela
Lemmiwinks 
Lemon 
Lemon Pepper 
Lenny 
Leo 
Leonardo 
Leonie 
Leonox 
Lerk 
Leroy 
Lestat 
LeStat 
LeVern 
Levi 
Lewis 
Lex 
Lexi 
Lexington 
Lexiy 
Lexus 
Lexy 
Lezzi 
Liam 
Libby 
Libra 
Licorice 
Liet 
Lightening 
Lightnin 
Lightning 
Lightning Bolt 
Lil 
Lil' 
Lila 
Lilah 
Lil Bandit 
Lil Bear 
Lil' Billy 
LilBit 
Lil' Bit 
Lil Bug 
Lil' Chestnut 
Lil'Dude 
Lil G 
Lillian 
Lillie 
Lilith 
Lilly 
Lil' Man 
Lil Miss 
Lil Nose 
Lilo 
Lil Oscar 
Lil' Rocky 
Lily 
Lily Ann 
LilyMay 
Lime 
Lime Pie 
Limo 
Limpy 
Linaly (pronounced Linn-al-E) 
Linc 
Lindy 
Ling 
Link 
Linnea 
Linny 
Linus 
Lioforce 
Liptzer 
Liquorice 
Lisa 
Lisa Simpson 
Lister 
Lit'l Miss 
Little Bear 
Little Buddy 
Little Bun 
Little Debbie Snack Cake 
Little Dude 
Little Fella 
Little Foot 
Littlefoot 
Little Gray 
Little Gimpy NoFoot 
Little Girl 
Little Harry 
Little Kim 
Little Lou 
Little Lucy Ball 
Little Man 
Little Miss Piggy 
Little One 
Little Rat 
Little Rhodent 
Little Squzzeser 
Little Tyke 
Little Who 
Little @#%*$ 
Liv 
Lizzie 
Lizzy 
Llama 
Lloyd 
Lloyd in Water Banks 
Lloyd Wagner 
Lobo 
Lock 
Lofa 
Loki 
Lokki 
Lola 
Lollie 
Lomit 
Long 
Loogaroo 
Loopie 
Loquita 
Lord Stanley 
Loreali 
Lorenzo 
Lorraine 
Lorrie 
Lottie 
Lottie Da 
Lotus 
Louie 
Louisa 
Louise 
Lovely 
Lovey 
L.S.D. (short for Lorenzo Saint Dubois) 
LT 
Lubell (pronounced Loo-bell) 
Luce Donovan 
Lucee (pronounced Lucy) 
Lucifer 
Lucifer Donovan 
Lucius 
Luck 
Luckie 
Lucky 
Lucky Bug 
Lucky Jr. 
Lucretia Borgia 
Lucy 
LucyBelle 
Ludo 
Lugs 
Luigi 
Luka 
Luke 
Lulu 
Lulucita 
Lun 
Luna 
Lunar 
Lunch 
Luta Wakan 
Luv 
Lux 
Lybris 
Lycan 
Lydia 
Lyla 
Lynn 
Lynne 
Lynx 
Lyoco 
Lyra 
Lysander (pronounced "lie-san-dur") 
Lysie (pronouncd "lie-see")
M&M 
Mac 
Macaroni 
Macchiato 
Macduff 
MacGuybird 
MacGuyver 
Mac -n- Cheese 
Macy 
Mad Dog 
Madagasca 
Madame Fluffypaws 
Maddie 
Maddison 
Madelaine 
Madeline 
Madeline Anne Dog Dog (MAD Dog) 
Madison 
Madusa 
Mae 
Maestro 
Maeva 
Magellian 
Magenta 
Magget 
Maggic 
Maggic Rubbit 
Maggie 
Maggie Pig 
Magic 
Magical Alice 
Magic Rubbit 
Magkij-znak 
Magnolia 
Magnum 
Magnum PIG 
Magoo 
Magpie 
Mahi 
Maia 
Maidy 
Maisy 
Mai Tai 
Maize 
Maja 
Majestic 
Majik 
Major 
Makaio 
Makavelli 
Mako 
Malachi 
Malcolm 
Malcom 
Maleash 
Malesia 
Malibu 
Malice 
Maliha 
Malteaser 
Malu 
Mama 
Mama Dog 
Mama Goat 
Mama Kitty 
Mamma 
Mandy 
Manfred 
Mango 
Mango Ma'am 
Mango Man 
Mani 
Manilla 
Mannie 
Manny 
Manson 
Manx 
Manzana 
Ma Petit Fleur 
Maple 
Maragret 
Marble 
Marco 
Marcus Antonius 
Marcy 
Mardi 
Mardi Gras 
Margaret 
Marge 
Marguerite 
Marigold 
Marilyn 
Marilyn Bunroe 
Marilyn Manson 
Marin 
Marisa 
Marissa 
Marita 
Mark 
Marlene 
Marley 
Marlo 
Marmalade 
Marmalaid 
Marmelade 
Marmite 
Marnee 
Marrical 
Marron 
Marshall 
Marshmallow 
Marshmello 
Marshmellow 
Marshy 
Martha 
Marther 
Martin 
Martzepan 
Marv 
Marvin 
Mary 
Maryjane 
Mary Jane 
MaryJayne 
Mary Kate 
Mary-Kate 
Mary Lou 
Mason 
Massimo 
Mate 
Matikah 
Matilda 
Matrix 
Matt 
Matthew 
Matthias 
Matthilda 
Mattie 
Maui 
Mauwi 
Mav 
Maverick 
Max 
Maxamillion 
Maxi 
Maxie 
Maximillian 
Maximillion Buttercup 
Maximus 
Maximus Bunniness 
Maxine 
Maxis 
Max Sterling 
Maxwell 
Maxx 
Maxy 
May 
Maybeanlline 
Maybell 
Maybelline 
Maycee 
Mayhem 
Mayla 
Maylee 
MayMay 
Maynard 
Mayson 
Mayzie Bird 
MB 
McFluffy 
McKinnon 
Mc. Cormick 
McTavish 
Medusa 
Meeko 
Mee Mee 
Meesha 
Meg 
Megan 
Mehitabel 
Meika 
Meka 
Mekena 
Meko 
Mel 
Melissa 
Mellisa 
Melody 
Melpomene 
Melvin 
Me-Mo 
Memphis 
Memnoch 
Mendes 
Menki-Menks 
Mental 
Mep 
Mercury 
Mercutio 
Meri 
Merigo Pluto 
Meringue 
Merla 
Merla Pearl 
Merlin 
Merry 
Mervin 
Mesina 
Messier 
Messy Marvin 
Metatron 
Methos 
Methuselah 
Mexico 
Mia 
Miacoda 
Miah 
Mia Ham-ster 
Miaka 
Miakota 
Micah 
Michael 
Michaelangelo 
Michia 
Mickey 
Micki 
Micro 
Midas 
Midge 
Midget 
Midnight 
Midnight Star 
Midori 
Miestreo 
Miette 
Miffy 
Miggy 
Mighty 
MiGuy 
Mika 
Mikey 
Mikey Joe 
Mikhail 
Mi'ko 
Milady 
Mileena 
Milinko 
Milk Dud 
Milkman 
Milk Shake 
Milkshake 
Milky 
Milky Way 
Milli 
Millie 
Milly 
Milly Mae 
Milly-Mop Millicent Silliment Bright Eyes Byue Bobbit Harrington (Mills for short!) 
Milo 
Mimbla 
Mimi 
Min 
Minerva 
Miniature (Mini) 
Mini 
Mini-Me 
Min Min 
Minna 
Minnie 
Mint 
Minters 
Minty 
Minx 
Mira 
Miracle 
Miriya Parino Sterling 
Miroku 
Misa Margret 
Mischief 
Mischief Jane 
Misfit 
Misha 
Mishka 
Miss Ain't Behavin 
Miss Farina Bean 
Miss Inky Velour 
Miss Isabelle 
Mississippi 
Miss Muffit 
Miss Pepper 
Miss Pretty 
Miss Priss 
Miss Prissy 
Miss Swiss 
Miss Tidyman 
Miss Velvet Fuzziwugs 
Missy 
Mist 
Mistandarpacles 
Mister 
Mister Misty 
Mistie 
Mistletoe 
Misty 
Mistyflip 
Misu 
Mitch 
Mitsie 
Mitsukake 
Mitsy 
Mittens 
Mittins 
Mitzi 
Mitzy 
Miu 
Miyuki 
Miz Callie-Inez 
Miz Tango-Lily 
Mizzthiang 
M-n-M (Mini Me) 
Mo 
MoBo 
Moca 
Mocha 
Mocha Cappuccino 
Mocha Cappucino 
Mocha chocha llama hottie 
Mocho Cappuccino 
Moco 
Moe 
Moet 
Mogget 
Mogwia 
Mohady 
Mohandas 
Mohave 
Mohawk 
MoJo 
Mojo-jo-jo 
MoJo-JoJo 
Moko 
Molder 
Moldy 
Moley 
Molli 
Molliemoose 
Molly 
Monday 
Moneokie 
Monica 
Monie 
Monkey-Boy 
Mono 
Monster 
Montana 
Montana Miracles 
Monte 
Monterey Jack Cheese 
Montezuma 
Montie 
Montique 
Monty 
Monty the Python 
Moo 
Moocho 
Mookie-doo 
Mookie-moo 
Mooku 
Moolan 
Moolander 
Moo Moo 
Moon 
Moondancer 
Moondust 
Moonlight 
Moonpie 
Moonstruck 
Moony 
Moose 
Mooshy 
Mops 
Mopsy 
Moreno 
Morgan 
Morgana 
Moritz 
Morley 
Morpheous 
Morpheus 
Morphious 
Morrigan 
Morris 
Morrison Jr. 
Morsel 
Morselina (Morsel) 
Mortimer 
Mortishia 
Morton 
Morumotto (pronounced mou-roo-MAHT-toh) 
Morwyn 
Moses 
Mossima (pronounced Moe-si-moe) 
Mosquito 
Moth 
Motley 
Motzi 
Mouchi 
Mouse 
Moustapha 
Mousy 
Mowhawk
Moxie 
Mozart 
Mozzerella 
Mr. Andy 
Mr. Billy 
Mr. Bojangles 
Mr. Bojangles-Francois 
Mr. Bubbles 
Mr. Chili 
Mr. Cookers 
Mr. Cookie 
Mr. Crabbitz 
Mr. Crabs 
Mr. Crowley 
Mr. Dickey Prickles 
Mr. Ed 
Mr. Evil 
Mr. Flop 
Mr. Fluffy 
Mr. French 
Mr. Frodo 
Mr. Ginners 
Mr. Hanky 
Mr. Krabs 
Mr. Magoo 
Mr. Mustaccio 
Mr. Nat 
Mr. Nibles 
Mr. Nibs 
Mr. Noah Rumples 
Mr. Pepper 
Mr. Pete 
Mr. Pig 
Mr. Pinch 
Mr. Pink 
Mr. Pooter 
Mr. President 
Mr. Prickles 
Mr. Priclesworth 
Mr. Rat 
Mr. Severum 
Mr. Sir 
Mr. Snowman 
Mr. Snuggles 
Mr. Sparkles 
Mr. Sticky 
Mr. T 
Mr. Ted-Ted 
Mr. Toodles 
Mr. Tudball 
Mr. Turtell 
Mr. Tutle 
Mr. Underfoot 
Mr. Velvet Ears 
Mr. Whiskas 
Mr. Whiskers 
Mr. Wigglesworth 
Mr. Wiggley Piggley 
Mrs. Crabapple 
Mrs. Ginners 
Mrs. Jiffy 
Mrs. Magnolia 
Mrs. Mrs 
Mrs. Pepper 
Mrs. Teasdale 
Mrs. Whiggins 
Mr. Wiggles 
Ms. Anaconda 
Ms. Boots 
Ms. Piggy 
Ms. Shopper 
Ms. T 
Ms. Wiggles Cochney 
Muchies 
Muchu 
Mucky 
Muddy 
Mudge 
Mudpit 
Mufasa 
Muff 
Muffin 
Muffin Mighty Pig 
Muffy 
Muggwye 
Mugs 
Mugsey 
Mumbles 
Munchkin 
Muppet 
Murphy 
Murray 
Murtle 
Murturtle 
Mush 
Musti 
Mutley 
Mutton 
Mya 
Myah 
Mylo 
Mynah 
Myra 
Mystery 
Mystic 
Mysty
Nacosha 
Nadia 
Nadine 
Naga 
Nahina Natani 
Naji 
Nakago 
Nakies 
Nakomi 
Nala 
Nambi 
Nana 
Nancy 
Nani 
Nanna 
Nannook 
Nannu 
Nannyskitty 
Nanook 
Napoleon 
Naraku 
Nat 
Natasha 
Nate 
Nathan 
Nathen 
Naudia 
Navi 
Navigator 
Nazar 
Ned 
Neddy 
Needles 
Needy 
Nefertiti 
Neffie (Nefratiti) 
Negri 
Neighbor 
Neiko 
Neko 
Nekosha 
Nell 
Nellie 
Nelly 
Nelson 
Nemo 
Neo 
Neon 
Neopolitan 
Nepeta 
Neph 
Nephertiti 
Nepolean 
Neptune 
Neptune Brian 
Nermal 
Nero 
Nessa 
Nessie 
Nestor 
Neutron Star 
Neva (as in "Neva again") 
Nevada 
Newt 
Newton 
Nexus 
Nezumi 
Nezumi Ninja 
Nezus 
Nia 
Nibble 
Nibbler 
Nibblers 
Nibbles 
Nibbs 
Nibsy 
Nichodemus 
Nichole 
Nickle 
Nicky 
Nicodemus 
Nicole 
Nigel 
Nigel Dorn Raschen aka "Piggy" 
Night-night 
Nike 
Nikita 
Nikki 
Nilla 
Nilla (pronounced Nee-la) 
Nimbus 
Nina 
Niner 
Ninja 
Ninja Cat 
Ninya 
Niobe 
Niobi 
Nipper 
Nipples 
Nipsey 
Nisey 
Nish 
Nishibi 
Nitrus 
Niv (short for Nivea) 
Nixie 
Noah 
Noblie 
Noel 
Noelle 
Nofeet 
Nokie 
Noni 
Noodle 
Noodles 
Nooshka 
Nora 
Norbert 
Norby 
Norma 
Norman 
Norvegicus 
Nosfer 
Nosferatu 
Nosy 
Nougat 
Nova 
November 
Nuba 
Nubbins 
Nugget 
Nuggz 
Number 1 
Number 2 
Nuriko 
Nusan 
Nutmeg 
Nutterbutter 
Nybras 
Nyla
Oatmeal 
Obelix 
Obie 
Obsidian 
Ocean 
October (Tobey for short) 
OdaMae 
Oddessy 
Oddity 
Odd One Out (Triple O) 
Oden 
Odet 
Odie 
Odies 
Odin 
Ody 
Odysseus 
Oggnob 
Ogua 
Ohana 
OJ 
Ojo 
Okolo 
Okwaho 
Old Man 
Olaf 
Olav 
Olga Marie 
Oli 
Olive 
Oliver 
Oliver 
Olivia 
Olli 
Ollie 
Olly 
O'Malley 
Omega 
Omelette 
One-Eyed Willie 
Onix 
Onyx 
Onzloe 
Oobie 
Oompa Loompa 
Opa 
Opal 
Ophelia 
Oracle 
Orange Boy 
Orange Moca Frappichino 
Orange Queen 
Orange Sherbert 
Orchid 
Orealve Reef 
Oreo 
Oreosh 
Oriel 
Orion 
Orkid 
Orkin 
Orlando 
Orli 
Ormond 
Orville 
Oscar 
Oscar Myer Weasel 
Osiris 
Ossi 
Otis 
Otto 
Owen 
Oz 
Ozzy
bio 
Pabst 
Pace 
Pacey 
Pacino 
Paco 
Paddy 
Padfoot 
Padme 
Paintere 
Pai Pai 
Pal 
Palikeke 
Pamela 
Pan 
Panca 
Pancake 
Pandora 
Panda 
Pandora LeFert 
Pansy 
Pantalaimon 
Panther 
Paper Clip 
Paris 
Parker 
Parnell Livingston 
Parsley 
Party Nugget
Pashmina 
Pasqualli 
Pastachio 
Pat 
Patch 
Patches 
Patchy 
Patit Tortue 
Patricia 
Patrick 
Patty 
Paul 
Paula 
Pauley 
Pauline 
Paws 
Pax 
Pazzaz 
PB 
P-bear 
P.C. (Problem Child) 
P. Diddy 
Pea 
Peabody 
Peaches 
Peach-O 
Peanut 
Peanut Butter 
Peanutbutter 
Pearl 
Pebbles 
Peddley 
Pedo 
Pedro 
Peede (PD) 
Peekaboo 
Peek-a-boo 
Peeko 
Peeper 
Peepers 
Peetree 
Peeves 
PeeWee 
Pegasus 
Peggy 
Peko 
Pemba 
Pene 
Peneloepe 
Penellope 
Penelope 
Pennelope 
Penny 
Penny-Lane 
Peony 
Pepe 
PePe 
Pepe La Pu 
Pep Pep
Pepper 
Pepperige (Pep) 
Peppermiz 
Pepperoni 
Peppy 
Peppy Pip Squeak 
Pepsi 
Pepsy 
Percy 
Perdie 
Perdita 
Perdy 
Periwinkle 
Perky 
Permythius 
Pernelle 
Perriwinkle 
Perry 
Persephone 
Petal 
Pete 
Peter 
Peterina 
Peter Paul 
Petey 
Petia 
Petre 
Petrie 
Petticoat 
Pettle 
Petunia 
Peublo 
Peurto 
Pewter 
Phagen 
Phantom 
Pheobie 
Phil 
Philiciti 
Phillip 
Phillipe 
Phoebe 
Phoebie 
Phoenix 
Phoenix River 
Phred 
Phyllis 
Picasso 
Picclo 
Piccolo 
Piccy 
Pickerington 
Pickle 
Pickles 
Pico 
Pie'r 
Pierr 
Pierre 
Pig Dog 
Pigglesworth Snortimer 
Piggy 
Piggyboy 
Piggy Sue 
Piglet 
Pig Pen 
Pigy 
Pika 
Pikachu 
Pinchy 
Pineapple 
Ping 
Ping Pong 
Pink 
Pinkerton 
Pinkie 
Pinky 
Pinstripe 
Pip 
Pipa 
Piper 
Piping 
Pipkin 
Pippa 
Pipper 
Pippi 
Pippilatus Willa-Mae 
Pippin 
Pipsqueak 
Pip Squeek 
Pique (pronounced pee-kay) 
Pirate 
Pisa 
Pistachio 
Piston 
Pita 
Pixel 
Pixie 
Pixil 
Pixy 
Pizza 
Pizzo 
PJ 
Plavador 
Plax 
Plaxico 
Pleo 
Pliskin 
Plopers 
Pluto 
P-nut 
Pocchi 
Pocket 
Pockets 
Poco 
Pocohontas 
Pogo 
Pokey 
Points 
Poison Berry 
Poke-a-Dot 
Poko 
Polish 
Pollux 
Polly 
Pollyanna 
Polo 
Polyester 
Pong 
Pongo 
Ponpon 
Pony 
Poof 
Pooh 
Pooka 
Pookey 
Pookie 
Pookie J 
Pookie Jetson 
Pookie-poo 
Pooky 
Poopoo 
Poo Poo Machine 
Poops-a-Lot 
Poopsi 
Poopsie 
Pootie 
Pop 
Popcorn 
Popeye 
Poppadom 
Popper 
Poppet 
Popples 
Poppy 
Popsicle 
Poptart 
Porkchop 
Pork Chop 
Porkie 
Porky 
Porsche 
Porthos 
Porticus 
Posidion 
Posiedon 
Potatoe 
Powder 
Powder Puff 
Prancer 
Pray 
Precious 
Predita 
Presley 
Preston 
Pretty 
Pretty Girl 
Pretzal 
Pretzel 
Pretzyl 
Prickly Poo 
Prince 
Prince Charming 
Prince of Midnight 
Princess Autumn Joy 
Princess 
Princesses 
Princess Fiona 
Princess Leah 
Princess Maisey 
Princess Peeanpoopalotta 
Princess Piggie 
Princess Priscilla Of Pink 
Princess Sunshine 
Princeton 
Pringle 
Print 
Prinz Ferdinand von Frettchen (Ferdie) 
Priscilla 
Prissy 
Priyadarshini 
Prof. Collene Wells 
Professor Dumbledore 
Professor Squeak 
Proffessor Whiskers 
Prongs 
Provel 
Prozac 
Prudence 
Prue 
Psycho 
P-taro 
Publius Cornelius Scipio Aemilianus Africanus 
Puck 
Puddin 
Puddin' 
Pudding 
Puddin' Pig 
Puddles 
Puff 
Puffdaddyo 
Puffin 
Puffkin 
Pug 
Pugnacious 
Pugnatious 
Pugsli 
Puma 
Pumba 
Pummy 
Pump 
Pumpers 
Pumpkin 
Pump Pump 
Pungey 
Punk 
Punkin 
Punky 
Punkyfish 
Punky-Girl 
Puppy 
Pupsu 
Purdy 
Purple Passion 
Purple Polar Bear 
Purple Tentacle 
Purpy 
Purty 
Puss 
Putter 
Puz 
Puzzles 
Pyp 
Pyramus
Q 
Qimmiq 
Q-Tip 
Quanah 
Quark 
Quartz 
Quasimoto 
Quatro 
Quazymoto 
Quechua (pronounced Qeechua) 
Queen 
Queenie 
Queen Snatch Cruella 
Quella Divill 
Quena 
Quentin 
Quentin Vislovious Cox 
Quick 
Quigley 
Quillen 
Quilliam Spike Tackett 
Quimby 
Quincy 
Quinkadink 
Quinn 
Quito 
Quiver 
Quwela Deivil
R32 Turbo 
Rabbit 
Rabitat 
Rabscuttle 
Rachel 
Rack 
Radar 
Radinski 
Rae 
Rafael 
Rafiki 
Rage 
Raggedy Ann 
Rags 
Raider 
Rain 
Rainbow 
Rainy 
Raisen 
Raisin 
Raisin Bun 
Raivi 
Raja 
Rajah 
Ralph 
Ralphie 
Ralston 
Rambler 
Rambo 
Ram-bore 
Ramses 
Ramzy 
Random 
Randy 
Ranger 
Ranger Rick 
Raphael 
Rascal 
Rasgal 
Rassi 
Rasta 
Rata-2-ee 
Ratbat 
Ratbert 
Rat Boy 
Ratigan 
Ratina 
Ratman 
Ratmandu 
Ratnick 
Rats Domino 
Rat-ta-tat 
Ratticus Finch 
Rattus 
Ratty 
Ratty Arbuckle 
Ratso 
Raven 
Ravenna 
Ravines Hannible 
Ray 
Raymond 
Raz 
Razzie 
Razzle 
Razzle-Dazzle Doggin & Biscuit Peter Pan Savage Puppy Blue Bee 
Razzle-Tazzle 
RB 
RcCola 
Reb 
Reba 
Rebal 
Rebekkah 
Rebel 
Recluse 
Red 
Redd 
Red Guy 
Reefer 
Reese 
Reese (s) 
Reeses 
Reeses Pieces 
Reggie 
Reggie Weggie 
Regina 
Reginal 
Reginauld 
Regster 
Reily 
Remmington 
Remy 
Ren 
Reno 
Reptar 
Retro 
Reverend Maynard 
Revlon 
Rev Norb 
Rex 
Rexy 
Rezin 
Rhino 
Ria 
Ribbit 
Ribbon 
Rib-Rab 
Richard 
Rickey-Ticky-Tavey 
Ricky 
Ricky-Ticky-Tabby 
Rico 
Rico Suave 
Riddick 
Riff Raff 
Rigby 
Rigsby 
Rikki 
Riley 
Rimmer 
Ringo 
Rio 
Ripple 
Riso 
Rita 
River 
River Cat 
Rizzo 
Roach 
Roast Beef 
Robbie 
Robby 
Robby Rabbit 
Robert 
Robert de Niro 
Roberto 
Robin 
Robyn 
Roca Mu Chocka (Roca for short) 
Roc-ci 
Rocco 
Roch (Roach) 
Rocket 
Rockey 
Rockie 
Rocko 
Rocky 
Rocky Balboa 
Rocky Doodle Dandy 
Rodeo 
Rodger 
Rodney 
Rodolfo 
Rodrigez 
Roger 
Rogue 
Roise 
Roli Poli Olli 
Rolo 
Roma 
Romeo 
Romey 
Ron 
Ronan 
Ronin 
Ronnie 
Ronoke (pronounced row-noke)
Roo 
Rookie 
Rookie Doo 
Roosevelt 
Rootbeer 
Rorschach 
Rory 
Rosa 
Rosalind 
Rosco 
Roscoe 
Rose 
Rosey 
Roshi 
Rosie 
Rosie Roo 
Rosita 
Ross 
Roswell 
Roudy 
R.O.U.S. (for Rodent Of Unusual Size) 
Roux (pronounced Roo) 
Rowdy 
Rowley 
Roxanne 
Roxey 
Roxie 
Roxy 
Rua 
Ruban 
Rubit 
Ruby 
Ruby Dee 
Ruckus 
Rudolph 
Rudy 
Rudy Ru 
Ruger 
Rugrat 
Ruffie 
Ruffus 
Ruffy 
Rufus 
Rumpled Pigskin 
Rumplesnakeskin 
Running Buffalo Wings 
Runt 
Rupert 
Rupurt 
Rusalka 
Russell 
Rusti 
Rusty 
Ryan 
Ryder 
Ryelle 
Rythum
Sabaloo 
Sabin 
Sable 
Sabre 
Sabrina 
Sadie 
Sadie Bella 
Safari 
Saffie 
Saffron 
Sage 
Sahara 
Sakana 
Saki 
Sal 
Salem 
Sally 
Sal Monella 
Salt 
Salty 
Salty VII 
Sam 
Samantha 
Samara 
Sambucca 
Sam Man 
Sammie 
Sammy 
Samoseto 
Sampson 
Samson 
Samuel 
Samule 
SamWise 
Samwise Gamgee (Sam) 
Sanar 
Sancho 
Sandino 
Sandusky 
Sandy 
Sandy Beans 
Sandy Bottom 
Sandy White Beans 
Sango 
Sanoma 
Santa 
Saphire 
Sapphire 
Sappho 
Sara 
Sarah 
Sarah Lee 
Sarge 
Sarsha Marie 
Sas 
Sasafras 
Sascha 
Sasha 
Sasha Marie 
Sasquatch 
Sassafras 
Sassy 
Sassy-Frass 
Satan 
Satchimo 
Satin 
Sativa 
Satsuki 
Saturn 
Sauron 
Sausage 
Savannah 
Sawdust 
Saydie 
Scabbers 
Scamp 
Scamper 
Scamperdoodle 
Scar 
Scar (Scar Snufulupagus) 
Scaramouch 
Scarlett 
Schnapps 
Schniffles 
Scooby 
Scooby Doo 
Scoota 
Scooter 
Scorpo 
Scorps 
Scotch 
Scout 
Scrappie 
Scrappy 
Scrat 
Scratch 
Scratches 
Scratchy 
Screecher 
Scroll 
Scrubbie 
Scruff 
Scruffes 
Scruffles 
Scrumpy 
Scully 
Scuni 
Scurry 
Scuttle 
Sea Biscuit 
Seafa 
Seamore 
Seattle 
Sebastian 
Sebastion 
Sedona 
Seifer (pronunced sigh-fur) 
Selenas 
Semlan 
Semolina 
Sephryn (pronounced seh-frin) 
Seraphim 
Serendipity 
Serenity 
Serpico 
Serrano 
Sessan 
Sesshomaru 
Seth 
Seto 
Seven 
Sexy 
Seymora 
Seymore 
Seymour 
Sgt Pepper 
Shabastin 
Shabby 
Shack 
Shade 
Shade 
Shadie 
Shadow 
Shadow Jay 
Shady 
Shaggy 
Shaka 
Shake 
Shakerboomboom 
Shakespeare 
Shakeypudding 
Shakira 
Sham 
Shammy 
Shamrock 
Shanade 
Shania 
Shaniqua-Shanaynay-Shabazz 
Shannara 
Shanon 
Shaq 
Shaquille 
Sharee 
Shark 
Shasade 
Sha-Sha (pronounced Shaw-Shaw) 
Shasta 
Shawna 
Shay 
Shayla 
Shearer 
Sheba 
Sheena 
Sheeva 
Sheila 
Shelby 
Sheldon 
Shell-Shocker 
Shelly 
Sherbert 
Serbet Tensing 
Sherburt 
Sherlock 
Sherman 
Sherry 
Shibby 
Shift 
Shika 
Shilo 
Shiloe 
Shiloh 
Shimmera (pronounced Shimmer-uh) 
Shining Star 
Shiori 
Shippo 
Shirley 
Shishkabob 
Shiva 
Shivers 
Shizzelle 
Shmoe 
Shmoo 
Shneaker 
Shoman 
Shopie 
Shorty 
Shreadder 
Shred 
Shredder 
Shrek 
Shubeedoo 
Shubert 
Shuga 
Shweedie 
Shy 
Shyla 
Shzuru 
Sian (pronounced Sharn) 
Sid 
Sidly 
Sidney 
Sigma 
Sienna 
Sierra 
Silk 
Silky 
Silly 
Silly Tilly Turtle 
Silver 
Silver Dutchess 
SilverSides 
Simba 
Simco 
Simon 
Simone 
Simpka 
Simply 
Simpson 
Simson 
Sinclair 
Sinjin 
Sioux 
Sir 
Sir. ButterRump 
Sir Christopher Thomas (aka Tommy) 
Sir. Cornelius Slithers 
Sir Fredrick Beauagard Basset the 1st 
Sir Fur 
Sir Hiss 
Sir Hops Alot 
Sir James 
Sir Nips-a-lot 
Sir Rabbitus Hopitus Furitus the Third 
Sir Reginald (Reggie) 
Sir Rodney's Marmalade 
Sir Scratch-A-Lot 
Sir Wigglesworth 
Sir William Wallice of the Rabbit Clan 
Sisi 
Sissy 
Sizzle 
Skampi 
Skeeter 
Skeezix 
Skettles 
Skinner 
Skinny 
Skip 
Skipper 
Skippy 
Skitter 
Skittles 
Skitz 
Skitzo 
Skokie 
Skooter 
Skorpan 
Skrollan 
Skunk 
Skweekers 
Sky 
Skydeypopsicle 
Skye 
Skyler 
Slam 
Slap 
Slash 
Slate 
Sleeps 
Sleepy 
Sleepy Magoo 
Slick 
Slider 
Slim 
Slinkster 
Slinky 
Slip 
Slipper 
Slippy 
Slithers 
Slowbro 
Slowpoke 
Slug 
Sly 
Slyder 
Slynky 
Slyther 
Small Fry 
Smaug 
Smeagol 
Smee 
Smee-Smoo 
Smeg 
Smelly 
Smidge 
Smiles 
Smiley 
Smirnoff 
Smoke
Smokeme 
Smokes 
Smokey 
Smokey Four Socks 
Smokey Jo 
Smokie 
Smoky 
Smoo 
Smooches 
Smores 
Smucker 
Smudge 
Smudgey 
Smuge 
Smugey 
Smurfy
Tab 
Tabbie 
Tabbris 
Tabitha 
Taboo 
Tac 
Taco 
Tacoma 
Taffy 
Tahoe 
Tai (pronounced Tie) 
Tai (pronounced Taya) 
Taima 
Taipei 
Taj 
Tak 
Tali 
Talia 
Talitha 
Tallulah 
Talula 
Tama-Chan 
Tamahome 
Tamale 
Tamika 
Tane 
Tang 
Tangie 
Tangle 
Tango 
Tangsodo 
Tank 
Tanker 
Tanki (pronounced Tonki)
Tanner 
Tanya 
Tao 
Tao Jin 
Tara 
Tarka 
Taro (long a, long o) 
Tarzan 
Tasha 
Tashia 
Tasket 
Tasslehoff 
Tasuki 
Tater 
Tater Tot 
Tavia 
Taya 
Tayla 
Taz 
Tazi 
Tazmina 
Tazo 
T-Bone 
Tea 
Teaka 
'Teaser 
Teasha 
TeCo 
Ted 
Teddy 
Teddybear 
Tedward 
Teeny 
Telescope 
Telfes 
Templeton 
Templeton Jr.
Tequi (pronounced Tee-kee, short for Tequila) 
Tequila 
Terkeles 
Terminator 
Terri 
Terry 
Tesa 
Tess 
Tessa 
Testudo 
Tethys 
Tetra 
Tex 
Thai 
Thanatos 
That Damn Mouse 
The Beast 
The Brain 
The Cheat 
The Chin Man 
The Colonel 
The Godfather 
The Professor Dumbledore 
The Rat! 
The Strangler 
The Tank 
Thee Incredible Mr. Limpett 
Thelma 
Themis 
Theo 
Theodore 
Thiery 
Thisbe 
Thissle 
Thomas 
Thor 
Threat 
Through-Streak 
Thumper 
Thumper Bumper 
Thunder 
Tia 
Tiago 
Tia-Maria 
Tiara 
Tibbs 
Tic 
Tica 
Tickles 
Tidy Bowl 
Tiere 
Tiffany 
Tiffs 
Tig 
Tiger 
Tigga 
Tigger 
Tigger Lynn 
Tike 
Tiki 
Tiko 
Tilli 
Tillie 
Tillikum 
Tilly 
Tim 
Timber 
Timmy 
Timofee 
Timon 
Tiney 
Tingle 
Tink 
Tinka 
Tinker 
Tinkerbell 
Tinkerbelle 
Tinkles 
Tinsy 
Tiny 
Tiny Tim 
Tipper 
Tips 
Titan 
Titana 
Tito 
Tiz 
Tizzy 
TJ 
Toadie 
Toast 
Tobey 
Toby 
Todd 
Toena 
Toffee 
Toffs 
Togadjijuji 
Tojo 
Tokie 
Tom 
Tomaye 
Tomcat 
Tom Cat 
Tommy 
Tonica 
Tonino 
Tonks 
Tonto 
Tony 
Tonya 
Toodilpip 
Tookie 
Tootie 
Tootsie 
Topaz 
Topper 
Topsy 
Torg 
Tork 
Tororo 
Torque 
Tortelli 
Tortuga 
Tosh 
Totero (toe-ter-oh) 
Totti 
Toula 
Touya 
Toxic 
Tragedy 
Tranquil 
Travis 
Treacle 
Treasure 
Treelo 
Trembles 
Trendi (accent over the "i") 
Trenity 
Trenton 
Tres 
Trevor 
Tricia 
Tricky 
Trigger 
Trikz 
Trina 
Trinket 
Trinity 
Trip 
Triple O (Odd One Out) 
Tripod 
Trisha 
Tristen 
Trivette 
Trix 
Trixie 
Trixie Shamele 
Trixy 
Trogdor 
Trojan 
Trooper 
Trouble 
Troubles 
Trudy 
True 
Truffles 
Trunks 
Tsing-Tao 
Tsunami 
Tubby 
Tubthumper 
Tucker 
Tuck-Tuck 
Tudball 
Tuela 
Tuff 
Tuffer 
Tuffnel 
Tuffy 
Tufty 
Tui 
Tukkie 
Tulip 
Tullie 
Tulula 
Tunie 
Tuppence 
Turbo 
Turby 
Turdman 
Turddy 
Turkey Bird 
Turkish 
Turtle 
Tushie 
Tutanka 
Tu-Tone 
Tuts 
Tutter 
Tutu 
Tuvok 
Tweak 
Tweakers 
Tweedle 
Tweedle Dee 
Tweedle Dum 
Tweek 
Tweeker 
Tweety 
Twiggy 
Twinkie 
Twinkle 
Twinkles 
Twisted Whiskers 
Twister 
Twisty 
Twix 
Twizzler 
Twizzler Twix (Tizzy) 
Twoface 
Twonka 
Tyco 
Tyler 
Tyrone 
Tyson 
Tzing-Yu 
Tsipora
UGA 
Uhura 
Ulises 
Ulysses 
Uma 
Umbridge 
Una 
Uncle Buck (Bucky) 
Uncle Chocolate 
Uncle Jessie 
Unelem 
Unger 
Uno 
Upir 
Ursula 
Usagi 
Usama 
Ushanka 
Utong 
Uzi
Valdez 
Valentina Rayne 
Valentine 
Valentino 
Valerie 
Valintina 
Valkyrie 
Vanilla 
Van Morrison 
Vash 
Veda 
Vega 
Vegas 
Vegeta 
Veggie 
Veil 
Velma 
Velveeta 
Velvet 
Velveteen 
Velvette 
Venenito 
Veneno 
Venus 
Veronica 
Veronica Boldy 
Versatchi 
Victoria 
Videl 
Vince "Fingerprint" Vaughn 
Vincent 
Vin Diesel 
Vinny 
Vin Veasel 
Violet 
Virgo 
Vito 
Vittorio 
Vivor 
Volcom 
Voldy 
Voodoo 
Vladimar 
Vladamir 
Vyolet
Waffles 
Waikiki 
Waldo 
Wall 
Wallace 
Walla-Walla 
Wallie 
Walker 
Walnut 
Walter 
Wander 
Wangsta 
WannaHawkALoogie 
Warren 
Warturtle 
Washee 
Waunder 
Wauwi 
Wayne Rooney 
Waxy Q-tip 
Waya 
Weasel 
Weasle 
Weasley 
Webber 
Webster 
Wednesday 
Weeble 
WeeBunBun Onion 
Weetabix 
Weetie 
Weezer 
Weezie Woo Woo 
Weezy 
Weezy the Weasel 
Wendi 
Wendy Lady 
Wesley 
Wexlton 
Wheater 
Wheeler 
Whip 
Whipper 
Whipple 
Whiskers 
Whiskey 
Whisky 
Whisper 
White Kitty 
White Pug 
Whitey 
Whitie 
Whizzah 
Whizzer 
Whompus Tid 
Whopper 
Wicket 
Widget 
Wiggle 
Wiggles 
Wiggy 
Wilbuhr 
Wilbur 
Wildfire 
Wild Thing 
Wiley 
Wiley Wat 
Willard 
William 
William SNakespeare 
William Wallace 
Willie 
Willoughby 
Willow 
Wilma 
Winchester 
Wind-dee 
Windex 
Winkie 
Winkin' 
Winky 
Winnie 
Winston 
Winter 
Wishee 
Wishes 
Wittle Baby 
Wizz 
Wizzer 
Wizzy 
Wolf 
Wolfgang 
Wolfie 
Wolly 
Wombat Wonker Will Junior (Wombo) 
Wommbie 
Wonder 
Wonka 
Woodstock 
Woody 
Woofy 
Wookie 
Woolly Bear 
Woozel 
Wozza 
Wrangler 
Wrenna 
Wrigbee 
Wufei 
Wufie 
Wyatt 
Wyatt B. Urp 
Wynjara 
Wysiwyg (What You See Is What You Get)
Xandir 
Xavier 
Xena 
Xeno 
X-Force 
Xibalba 
Xylophone
Yagers 
Yakky 
Yamcha 
Yang 
Yarndi 
Yayo 
Yazmin 
Yellownose 
Yerba 
Ying 
Yma 
Yoda 
Yogi 
Yogurt 
Yoh Asakura 
Yolanda 
Yoshi 
Yoshihiro 
You BAD Rat 
Youko 
Yo-Yo 
YO-YO Britches 
Yssup 
Yugi 
Yukina 
Yukon 
Yurtle 
Yurtle the Turtle 
Yusuke
Zachariah 
Zacherie 
Zack 
Zaffle 
Zak 
Zakk 
Zander 
Zanzibar 
Zap 
Zarba 
Zazu 
Zebra 
Zed 
Zeeko 
Zeke 
Zelda 
Zemo 
Zen 
Zena 
Zenny 
Zephyr 
Zeppelin 
Zeppo 
Zero 
Zeus 
Ziah 
Zigbert 
Ziggy 
ZigZag 
Zilla 
Zin (Zinny) 
Zipper 
Zippo 
Zippy 
Zizzi 
Zobique 
Zoe 
Zoey 
Zoe-Zo 
Zookie 
Zoombini 
Zooter 
Zorom 
Zorro 
Zues 
Zuku 
Zylonna 
Zypp 
Zzo
""".split("\n")

def get_random_name() -> str:
    return random.choice(NAMES)

def get_random_single_word_name() -> str:
    """ Returns only names that are a single word """
    while True:
        name = get_random_name()
        if name.find(" ") == -1 and name.strip() != "":
            return name
