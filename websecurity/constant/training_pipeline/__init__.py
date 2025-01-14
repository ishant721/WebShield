import os 
import sys 
import pandas as pd
import numpy as np 

TARGET_COLUMN = "Result"
PIPELINE_NAME = "Web Shield"
ARTIFACT_DIR = "Artifacts"
FILE_NAME = "phisingData.csv"

TRAIN_FILE_NAME : str = "train.csv"
TEST_FILE_NAME : str = "test.csv"

DATA_INGESTION_COLLECTION_NAME : str = "WebData"
DATA_INGESTION_DATABASE_NAME : str ="Ishant"
DATA_INGESTION_DIR_NAME : str = "data_ingestion"
DATA_INGESTION_FEATURE_STORE_DIR : str = "feature store"
DATA_INGESTION_INGESTED_DIR: str = "ingested"
DATA_INGESTION_TRAIN_TEST_SPLIT_RATION: float = 0.2