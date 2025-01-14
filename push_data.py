import os
import sys
import json
import certifi
import pandas as pd
import numpy as np
import pymongo
from dotenv import load_dotenv
from websecurity.exception.exception import WebShieldException
from websecurity.logging.logger import logging

# Load environment variables
load_dotenv()

# Fetch MongoDB URL from environment variables
MONGO_DB_URL = os.getenv("MONGO_DB_URL")

# Ensure the MongoDB URL is provided
if not MONGO_DB_URL:
    raise ValueError("MONGO_DB_URL is not set in the environment variables.")

# Certificate for secure MongoDB connection
ca = certifi.where()

class WebDataExtract:
    def __init__(self):
        try:
            # Initialize MongoDB client
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
            logging.info("MongoDB client initialized successfully.")
        except Exception as e:
            raise WebShieldException(e, sys)

    def csv_to_json_converter(self, file_path):
        """
        Converts a CSV file to a JSON-like list of records.
        """
        try:
            logging.info(f"Reading CSV file from path: {file_path}")
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            logging.info(f"Successfully converted CSV to JSON records: {len(records)} records found.")
            return records
        except FileNotFoundError:
            logging.error(f"File not found: {file_path}")
            raise WebShieldException(f"File not found: {file_path}", sys)
        except Exception as e:
            raise WebShieldException(e, sys)

    def insert_data_to_mongodb(self, records, database, collection):
        """
        Inserts a list of JSON-like records into a MongoDB collection.
        """
        try:
            logging.info(f"Inserting data into MongoDB: Database={database}, Collection={collection}")
            db = self.mongo_client[database]
            col = db[collection]
            result = col.insert_many(records)
            logging.info(f"Inserted {len(result.inserted_ids)} records into MongoDB.")
            return len(result.inserted_ids)
        except pymongo.errors.PyMongoError as e:
            logging.error(f"MongoDB error: {e}")
            raise WebShieldException(e, sys)
        except Exception as e:
            raise WebShieldException(e, sys)

if __name__ == '__main__':
    try:
        # Configuration for the script
        FILE_PATH = 'Network_Data/phisingData.csv'  # Ensure this path exists
        DATABASE = "Ishant"
        COLLECTION = "WebData"

        # Initialize the class
        web_obj = WebDataExtract()

        # Convert CSV to JSON records
        records = web_obj.csv_to_json_converter(file_path=FILE_PATH)
        print(records)
        # Insert records into MongoDB
        no_of_records = web_obj.insert_data_to_mongodb(records, DATABASE, COLLECTION)

        # Print the number of records inserted
        print(f"Successfully inserted {no_of_records} records into MongoDB.")
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
