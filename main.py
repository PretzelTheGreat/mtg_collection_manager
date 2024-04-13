import src.collection_manager as collection_manager

# Main Collection
# collection_filename = "resources/databases/my_collection.json"
# collection = collection_manager.CollectionManager(collection_filename, debug_level="INFO")

# collection.export_pricing_data(include_in_use=True)
# print("Exported pricing data for collection")

# OTJ rares
collection_filename = "resources/databases/OTJ_rares.json"
otj_rares = collection_manager.CollectionManager(collection_filename, debug_level="INFO")
otj_rares.export_pricing_data()
