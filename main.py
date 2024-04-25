import src.collection_manager as collection_manager

# Main Collection
# collection_filename = "resources/databases/my_collection.json"
# collection = collection_manager.CollectionManager(collection_filename, debug_level="INFO")

# collection.export_pricing_data(include_in_use=True)
# print("Exported pricing data for collection")

# OTJ rares
collection_filename = "resources/databases/my_collection_2024.json"
my_collection = collection_manager.CollectionManager(collection_filename, skip_decks=True, debug_level="ERROR")
value_at_100 = my_collection.calculate_value_of_collection()
print(f"Collection Value: ${value_at_100}")
print(f"Highest value card: {my_collection.highest_value_card}")
my_collection.export_pricing_data(include_in_use=True)
