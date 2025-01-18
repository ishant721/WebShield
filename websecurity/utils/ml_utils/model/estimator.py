from websecurity.constant.training_pipeline import SAVED_MODEL_DIR,MODEL_FILE_NAME
import os
import sys

from websecurity.exception.exception import WebShieldException
from websecurity.logging.logger import logging

class NetworkModel:
    def __init__(self,preprocessor,model):
        try:
            self.preprocesssor=preprocessor
            self.model=model
        except Exception as e:
            raise WebShieldException(e,sys) from e
        
    def predict(self,x):
        try:
            X_transform=self.preprocessor.transform(x)
            y_hat=self.model.predict(X_transform)
            return y_hat
        except Exception as e:
            raise WebShieldException(e,sys) from e