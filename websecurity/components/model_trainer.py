import os
import sys
from websecurity.exception.exception import WebShieldException 
from websecurity.logging.logger import logging

from websecurity.entity.artifact_entity import DataTransformationArtifact, ModelTrainerArtifact
from websecurity.entity.config_entity import ModelTrainerConfig

from websecurity.utils.ml_utils.model.estimator import NetworkModel
from websecurity.utils.main_utils.utils import save_object, load_object
from websecurity.utils.main_utils.utils import load_numpy_array_data, evaluate_models
from websecurity.utils.ml_utils.metric.classification_metric import get_classification_score

from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    AdaBoostClassifier,
    GradientBoostingClassifier,
    RandomForestClassifier,
)
import mlflow

class ModelTrainer:
    def __init__(self, model_trainer_config: ModelTrainerConfig, data_transformation_artifact: DataTransformationArtifact):
        try:
            self.model_trainer_config = model_trainer_config
            self.data_transformation_artifact = data_transformation_artifact
        except Exception as e:
            raise WebShieldException(e, sys)

    def track_mlflow(self, model_name, model, classification_metric, stage, input_example=None):  
        try:
            with mlflow.start_run():
                # Log metrics
                mlflow.log_metric(f"{stage}_f1_score", classification_metric.f1_score)
                mlflow.log_metric(f"{stage}_precision", classification_metric.precision_score)
                mlflow.log_metric(f"{stage}_recall", classification_metric.recall_score)

                # Log the model with input_example
                mlflow.sklearn.log_model(
                    sk_model=model,
                    artifact_path=model_name,
                    registered_model_name=f"{model_name}_{stage}",
                    input_example=input_example,  
                )
        except Exception as e:
            raise WebShieldException(e, sys)

    def train_model(self, X_train, y_train, X_test, y_test):
        models = {
            "Random Forest": RandomForestClassifier(verbose=1),  
            "Decision Tree": DecisionTreeClassifier(),
            "Gradient Boosting": GradientBoostingClassifier(verbose=1), 
            "Logistic Regression": LogisticRegression(verbose=1),  
            "AdaBoost": AdaBoostClassifier(),
        }
        params = {
            "Decision Tree": {
                'criterion': ['gini', 'entropy'],
                'splitter': ['best', 'random'],
                'max_features': ['sqrt', 'log2'],
            },
            "Random Forest": {
                'criterion': ['gini', 'entropy', 'log_loss'],
                'max_features': ['sqrt', 'log2'],
                'n_estimators': [8, 16, 32, 128, 256],
            },
            "Gradient Boosting": {
                'loss': ['log_loss', 'exponential'],
                'learning_rate': [.1, .01, .05, .001],
                'subsample': [0.6, 0.7, 0.75, 0.85, 0.9],
                'criterion': ['squared_error', 'friedman_mse'],
                'max_features': ['sqrt', 'log2'],
                'n_estimators': [8, 16, 32, 64, 128, 256],
            },
            "Logistic Regression": {},
            "AdaBoost": {
                'learning_rate': [.1, .01, .001],
                'n_estimators': [8, 16, 32, 64, 128, 256],
            }
        }

        # Evaluate models and get the best one
        model_report: dict = evaluate_models(
            X_train=X_train, y_train=y_train, X_test=X_test, y_test=y_test,
            models=models, params=params)
        best_model_score = max(sorted(model_report.values()))
        best_model_name = list(model_report.keys())[
            list(model_report.values()).index(best_model_score)
        ]
        best_model = models[best_model_name]

        # Get training metrics
        y_train_pred = best_model.predict(X_train)
        classification_train_metric = get_classification_score(y_true=y_train, y_pred=y_train_pred)

        # Track training metrics with MLflow
        input_example = X_train[:1]  # Used a small subset of X_train for input_example
        self.track_mlflow(best_model_name, best_model, classification_train_metric, "train", input_example=input_example)

        # Get testing metrics
        y_test_pred = best_model.predict(X_test)
        classification_test_metric = get_classification_score(y_true=y_test, y_pred=y_test_pred)

        # Track testing metrics with MLflow
        self.track_mlflow(best_model_name, best_model, classification_test_metric, "test", input_example=input_example)

        # Save the preprocessor and model
        preprocessor = load_object(file_path=self.data_transformation_artifact.transformed_object_file_path)
        model_dir_path = os.path.dirname(self.model_trainer_config.trained_model_file_path)
        os.makedirs(model_dir_path, exist_ok=True)

        # Wrap preprocessor and model into a NetworkModel
        Network_Model = NetworkModel(preprocessor=preprocessor, model=best_model)
        save_object(self.model_trainer_config.trained_model_file_path, obj=Network_Model)

        # Save the standalone model for deployment
        save_object("final_model/model.pkl", best_model)

        # Return ModelTrainerArtifact
        model_trainer_artifact = ModelTrainerArtifact(
            trained_model_file_path=self.model_trainer_config.trained_model_file_path,
            train_metric_artifact=classification_train_metric,
            test_metric_artifact=classification_test_metric,
        )
        logging.info(f"Model trainer artifact: {model_trainer_artifact}")
        return model_trainer_artifact

    def initiate_model_trainer(self) -> ModelTrainerArtifact:
        try:
            train_file_path = self.data_transformation_artifact.transformed_train_file_path
            test_file_path = self.data_transformation_artifact.transformed_test_file_path

            # Load numpy array data
            train_arr = load_numpy_array_data(train_file_path)
            test_arr = load_numpy_array_data(test_file_path)

            X_train, y_train, X_test, y_test = (
                train_arr[:, :-1],
                train_arr[:, -1],
                test_arr[:, :-1],
                test_arr[:, -1],
            )

            model = self.train_model(X_train, y_train, X_test, y_test)
            return model
        except Exception as e:
            raise WebShieldException(e, sys)
