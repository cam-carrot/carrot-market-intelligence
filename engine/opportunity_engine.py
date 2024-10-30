import logging
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from typing import Tuple, List, Dict

from config.constants import MARKET_TAGS

logger = logging.getLogger(__name__)

class OpportunityEngine:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_opportunity_score(self, df: pd.DataFrame, target_city_state: str) -> Tuple[pd.DataFrame, List[str]]:
        """
        Calculate opportunity scores for markets based on various metrics.
        
        Args:
            df: DataFrame containing market data
            target_city_state: The target market for comparison
            
        Returns:
            Tuple containing:
            - DataFrame with opportunity scores and categories added
            - List of standardized GA4 column names
        """
        self.logger.info(f"Calculating opportunity score. DataFrame shape: {df.shape}")
        self.logger.info(f"Columns in DataFrame: {df.columns.tolist()}")
        
        # Validate required columns
        required_columns = ['unique_sites', 'housing_units', 'users_org', 'users_paid']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            self.logger.warning(f"Missing columns: {missing_columns}")
            for col in missing_columns:
                df[col] = 1  # Default value
        
        # Calculate GA4 metrics
        ga4_metrics = self._calculate_ga4_metrics(df, target_city_state)
        df = df.join(ga4_metrics)
        
        # Calculate market metrics
        market_metrics = self._calculate_market_metrics(df)
        df = df.join(market_metrics)
        
        # Calculate final scores
        df = self._calculate_final_scores(df)
        
        # Now assign tags
        df['tags'] = df.apply(self._assign_tags, axis=1)
        
        self.logger.info("Opportunity score calculation and tag assignment completed successfully")
        return df, [col for col in df.columns if col.startswith('std_')]

    def _calculate_ga4_metrics(self, df: pd.DataFrame, target_city_state: str) -> pd.DataFrame:
        """Calculate standardized GA4 metrics and performance difference."""
        ga4_columns = ['users_org', 'cvr_org', 'leads_org', 'users_paid', 'cvr_paid', 'leads_paid']
        scaler = StandardScaler()
        
        # Create standardized metrics
        metrics_df = pd.DataFrame(index=df.index)
        std_ga4_columns = [f'std_{col}' for col in ga4_columns]
        metrics_df[std_ga4_columns] = scaler.fit_transform(df[ga4_columns].fillna(df[ga4_columns].mean()))
        
        # Calculate performance difference
        avg_performance = metrics_df[metrics_df.index != target_city_state][std_ga4_columns].mean()
        metrics_df['performance_diff'] = (metrics_df[std_ga4_columns] - avg_performance).mean(axis=1)
        
        return metrics_df

    def _calculate_market_metrics(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate various market metrics used in opportunity score."""
        metrics_df = pd.DataFrame(index=df.index)
        
        # Network penetration
        metrics_df['network_penetration'] = (df['unique_sites'] / df['housing_units']) * 100
        metrics_df['avg_network_penetration'] = metrics_df['network_penetration'].mean()
        
        # Engagement diversity
        total_users = df['users_org'] + df['users_paid'] + 1  # Add 1 to avoid division by zero
        metrics_df['engagement_diversity'] = df['unique_sites'] / total_users
        
        # Growth potential
        avg_penetration = metrics_df['network_penetration'].mean()
        metrics_df['growth_potential'] = (avg_penetration - metrics_df['network_penetration']) / avg_penetration
        
        # Performance efficiency
        total_leads = df['leads_org'] + df['leads_paid']
        metrics_df['performance_efficiency'] = total_leads / (df['unique_sites'] + 1)
        
        # Saturation risk
        metrics_df['log_unique_sites'] = np.log1p(df['unique_sites'])
        metrics_df['log_housing_units'] = np.log1p(df['housing_units'])
        metrics_df['saturation_risk'] = 1 - (1 / (1 + np.exp(-(metrics_df['log_unique_sites'] - metrics_df['log_housing_units']))))
        
        return metrics_df

    def _calculate_final_scores(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate final opportunity scores and categories."""
        # Normalize similarity score if it exists
        if 'similarity_score' in df.columns:
            if df['similarity_score'].isna().all():
                df['norm_similarity'] = 1
            else:
                df['norm_similarity'] = 1 - (
                    (df['similarity_score'] - df['similarity_score'].min()) / 
                    (df['similarity_score'].max() - df['similarity_score'].min())
                )
        else:
            df['norm_similarity'] = 1
        
        # Calculate raw opportunity score
        df['raw_opportunity_score'] = (
            0.3 * df['norm_similarity'] +
            0.2 * (1 - df['performance_diff']) +
            0.1 * df['network_penetration'] +
            0.1 * df['engagement_diversity'] +
            0.1 * df['growth_potential'] +
            0.1 * df['performance_efficiency'] +
            0.1 * (1 - df['saturation_risk'])
        )
        
        # Apply market size adjustment
        df['normalized_log_housing'] = (df['log_housing_units'] - df['log_housing_units'].min()) / (
            df['log_housing_units'].max() - df['log_housing_units'].min()
        )
        
        # Calculate final opportunity score
        df['opportunity_score'] = df['raw_opportunity_score'] * (1 + df['normalized_log_housing'])
        
        # Normalize final score
        min_score = df['opportunity_score'].min()
        max_score = df['opportunity_score'].max()
        if min_score != max_score:
            df['opportunity_score'] = (df['opportunity_score'] - min_score) / (max_score - min_score)
        else:
            self.logger.warning("All opportunity scores are the same. Setting to a constant value.")
            df['opportunity_score'] = 1
        
        # Categorize scores
        df['opportunity_category'] = pd.qcut(
            df['opportunity_score'], 
            q=3, 
            labels=['Low', 'Average', 'High'],
            duplicates='drop'
        )
        
        return df

    def _assign_tags(self, row: pd.Series) -> List[str]:
        """Assign market tags based on metrics."""
        return [tag for tag, data in MARKET_TAGS.items() if data['condition'](row)]