import pymongo.mongo_client
from websecurity.exception.exception import WebShieldException
from websecurity.logging.logger import logging

# Config file for DataIngestion Config
from websecurity.entity.config_entity import DataIngestionConfig
from websecurity.entity.artifact_entity import DataIngestionArtifact

import os
import sys
import pymongo
import numpy as np
import pandas as pd
from typing import List
from sklearn.model_selection import train_test_split

from dotenv import load_dotenv
load_dotenv()

MONGO_DB_URL = os.getenv("MONGO_DB_URL")

class DataIngestion:
    def __init__(self, data_ingestion_config: DataIngestionConfig):
        try:
            self.data_ingestion_config = data_ingestion_config
        except Exception as e:
            raise WebShieldException(e, sys)

    # Reading DataFrame from MongoDB
    def export_collection_as_dataframe(self):
        try:
            database = self.data_ingestion_config.database_name
            collection_name = self.data_ingestion_config.collection_name
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL)
            collection = self.mongo_client[database][collection_name]

            df = pd.DataFrame(list(collection.find()))

            if "_id" in df.columns.to_list():
                df.drop(columns=["_id"], axis=1, inplace=True)  # Fixed assignment issue

            df.replace({"na": np.nan}, inplace=True)

            return df

        except Exception as e:
            raise WebShieldException(e, sys)  # Fixed missing parameters

    # Exporting Data into Feature Store
    def export_data_into_feature_store(self, dataframe: pd.DataFrame):
        try:
            feature_store_file_path = self.data_ingestion_config.feature_store_file_path
            # Creating folder
            dir_path = os.path.dirname(feature_store_file_path)
            os.makedirs(dir_path, exist_ok=True)
            dataframe.to_csv(feature_store_file_path, index=False, header=True)  # Fixed method name
            return dataframe
        except Exception as e:
            raise WebShieldException(e, sys)

    # Splitting Data into Train/Test
    def split_data_into_train_test_split(self, dataframe=pd.DataFrame):
        try:
            train_set, test_set = train_test_split(
                dataframe, test_size=self.data_ingestion_config.train_test_split_ratio  # Fixed attribute access
            )

            logging.info("Performed train-test split on the DataFrame.")
            logging.info("Exiting split_data_into_train_test method of the DataIngestion class.")

            dir_path = os.path.dirname(self.data_ingestion_config.training_file_path)
            os.makedirs(dir_path, exist_ok=True)

            logging.info("Exporting train and test file paths.")

            train_set.to_csv(
                self.data_ingestion_config.training_file_path, index=False, header=True
            )
            test_set.to_csv(
                self.data_ingestion_config.testing_file_path, index=False, header=True
            )

            logging.info("Exported train-test CSV files.")
        except Exception as e:
            raise WebShieldException(e, sys)

    # Initiating Data Ingestion
    def intiate_data_ingestion(self):
        try:
            dataframe = self.export_collection_as_dataframe()
            dataframe = self.export_data_into_feature_store(dataframe)  # Fixed method call
            self.split_data_into_train_test_split(dataframe)

            dataingestionartifact = DataIngestionArtifact(
                trained_file_path=self.data_ingestion_config.training_file_path,
                test_file_path=self.data_ingestion_config.testing_file_path  # Fixed typo in attribute name
            )

            return dataingestionartifact
        except Exception as e:
            raise WebShieldException(e, sys)
