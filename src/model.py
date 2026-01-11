"""
Machine Learning model training and evaluation using Spark MLlib
"""

import logging
from pyspark.ml.feature import VectorAssembler, StringIndexer, StandardScaler
from pyspark.ml.classification import RandomForestClassifier, DecisionTreeClassifier
from pyspark.ml.regression import RandomForestRegressor
from pyspark.ml.evaluation import MulticlassClassificationEvaluator, RegressionEvaluator
from pyspark.ml import Pipeline

logger = logging.getLogger(__name__)


def prepare_features(df, feature_cols, target_col):
    """
    Prepare features for ML model training
    
    Args:
        df (DataFrame): Input Spark DataFrame
        feature_cols (list): List of feature column names
        target_col (str): Target variable column name
    
    Returns:
        DataFrame: DataFrame with assembled features
    """
    logger.info(f"Preparing features: {len(feature_cols)} columns")
    
    # Assemble features into a vector
    assembler = VectorAssembler(
        inputCols=feature_cols,
        outputCol="features",
        handleInvalid="skip"
    )
    
    df_features = assembler.transform(df)
    
    logger.info("Features prepared successfully")
    
    return df_features


def train_classification_model(train_df, test_df, feature_col="features", label_col="congestion_encoded"):
    """
    Train a Random Forest classification model to predict congestion levels
    
    Args:
        train_df (DataFrame): Training data
        test_df (DataFrame): Test data
        feature_col (str): Feature column name
        label_col (str): Label column name
    
    Returns:
        tuple: (model, predictions, metrics)
    """
    logger.info("Training Random Forest classification model...")
    
    # Create Random Forest classifier
    rf = RandomForestClassifier(
        featuresCol=feature_col,
        labelCol=label_col,
        numTrees=100,
        maxDepth=10,
        seed=42
    )
    
    # Train model
    model = rf.fit(train_df)
    
    # Make predictions
    predictions = model.transform(test_df)
    
    # Evaluate model
    evaluator_accuracy = MulticlassClassificationEvaluator(
        labelCol=label_col,
        predictionCol="prediction",
        metricName="accuracy"
    )
    
    evaluator_f1 = MulticlassClassificationEvaluator(
        labelCol=label_col,
        predictionCol="prediction",
        metricName="f1"
    )
    
    accuracy = evaluator_accuracy.evaluate(predictions)
    f1_score = evaluator_f1.evaluate(predictions)
    
    metrics = {
        'model_type': 'Random Forest Classifier',
        'accuracy': accuracy,
        'f1_score': f1_score,
        'num_trees': 100,
        'max_depth': 10
    }
    
    logger.info(f"Model trained - Accuracy: {accuracy:.4f}, F1: {f1_score:.4f}")
    
    return model, predictions, metrics


def train_regression_model(train_df, test_df, feature_col="features", label_col="delay_minutes"):
    """
    Train a regression model to predict delay minutes
    
    Args:
        train_df (DataFrame): Training data
        test_df (DataFrame): Test data
        feature_col (str): Feature column name
        label_col (str): Label column name
    
    Returns:
        tuple: (model, predictions, metrics)
    """
    logger.info("Training Random Forest regression model...")
    
    # Create Random Forest regressor
    rf = RandomForestRegressor(
        featuresCol=feature_col,
        labelCol=label_col,
        numTrees=100,
        maxDepth=10,
        seed=42
    )
    
    # Train model
    model = rf.fit(train_df)
    
    # Make predictions
    predictions = model.transform(test_df)
    
    # Evaluate model
    evaluator_rmse = RegressionEvaluator(
        labelCol=label_col,
        predictionCol="prediction",
        metricName="rmse"
    )
    
    evaluator_r2 = RegressionEvaluator(
        labelCol=label_col,
        predictionCol="prediction",
        metricName="r2"
    )
    
    rmse = evaluator_rmse.evaluate(predictions)
    r2 = evaluator_r2.evaluate(predictions)
    
    metrics = {
        'model_type': 'Random Forest Regressor',
        'rmse': rmse,
        'r2': r2,
        'num_trees': 100,
        'max_depth': 10
    }
    
    logger.info(f"Model trained - RMSE: {rmse:.4f}, R²: {r2:.4f}")
    
    return model, predictions, metrics


def get_feature_importance(model, feature_cols):
    """
    Extract feature importance from trained model
    
    Args:
        model: Trained Spark ML model
        feature_cols (list): List of feature column names
    
    Returns:
        dict: Feature importance scores
    """
    try:
        importances = model.featureImportances.toArray()
        
        feature_importance = dict(zip(feature_cols, importances))
        
        # Sort by importance
        feature_importance = dict(
            sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        )
        
        logger.info("Feature importance extracted")
        
        return feature_importance
    
    except Exception as e:
        logger.error(f"Failed to extract feature importance: {str(e)}")
        return {}


# Example usage
if __name__ == "__main__":
    from src.spark_session import create_spark_session, stop_spark_session
    
    logging.basicConfig(level=logging.INFO)
    
    logger.info("Model module loaded successfully")
