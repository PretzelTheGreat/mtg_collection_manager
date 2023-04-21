def get_deck_stats(deck):
    deck_stats = {"commander": 1}

    for k, v in deck["the_99"].items():
        if  k == "basic_lands":
            deck_stats["basic_lands"] = sum(v.values())

        elif len(v) != 0:
            deck_stats[k] = len(v)

    return deck_stats

def print_deck_stats(deck):
    deck_stats = get_deck_stats(deck)

    print(f"Deck Name: {deck['name']}, Commander: {deck['commander']}")
    print(f"Deck Theme: {deck['theme']}")

    for k, v in deck_stats.items():
        print(f"\t{k}: {v}")

    print(f"Total Cards in deck: {sum(deck_stats.values())}")