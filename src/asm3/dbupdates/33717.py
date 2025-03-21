# Add default colour mappings to existing colours if they
# have not been mapped already
defmap = {
    1: "Black",
    2: "White",
    3: "Black - with White",
    4: "Red/Golden/Orange/Chestnut",
    5: "White - with Black",
    6: "Tortoiseshell",
    7: "Brown Tabby",
    8: "Tan/Yellow/Fawn",
    9: "Black - with Tan, Yellow or Fawn",
    10: "Black - with Tan, Yellow or Fawn",
    11: "Brown/Chocolate",
    12: "Brown/Chocolate - with Black",
    13: "Brown/Chocolate - with White",
    14: "Brindle",
    15: "Brindle",
    16: "Brindle - with White",
    17: "Black - with Tan, Yellow or Fawn",
    18: "White - with Tan, Yelow or Fawn",
    19: "Tricolor (Tan/Brown & Black & White)",
    20: "Brown/Chocolate",
    21: "Brown/Chocolate - with White",
    22: "Brown/Chocolate - with White",
    23: "White",
    24: "White - with Tan, Yellow or Fawn",
    26: "White - with Tan, Yellow or Fawn",
    27: "Tortoiseshell",
    28: "Brown Tabby",
    29: "Red/Golden/Orange/Chestnut - with White",
    30: "Gray/Blue/Silver/Salt & Pepper",
    31: "Gray/Silver/Salt & Pepper - with White",
    32: "Gray/Silver/Salt & Pepper - with White",
    33: "Tortoiseshell",
    35: "Brown/Chocolate - with White",
    36: "Gray or Blue",
    37: "White",
    38: "Tan/Yellow/Fawn",
    39: "Tan/Yellow/Fawn",
    40: "Brown/Chocolate - with White",
    41: "Green",
    42: "Red/Golden/Orange/Chestnut",
    43: "Tortoiseshell",
    44: "Tortoiseshell",
    45: "Brown/Chocolate",
    46: "Tortoiseshell",
    47: "Red/Golden/Orange/Chestnut",
    48: "Tortoiseshell",
    49: "Tan/Yellow/Fawn",
    50: "Tortoiseshell",
    51: "Red/Golden/Orange/Chestnut",
    52: "Red/Golden/Orange/Chestnut",
    53: "Gray/Blue/Silver/Salt & Pepper",
    54: "Tortoiseshell",
    55: "Red/Golden/Orange/Chestnut",
    56: "Tan/Yellow/Fawn",
    57: "Gray/Blue/Silver/Salt & Pepper",
    58: "Red/Golden/Orange/Chestnut",
    59: "Tortoiseshell",
}
for c in dbo.query("SELECT ID FROM basecolour WHERE ID <= 59 AND (AdoptAPetColour Is Null OR AdoptAPetColour = '')"):
    if c["ID"] in defmap:
        execute(dbo,"UPDATE basecolour SET AdoptAPetColour=? WHERE ID=?", [ defmap[c["ID"]], c["ID"] ])
