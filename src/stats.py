"""
Statistical analysis module - Inferential and Bayesian statistics
"""

import logging
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import chi2_contingency, f_oneway, ttest_ind

logger = logging.getLogger(__name__)


def hypothesis_test_congestion_by_route(df, route_col='route_id', congestion_col='congestion_encoded'):
    """
    Test if congestion levels differ significantly across routes using ANOVA
    
    Args:
        df (pd.DataFrame): Pandas DataFrame
        route_col (str): Route identifier column
        congestion_col (str): Congestion level column
    
    Returns:
        dict: Test results including F-statistic and p-value
    """
    logger.info("Performing ANOVA test for congestion across routes")
    
    # Group data by route
    groups = [group[congestion_col].values for name, group in df.groupby(route_col)]
    
    # Perform one-way ANOVA
    f_stat, p_value = f_oneway(*groups)
    
    result = {
        'test': 'One-way ANOVA',
        'hypothesis': 'Congestion levels differ across routes',
        'f_statistic': f_stat,
        'p_value': p_value,
        'significant': p_value < 0.05,
        'interpretation': 'Reject null hypothesis' if p_value < 0.05 else 'Fail to reject null hypothesis'
    }
    
    logger.info(f"ANOVA Results: F={f_stat:.4f}, p={p_value:.4f}")
    
    return result


def hypothesis_test_peak_vs_offpeak(df, peak_col='is_peak_hour', congestion_col='congestion_encoded'):
    """
    Test if congestion differs between peak and off-peak hours using t-test
    
    Args:
        df (pd.DataFrame): Pandas DataFrame
        peak_col (str): Peak hour indicator column
        congestion_col (str): Congestion level column
    
    Returns:
        dict: Test results
    """
    logger.info("Performing t-test for peak vs off-peak congestion")
    
    peak_data = df[df[peak_col] == 1][congestion_col]
    offpeak_data = df[df[peak_col] == 0][congestion_col]
    
    t_stat, p_value = ttest_ind(peak_data, offpeak_data)
    
    result = {
        'test': 'Independent t-test',
        'hypothesis': 'Congestion differs between peak and off-peak hours',
        't_statistic': t_stat,
        'p_value': p_value,
        'peak_mean': peak_data.mean(),
        'offpeak_mean': offpeak_data.mean(),
        'significant': p_value < 0.05,
        'interpretation': 'Reject null hypothesis' if p_value < 0.05 else 'Fail to reject null hypothesis'
    }
    
    logger.info(f"T-test Results: t={t_stat:.4f}, p={p_value:.4f}")
    
    return result


def correlation_analysis(df, features):
    """
    Compute correlation matrix for specified features
    
    Args:
        df (pd.DataFrame): Pandas DataFrame
        features (list): List of feature columns
    
    Returns:
        pd.DataFrame: Correlation matrix
    """
    logger.info(f"Computing correlation matrix for {len(features)} features")
    
    corr_matrix = df[features].corr()
    
    logger.info("Correlation analysis completed")
    
    return corr_matrix


def chi_square_test(df, col1, col2):
    """
    Perform chi-square test of independence between two categorical variables
    
    Args:
        df (pd.DataFrame): Pandas DataFrame
        col1 (str): First categorical column
        col2 (str): Second categorical column
    
    Returns:
        dict: Test results
    """
    logger.info(f"Performing chi-square test: {col1} vs {col2}")
    
    # Create contingency table
    contingency_table = pd.crosstab(df[col1], df[col2])
    
    # Perform chi-square test
    chi2, p_value, dof, expected = chi2_contingency(contingency_table)
    
    result = {
        'test': 'Chi-square test of independence',
        'variables': f"{col1} vs {col2}",
        'chi2_statistic': chi2,
        'p_value': p_value,
        'degrees_of_freedom': dof,
        'significant': p_value < 0.05,
        'interpretation': 'Variables are dependent' if p_value < 0.05 else 'Variables are independent'
    }
    
    logger.info(f"Chi-square Results: χ²={chi2:.4f}, p={p_value:.4f}")
    
    return result


def bayesian_estimation_placeholder(df, target_col):
    """
    Placeholder for Bayesian estimation using PyMC
    This will be implemented in the notebook with proper PyMC models
    
    Args:
        df (pd.DataFrame): Pandas DataFrame
        target_col (str): Target variable for Bayesian estimation
    
    Returns:
        dict: Placeholder results
    """
    logger.info("Bayesian estimation will be implemented in notebook 04")
    
    return {
        'method': 'Bayesian Estimation',
        'note': 'To be implemented with PyMC in notebook',
        'target': target_col
    }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Create sample data for testing
    np.random.seed(42)
    sample_df = pd.DataFrame({
        'route_id': np.random.choice(['R1', 'R2', 'R3'], 1000),
        'congestion_encoded': np.random.randint(0, 3, 1000),
        'is_peak_hour': np.random.randint(0, 2, 1000),
        'average_speed': np.random.uniform(10, 60, 1000),
        'service_reliability_index': np.random.uniform(0, 1, 1000)
    })
    
    # Run tests
    anova_result = hypothesis_test_congestion_by_route(sample_df)
    print(anova_result)
    
    ttest_result = hypothesis_test_peak_vs_offpeak(sample_df)
    print(ttest_result)
