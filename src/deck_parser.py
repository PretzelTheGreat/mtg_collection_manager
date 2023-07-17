import src.pricing_info as pricing_info

def get_deck_stats(deck, pricing_data):
    deck_stats = {"commander": 1}

    for k, v in deck["the_99"].items():
        if  k == "basic_lands":
            deck_stats["basic_lands"] = sum(v.values())

        elif len(v) != 0:
            deck_stats[k] = len(v)

    deck_stats["deck_value"] = pricing_info.get_valuation_of_deck(deck, pricing_data)

    return deck_stats

def print_deck_stats(deck, pricing_data):
    deck_stats = get_deck_stats(deck, pricing_data)
    deck_value = deck_stats.pop('deck_value')

    print(f"Deck Name: {deck['name']}, Commander: {deck['commander']['name']}")
    print(f"Deck Theme: {deck['theme']}")

    for k, v in deck_stats.items():
        print(f"\t{k}: {v}")

    print(f"Total Cards in deck: {sum(deck_stats.values())}")
    print(f"Total Deck Value: ${deck_value}")

def convert_deck_to_csv_format(deck):
    # this can be used to convert a deck list to the csv format
    # used to add to the collection database. primarily used if
    # the decklist cards aren't already accounted for in the database
    # i.e you create the decklist first before having the cards in the
    # database
    cards_to_convert = []

    f = {"name": "", "setCode": "", "setNumber": "", "treatment": "", "num_of_treatment": 1, "num_in_use": 1}

    # add commander
    f["name"] = deck["commander"]["name"]
    f["setCode"] = deck["commander"]["setCode"]
    f["treatment"] = deck["commander"]["treatment"]
    f["setNumber"] = deck["commander"]["setNumber"]

    cards_to_convert.append(f)

    for card_type, cards in deck["the_99"].items():
        if card_type != "basic_lands" and len(cards) > 0:
            for card in cards:
                f = {"name": "", "setCode": "", "setNumber": "", "treatment": "", "num_of_treatment": 1, "num_in_use": 1}
                f["name"] = card["name"]
                f["setCode"] = card["setCode"]
                f["treatment"] = card["treatment"]
                f["setNumber"] = card["setNumber"]
                cards_to_convert.append(f)

    return cards_to_convert