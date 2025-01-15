from websecurity.components.data_ingestion import DataIngestion
from websecurity.components.data_validation import DataValidation
from websecurity.exception.exception import WebShieldException
from websecurity.logging.logger import logging
from websecurity.entity.config_entity import DataIngestionConfig,DataValidationConfig 
from websecurity.entity.config_entity import TrainingPipelineConfig
import sys

if __name__=="__main__":
    try:
       trainingpipelineconfig=TrainingPipelineConfig()
       dataingestionconfig=DataIngestionConfig(trainingpipelineconfig)
       data_ingestion=DataIngestion(dataingestionconfig)
       logging.info("Initiate the data ingestion")
       dataingstionartifact=data_ingestion.intiate_data_ingestion()
       logging.info("Data Ingestiom is completed")
       data_validation_config=DataValidationConfig(trainingpipelineconfig)
       data_validation=DataValidation(dataingestionconfig,data_validation_config)
       logging.info("Inititate Data Validations")
       data_validation_artifact=data_validation.initiate_data_validation()
       logging.info("Data Validation completed")
       print(data_validation_artifact)
    except Exception as e:
        raise WebShieldException(e,sys)
