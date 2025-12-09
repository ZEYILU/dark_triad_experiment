"""
Annotation Data Loader
Loads and preprocesses annotation data from multiple annotators
"""

import pandas as pd
import numpy as np
import glob
import re
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from ..utils.logger import get_logger


@dataclass
class AnnotationDataset:
    """Container for annotation data"""
    ground_truth: pd.DataFrame
    annotators: Dict[str, pd.DataFrame]
    merged: pd.DataFrame

    @property
    def annotator_names(self) -> List[str]:
        """Get list of annotator names"""
        return list(self.annotators.keys())

    @property
    def n_samples(self) -> int:
        """Get number of samples"""
        return len(self.merged)

    @property
    def n_annotators(self) -> int:
        """Get number of annotators"""
        return len(self.annotators)


class AnnotationDataLoader:
    """Load and merge annotation data from multiple sources"""

    # Code to label mapping (supports both int and string codes)
    CODE_TO_LABEL = {
        1: 'REFUSAL',
        2: 'REINFORCING',
        3: 'CORRECTIVE',
        4: 'MIXED',
        '1': 'REFUSAL',
        '2': 'REINFORCING',
        '3': 'CORRECTIVE',
        '4': 'MIXED'
    }

    def __init__(self, base_dir: Optional[Path] = None):
        """
        Initialize data loader

        Args:
            base_dir: Base directory for data files. If None, uses current directory.
        """
        self.base_dir = Path(base_dir) if base_dir else Path('.')
        self.logger = get_logger(__name__)

    def _convert_codes_to_labels(
        self,
        df: pd.DataFrame,
        column: str = 'Human_Classification'
    ) -> pd.DataFrame:
        """
        Convert numeric codes to text labels

        Args:
            df: DataFrame containing the column to convert
            column: Name of column to convert

        Returns:
            DataFrame with converted labels
        """
        df = df.copy()

        # Check if column exists
        if column not in df.columns:
            self.logger.warning(f"Column '{column}' not found in dataframe")
            return df

        # Check if conversion is needed
        df_valid = df[df[column].notna()].copy()
        if len(df_valid) == 0:
            return df

        first_value = df_valid[column].iloc[0]

        # Check if values are numeric or numeric strings
        is_numeric = isinstance(first_value, (int, float, np.integer, np.floating)) or \
                    (isinstance(first_value, str) and str(first_value).isdigit())

        if is_numeric:
            self.logger.info(f"Converting numeric codes to text labels in column '{column}'")
            df[column] = df[column].map(
                lambda x: self.CODE_TO_LABEL.get(x, x) if pd.notna(x) else x
            )
            self.logger.info("Conversion completed")

        return df

    def _fix_annotation_id_column(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Fix missing or unnamed Annotation_ID column

        Args:
            df: DataFrame to fix

        Returns:
            DataFrame with fixed Annotation_ID column
        """
        # If the first column is empty or unnamed, rename it to Annotation_ID
        if df.columns[0] == '' or 'Unnamed' in df.columns[0]:
            df = df.rename(columns={df.columns[0]: 'Annotation_ID'})
            self.logger.info("Fixed missing Annotation_ID column name")

        return df

    def _extract_annotator_name(self, filename: str) -> str:
        """
        Extract annotator name from filename

        Args:
            filename: Name of annotator file

        Returns:
            Annotator name (e.g., 'Annotator1')
        """
        match = re.search(r'annotator(\d+)', filename.lower())
        if match:
            annotator_num = match.group(1)
            return f'Annotator{annotator_num}'

        # Fallback: use filename without extension
        return Path(filename).stem

    def load_single_annotator(
        self,
        file_path: Path,
        annotator_name: str
    ) -> pd.DataFrame:
        """
        Load data from a single annotator

        Args:
            file_path: Path to annotator file
            annotator_name: Name of annotator

        Returns:
            DataFrame with annotator's annotations
        """
        self.logger.info(f"Loading annotations from {annotator_name}...")

        # Read CSV
        df = pd.read_csv(file_path)

        # Fix Annotation_ID column if needed
        df = self._fix_annotation_id_column(df)

        # Convert codes to labels (before renaming)
        df = self._convert_codes_to_labels(df, column='Human_Classification')

        # Rename columns to distinguish annotators
        rename_dict = {
            'Human_Classification': f'{annotator_name}_Classification',
            'Notes': f'{annotator_name}_Notes'
        }

        # Only rename Confidence column if it exists
        if 'Confidence' in df.columns:
            rename_dict['Confidence'] = f'{annotator_name}_Confidence'

        df = df.rename(columns=rename_dict)

        # Log statistics
        completed = df[f'{annotator_name}_Classification'].notna().sum()
        completion_rate = (completed / len(df) * 100) if len(df) > 0 else 0

        self.logger.info(f"  Samples: {len(df)}")
        self.logger.info(f"  Completed: {completed}/{len(df)} ({completion_rate:.1f}%)")

        # Keep only necessary columns
        keep_cols = ['Annotation_ID', f'{annotator_name}_Classification']

        # Dynamically add existing columns
        if f'{annotator_name}_Confidence' in df.columns:
            keep_cols.append(f'{annotator_name}_Confidence')
        if f'{annotator_name}_Notes' in df.columns:
            keep_cols.append(f'{annotator_name}_Notes')

        df = df[keep_cols]

        return df

    def load_ground_truth(self, pattern: str) -> pd.DataFrame:
        """
        Load ground truth data

        Args:
            pattern: Glob pattern for ground truth file

        Returns:
            DataFrame with ground truth labels

        Raises:
            FileNotFoundError: If no ground truth file found
        """
        self.logger.info("Loading Ground Truth...")

        # Find matching files
        files = list(self.base_dir.glob(pattern))

        if not files:
            raise FileNotFoundError(
                f"No ground truth file found matching pattern: {pattern}"
            )

        # Use the first file found
        file_path = files[0]
        self.logger.info(f"  Using file: {file_path.name}")

        # Read CSV
        df = pd.read_csv(file_path)
        self.logger.info(f"  Samples: {len(df)}")

        # Convert LLM classification codes if needed
        if 'LLM_Judge_Classification' in df.columns:
            df = self._convert_codes_to_labels(df, column='LLM_Judge_Classification')
        elif 'Response_Classification' in df.columns:
            df = self._convert_codes_to_labels(df, column='Response_Classification')

        return df

    def load_annotators(self, pattern: str) -> Dict[str, pd.DataFrame]:
        """
        Load all annotator files matching pattern

        Args:
            pattern: Glob pattern for annotator files

        Returns:
            Dictionary mapping annotator names to DataFrames

        Raises:
            FileNotFoundError: If no annotator files found
        """
        self.logger.info("Loading annotator files...")

        # Find matching files
        files = sorted(self.base_dir.glob(pattern))

        if not files:
            raise FileNotFoundError(
                f"No annotator files found matching pattern: {pattern}"
            )

        self.logger.info(f"Found {len(files)} annotator file(s):")
        for file_path in files:
            self.logger.info(f"  - {file_path.name}")

        # Load each annotator
        annotators = {}
        for file_path in files:
            annotator_name = self._extract_annotator_name(file_path.name)
            df = self.load_single_annotator(file_path, annotator_name)
            annotators[annotator_name] = df

        self.logger.info(f"Loaded {len(annotators)} annotator(s)")

        return annotators

    def load_all(
        self,
        gt_pattern: str,
        annotator_pattern: str,
        gt_fallback: Optional[str] = None
    ) -> AnnotationDataset:
        """
        Load and merge all annotation data

        Args:
            gt_pattern: Glob pattern for ground truth file
            annotator_pattern: Glob pattern for annotator files
            gt_fallback: Fallback pattern for ground truth file if first pattern fails

        Returns:
            AnnotationDataset containing all loaded data

        Raises:
            FileNotFoundError: If required files not found
        """
        # Load ground truth
        try:
            gt_df = self.load_ground_truth(gt_pattern)
        except FileNotFoundError:
            if gt_fallback:
                self.logger.warning(f"Primary pattern failed, trying fallback: {gt_fallback}")
                gt_df = self.load_ground_truth(gt_fallback)
            else:
                raise

        # Load annotators
        annotator_dfs = self.load_annotators(annotator_pattern)

        # Merge all data
        self.logger.info("Merging data...")
        merged_df = gt_df.copy()

        for name, df in annotator_dfs.items():
            merged_df = merged_df.merge(df, on='Annotation_ID', how='left')

        self.logger.info(f"Merged dataset: {len(merged_df)} samples")

        # Create dataset object
        dataset = AnnotationDataset(
            ground_truth=gt_df,
            annotators=annotator_dfs,
            merged=merged_df
        )

        return dataset

    def get_llm_column_name(self, df: pd.DataFrame) -> str:
        """
        Automatically detect LLM classification column name

        Args:
            df: DataFrame to search

        Returns:
            Name of LLM classification column

        Raises:
            ValueError: If no LLM classification column found
        """
        possible_names = ['LLM_Judge_Classification', 'Response_Classification']

        for col_name in possible_names:
            if col_name in df.columns:
                self.logger.info(f"Using LLM classification column: {col_name}")
                return col_name

        raise ValueError(
            f"No LLM classification column found. "
            f"Expected one of: {possible_names}. "
            f"Available columns: {list(df.columns)}"
        )
