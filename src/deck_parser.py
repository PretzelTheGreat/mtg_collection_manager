import src.pricing_info as pricing_info

def get_deck_stats(deck, pricing_data=None):
    deck_stats = {"commander": 1}
    basic_lands = {}

    for k, v in deck["the_99"].items():
        if  k == "basic_lands":
            for card in v:
                if card["name"] not in basic_lands.keys():
                    basic_lands[card["name"]] = 1
                else:
                    basic_lands[card["name"]] += 1
            deck_stats["basic_lands"] = sum(basic_lands.values())

        elif len(v) != 0:
            deck_stats[k] = len(v)

    if pricing_data != None:
        deck_stats["deck_value"] = pricing_info.get_valuation_of_deck(deck, pricing_data)
    else:
        deck_stats["deck_value"] = None

    return deck_stats

def print_deck_stats(deck, pricing_data = None):
    deck_stats = get_deck_stats(deck, pricing_data=pricing_data)
    deck_value = deck_stats.pop('deck_value')

    print(f"Deck Name: {deck['name']}, Commander: {deck['commander']['name']}")
    print(f"Deck Theme: {deck['theme']}")

    for k, v in deck_stats.items():
        print(f"\t{k}: {v}")

    print(f"Total Cards in deck: {sum(deck_stats.values())}")
    if deck_value != None:
        print(f"Total Deck Value: ${deck_value}")

def dedupe_basic_lands(basic_lands):
    new_basic_lands = {}

    # {"name": "", "setCode": "", "setNumber": "", "treatment": "", "num_of_treatment": 1, "num_in_use": 0}

    for card in basic_lands:
        combined_name = f"{card['name']}:{card['setCode']}:{card['setNumber']}:{card['treatment']}"
        if combined_name not in new_basic_lands.keys():
            new_basic_lands[combined_name] = card

        else:
            new_basic_lands[combined_name]['num_of_treatment'] += card['num_of_treatment']
            new_basic_lands[combined_name]['num_in_use'] += card['num_in_use']

    return list(new_basic_lands.values())

def convert_deck_to_csv_format(deck):
    # this can be used to convert a deck list to the csv format
    # used to add to the collection database. primarily used if
    # the decklist cards aren't already accounted for in the database
    # i.e you create the decklist first before having the cards in the
    # database
    cards_to_convert = []

    f = {"name": "", "setCode": "", "setNumber": "", "treatment": "", "num_of_treatment": 1, "num_in_use": 0}
    if deck["deck_in_use"]:
        f["num_in_use"] = 1

    # add commander
    f["name"] = deck["commander"]["name"]
    f["setCode"] = deck["commander"]["setCode"]
    f["treatment"] = deck["commander"]["treatment"]
    f["setNumber"] = deck["commander"]["setNumber"]

    cards_to_convert.append(f)

    for card_type, cards in deck["the_99"].items():
        if card_type != "basic_lands" and len(cards) > 0:
            for card in cards:
                f = {"name": "", "setCode": "", "setNumber": "", "treatment": "", "num_of_treatment": 1, "num_in_use": 0}
                if deck["deck_in_use"]:
                    f["num_in_use"] = 1
                f["name"] = card["name"]
                f["setCode"] = card["setCode"]
                f["treatment"] = card["treatment"]
                f["setNumber"] = card["setNumber"]
                cards_to_convert.append(f)
        elif card_type == "basic_lands":
            basic_lands = []
            for card in cards:
                f = {"name": "", "setCode": "", "setNumber": "", "treatment": "", "num_of_treatment": 1, "num_in_use": 0}
                if deck["deck_in_use"]:
                    f["num_in_use"] = 1
                f["name"] = card["name"]
                f["setCode"] = card["setCode"]
                f["treatment"] = card["treatment"]
                f["setNumber"] = card["setNumber"]
                basic_lands.append(f)
            deduped_lands = dedupe_basic_lands(basic_lands)
            cards_to_convert.extend(deduped_lands)


    return cards_to_convert