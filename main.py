from websecurity.components.data_ingestion import DataIngestion
from websecurity.components.data_validation import DataValidation
from websecurity.components.data_transformation import DataTransformation
from websecurity.exception.exception import WebShieldException
from websecurity.components.model_trainer import ModelTrainer
from websecurity.logging.logger import logging
from websecurity.entity.config_entity import DataIngestionConfig,DataValidationConfig ,DataTransformationConfig,ModelTrainerConfig
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
       data_transformation_config=DataTransformationConfig(trainingpipelineconfig)
       logging.info("Data Tranformation started")
       data_tranformation=DataTransformation(data_validation_artifact,data_transformation_config)
       data_transformation_artifact=data_tranformation.initiate_data_transformation()
       logging.info("Data Tranformation completed")
       print(data_transformation_artifact)
       logging.info("Model Training stared")
       model_trainer_config=ModelTrainerConfig(trainingpipelineconfig)
       model_trainer=ModelTrainer(model_trainer_config=model_trainer_config,
                                  data_transformation_artifact=data_transformation_artifact)
       model_trainer_artifact=model_trainer.initiate_model_trainer()
       logging.info("Model Training artifact created")
    except Exception as e:
        raise WebShieldException(e,sys)
