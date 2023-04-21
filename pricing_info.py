import util_funcs

# at some point, include automatically downloading and unzipping the required files from https://mtgjson.com/downloads/all-files/

def create_name_to_uuid_mapping(identifiers):
    # because the data from MTGJSON is a large file with a bunch of unecessary data
    # the intent of this function is to map the name of a card to it's UUID, letting
    # the rest of the data be released from memory

    # multiple printings are handled by using the setcode as a key, and the uuid as a value
    mapping = {}

    for k, v in identifiers.items():
        if mapping.get(v['name']):
            mapping[v['name']][v['setCode']] = k

        else:
            mapping[v['name']] = {v['setCode']: k}

    return mapping

identifiers = util_funcs.import_json_file("resources/AllIdentifiers.json")
identifiers_clean = create_name_to_uuid_mapping(identifiers['data'])
del identifiers # releasing the file here since the data within is no longer needed

price_info = util_funcs.import_json_file("resources/AllPrices.json")