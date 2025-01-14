from websecurity.components.data_ingestion import DataIngestion
from websecurity.exception.exception import WebShieldException
from websecurity.logging.logger import logging
from websecurity.entity.config_entity import DataIngestionConfig
from websecurity.entity.config_entity import TrainingPipelineConfig
import sys

if __name__=="__main__":
    try:
       trainingpipelineconfig=TrainingPipelineConfig()
       dataingestionconfig=DataIngestionConfig(trainingpipelineconfig)
       data_ingestion=DataIngestion(dataingestionconfig)
       logging.info("Initiate the data ingestion")
       dataingstionartifact=data_ingestion.intiate_data_ingestion()
       print(dataingstionartifact)
    except Exception as e:
        raise WebShieldException(e,sys)
