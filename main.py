import src.collection_manager as collection_manager

# Main Collection
# collection_filename = "resources/databases/my_collection.json"
# collection = collection_manager.CollectionManager(collection_filename, debug_level="INFO")

# collection.export_pricing_data(include_in_use=True)
# print("Exported pricing data for collection")

# OTJ rares
collection_filename = "resources/databases/OTJ_rares.json"
otj_rares = collection_manager.CollectionManager(collection_filename, skip_decks=True, debug_level="ERROR")
value_at_100 = otj_rares.calculate_value_of_collection()
print(f"Value of OTJ rares ($2 minimum): {value_at_100}\nHighest value card: {otj_rares.highest_value_card}")
otj_rares.export_pricing_data()
