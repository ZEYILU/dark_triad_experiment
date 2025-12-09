"""
配置管理模块
统一管理所有配置：API密钥、模型参数、关键词等
"""

import os
import yaml
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv


class Config:
    """配置管理类"""

    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化配置

        Args:
            config_dir: 配置文件目录，默认为项目根目录的configs/
        """
        # 加载环境变量
        load_dotenv()

        # 设置配置目录
        if config_dir is None:
            # 从当前文件位置找到项目根目录
            current_dir = Path(__file__).parent.parent
            self.config_dir = current_dir / "configs"
        else:
            self.config_dir = Path(config_dir)

        # 默认配置
        self._api_keys: Dict[str, str] = {}
        self._models: Dict[str, List[Dict]] = {}
        self._keywords: Dict[str, List[str]] = {}
        self._paths: Dict[str, str] = {}

        # 加载配置
        self._load_env_vars()
        self._load_yaml_configs()
        self._setup_default_paths()

    def _load_env_vars(self):
        """从环境变量加载API密钥"""
        self._api_keys = {
            "openai": os.getenv("OPENAI_API_KEY", ""),
            "anthropic": os.getenv("ANTHROPIC_API_KEY", ""),
        }

    def _load_yaml_configs(self):
        """从YAML文件加载配置"""
        # 加载模型配置
        models_file = self.config_dir / "models.yaml"
        if models_file.exists():
            with open(models_file, 'r', encoding='utf-8') as f:
                self._models = yaml.safe_load(f) or {}

        # 加载关键词配置
        keywords_file = self.config_dir / "keywords.yaml"
        if keywords_file.exists():
            with open(keywords_file, 'r', encoding='utf-8') as f:
                self._keywords = yaml.safe_load(f) or {}

    def _setup_default_paths(self):
        """设置默认路径"""
        root_dir = Path(__file__).parent.parent
        self._paths = {
            "root": str(root_dir),
            "data": str(root_dir / "data"),
            "results": str(root_dir / "results"),
            "figures": str(root_dir / "figures"),
            "dataset": str(root_dir / "data" / "Dark_Triad_Dataset_FINAL.csv"),
        }

    # API Keys
    def get_api_key(self, provider: str) -> Optional[str]:
        """
        获取API密钥

        Args:
            provider: API提供商 ("openai" or "anthropic")

        Returns:
            API密钥，如果未配置则返回None
        """
        key = self._api_keys.get(provider.lower())
        if not key or key.startswith("your-"):
            return None
        return key

    def validate_api_keys(self, providers: Optional[List[str]] = None) -> Dict[str, bool]:
        """
        验证API密钥是否已配置

        Args:
            providers: 要验证的提供商列表，None表示验证所有

        Returns:
            字典，键为提供商名称，值为是否有效
        """
        if providers is None:
            providers = list(self._api_keys.keys())

        return {
            provider: self.get_api_key(provider) is not None
            for provider in providers
        }

    # Models
    def get_models(self, provider: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取模型配置

        Args:
            provider: 提供商名称，None表示获取所有

        Returns:
            模型配置列表
        """
        if provider:
            return self._models.get(provider, [])

        # 返回所有模型
        all_models = []
        for models in self._models.values():
            all_models.extend(models)
        return all_models

    def get_model_config(self, model_name: str) -> Optional[Dict[str, Any]]:
        """
        根据模型名称获取配置

        Args:
            model_name: 模型名称

        Returns:
            模型配置字典，未找到返回None
        """
        for models in self._models.values():
            for model in models:
                if model.get("name") == model_name:
                    return model
        return None

    # Keywords
    def get_keywords(self, category: str) -> List[str]:
        """
        获取分类关键词

        Args:
            category: 类别名称 ("refusal", "corrective", "reinforcing", "neutral")

        Returns:
            关键词列表
        """
        return self._keywords.get(category, [])

    def get_all_keywords(self) -> Dict[str, List[str]]:
        """获取所有关键词"""
        return self._keywords.copy()

    # Paths
    def get_path(self, key: str) -> str:
        """
        获取路径配置

        Args:
            key: 路径键名 ("root", "data", "results", "figures", "dataset")

        Returns:
            路径字符串
        """
        return self._paths.get(key, "")

    def ensure_directories(self):
        """确保所有必需的目录存在"""
        for key in ["data", "results", "figures"]:
            path = Path(self._paths[key])
            path.mkdir(parents=True, exist_ok=True)

    # Export
    def to_dict(self) -> Dict[str, Any]:
        """导出配置为字典"""
        return {
            "api_keys_configured": self.validate_api_keys(),
            "models": self._models,
            "keywords": self._keywords,
            "paths": self._paths,
        }

    def __repr__(self) -> str:
        """字符串表示"""
        api_status = self.validate_api_keys()
        return f"Config(api_keys={api_status}, models={len(self.get_models())} total)"


# 全局配置实例（单例模式）
_global_config: Optional[Config] = None


def get_config(config_dir: Optional[str] = None) -> Config:
    """
    获取全局配置实例

    Args:
        config_dir: 配置目录，仅第一次调用时有效

    Returns:
        Config实例
    """
    global _global_config
    if _global_config is None:
        _global_config = Config(config_dir)
    return _global_config


def reload_config(config_dir: Optional[str] = None) -> Config:
    """
    重新加载配置

    Args:
        config_dir: 配置目录

    Returns:
        新的Config实例
    """
    global _global_config
    _global_config = Config(config_dir)
    return _global_config


class AnnotationAnalysisConfig:
    """
    Configuration manager for annotation analysis
    Loads settings from config/annotation_analysis.yaml
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize annotation analysis configuration

        Args:
            config_path: Path to YAML config file. If None, uses default location.
        """
        if config_path is None:
            root_dir = Path(__file__).parent.parent
            config_path = root_dir / "config" / "annotation_analysis.yaml"

        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please ensure config/annotation_analysis.yaml exists."
            )

        with open(self.config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    # Path methods
    def get_path(self, key: str) -> Path:
        """
        Get path configuration

        Args:
            key: Path key from config (e.g., 'base_dir', 'output_dir')

        Returns:
            Path object
        """
        path_str = self.config['paths'].get(key, '')
        if not path_str:
            raise KeyError(f"Path key '{key}' not found in configuration")

        # Convert relative paths to absolute
        path = Path(path_str)
        if not path.is_absolute():
            root_dir = Path(__file__).parent.parent
            path = root_dir / path

        return path

    def get_pattern(self, key: str) -> str:
        """
        Get file pattern configuration

        Args:
            key: Pattern key (e.g., 'annotator_pattern', 'ground_truth_pattern')

        Returns:
            Pattern string
        """
        return self.config['paths'].get(key, '')

    # Analysis methods
    def get_categories(self) -> List[str]:
        """Get list of classification categories"""
        return self.config['analysis']['categories']

    def get_code_to_label_mapping(self) -> Dict[int, str]:
        """Get mapping from numeric codes to text labels"""
        return self.config['analysis']['code_to_label']

    def interpret_kappa(self, kappa: float) -> str:
        """
        Interpret Fleiss' Kappa value using thresholds

        Args:
            kappa: Kappa value to interpret

        Returns:
            Interpretation string
        """
        thresholds = self.config['analysis']['kappa_thresholds']

        if kappa < thresholds['poor']:
            return "Poor (worse than random)"
        elif kappa < thresholds['slight']:
            return "Slight agreement"
        elif kappa < thresholds['fair']:
            return "Fair agreement"
        elif kappa < thresholds['moderate']:
            return "Moderate agreement"
        elif kappa < thresholds['substantial']:
            return "Substantial agreement"
        else:
            return "Almost perfect agreement"

    # Visualization methods
    def get_viz_config(self, key: Optional[str] = None) -> Any:
        """
        Get visualization configuration

        Args:
            key: Specific config key. If None, returns all viz config.

        Returns:
            Configuration value or entire viz config dict
        """
        if key is None:
            return self.config['visualization']
        return self.config['visualization'].get(key)

    def get_colors(self) -> List[str]:
        """Get color palette for visualizations"""
        return self.config['visualization']['colors']

    def get_figsize(self, chart_type: str = 'figsize') -> tuple:
        """
        Get figure size for charts

        Args:
            chart_type: Type of chart ('figsize', 'confusion_matrix_figsize', etc.)

        Returns:
            Tuple of (width, height)
        """
        size = self.config['visualization'].get(chart_type, [12, 8])
        return tuple(size)

    # Output methods
    def get_output_filename(self, key: str) -> str:
        """
        Get output filename from config

        Args:
            key: Filename key (e.g., 'confusion_matrix_prefix', 'agreement_report')

        Returns:
            Filename string
        """
        return self.config['output'].get(key, '')

    def get_csv_encoding(self) -> str:
        """Get CSV file encoding"""
        return self.config['output'].get('csv_encoding', 'utf-8-sig')

    def ensure_output_dir(self) -> Path:
        """
        Ensure output directory exists

        Returns:
            Path to output directory
        """
        output_dir = self.get_path('output_dir')
        output_dir.mkdir(parents=True, exist_ok=True)
        return output_dir

    def __repr__(self) -> str:
        """String representation"""
        n_categories = len(self.get_categories())
        return f"AnnotationAnalysisConfig(categories={n_categories}, config_path={self.config_path})"
