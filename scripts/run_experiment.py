"""
重构后的实验运行脚本
使用面向对象的模块化架构
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json
import pandas as pd

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_config
from src.llm import OpenAIClient, AnthropicClient
from src.data import DatasetLoader
from src.utils.logger import setup_logger


class ExperimentRunner:
    """实验运行器 - 管理整个实验流程"""

    def __init__(self, test_mode: bool = False):
        """
        初始化实验运行器

        Args:
            test_mode: 测试模式（只测试前5个prompts）
        """
        self.config = get_config()
        self.logger = setup_logger("experiment", use_colors=True)
        self.test_mode = test_mode
        self.results = []

    def run(self, model_configs: list):
        """
        运行实验

        Args:
            model_configs: 模型配置列表
                          每个元素是字典: {"type": "openai|anthropic", "name": "model-name"}
        """
        self.logger.info(f"开始实验 - {len(model_configs)}个模型")
        self.logger.info(f"测试模式: {'是' if self.test_mode else '否'}")

        # 确保目录存在
        self.config.ensure_directories()

        # 加载数据集
        dataset_path = self.config.get_path("dataset")
        loader = DatasetLoader(dataset_path)

        try:
            limit = 5 if self.test_mode else None
            loader.load(limit=limit)
        except Exception as e:
            self.logger.error(f"加载数据集失败: {e}")
            return False

        # 测试每个模型
        for i, model_config in enumerate(model_configs, 1):
            self.logger.info(f"\n{'='*70}")
            self.logger.info(f"测试模型 {i}/{len(model_configs)}: {model_config['name']}")
            self.logger.info(f"{'='*70}")

            success = self._test_model(model_config, loader)

            if success:
                self.logger.info(f"模型 {model_config['name']} 测试完成")
            else:
                self.logger.error(f"模型 {model_config['name']} 测试失败")

        self.logger.info(f"\n{'='*70}")
        self.logger.info("实验完成!")
        self.logger.info(f"{'='*70}")

        return True

    def _test_model(self, model_config: dict, loader: DatasetLoader) -> bool:
        """
        测试单个模型

        Args:
            model_config: 模型配置
            loader: 数据加载器

        Returns:
            是否成功
        """
        model_type = model_config["type"]
        model_name = model_config["name"]

        # 获取API密钥
        api_key = self.config.get_api_key(model_type)
        if not api_key:
            self.logger.error(f"未配置{model_type}的API密钥")
            return False

        # 创建LLM客户端
        try:
            if model_type == "openai":
                client = OpenAIClient(
                    model_name=model_name,
                    api_key=api_key,
                    temperature=0.7,
                    max_tokens=1000
                )
            elif model_type == "anthropic":
                client = AnthropicClient(
                    model_name=model_name,
                    api_key=api_key,
                    temperature=0.7,
                    max_tokens=1000
                )
            else:
                self.logger.error(f"未知的模型类型: {model_type}")
                return False

        except Exception as e:
            self.logger.error(f"创建客户端失败: {e}")
            return False

        # 测试所有prompts
        model_results = []
        total = len(loader)

        for idx in range(total):
            metadata = loader.get_metadata(idx)
            prompt = metadata['User Prompt']

            self.logger.info(f"[{idx+1}/{total}] 测试 prompt: {metadata['ID']}")

            # 调用LLM
            response = client.call(prompt)

            # 记录结果
            result = {
                'ID': metadata['ID'],
                'Primary Trait': metadata['Primary Trait'],
                'Context': metadata['Context'],
                'Severity': metadata['Severity'],
                'User Prompt': prompt,
                'LLM Response': response if response else "ERROR: No response",
                'Model': model_name,
                'Timestamp': datetime.now().isoformat(),
                'Success': response is not None
            }

            model_results.append(result)

            # 显示响应预览
            if response:
                preview = response[:100] + "..." if len(response) > 100 else response
                self.logger.info(f"响应: {preview}\n")

        # 保存结果
        return self._save_results(model_name, model_results)

    def _save_results(self, model_name: str, results: list) -> bool:
        """
        保存测试结果

        Args:
            model_name: 模型名称
            results: 结果列表

        Returns:
            是否成功
        """
        if not results:
            self.logger.error("没有结果可保存")
            return False

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = self.config.get_path("results")

        # 保存CSV
        csv_filename = f"{results_dir}/results_{model_name.replace('/', '_')}_{timestamp}.csv"
        df = pd.DataFrame(results)
        df.to_csv(csv_filename, index=False, encoding='utf-8-sig')
        self.logger.info(f"CSV已保存: {csv_filename}")

        # 保存JSON
        json_filename = f"{results_dir}/results_{model_name.replace('/', '_')}_{timestamp}.json"
        output_data = {
            "metadata": {
                "model": model_name,
                "total_prompts": len(results),
                "successful": sum(1 for r in results if r['Success']),
                "failed": sum(1 for r in results if not r['Success']),
                "timestamp": timestamp,
            },
            "results": results
        }

        with open(json_filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"JSON已保存: {json_filename}")

        # 打印统计
        self._print_statistics(results)

        return True

    def _print_statistics(self, results: list):
        """打印统计信息"""
        df = pd.DataFrame(results)

        self.logger.info(f"\n{'='*60}")
        self.logger.info("统计信息")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"成功: {df['Success'].sum()}")
        self.logger.info(f"失败: {(~df['Success']).sum()}")
        self.logger.info(f"\n按特质:")
        for trait, count in df['Primary Trait'].value_counts().items():
            self.logger.info(f"  {trait}: {count}")
        self.logger.info(f"{'='*60}")


def main():
    """主函数"""
    print("="*70)
    print("🧪 Dark Triad Experiment - 重构版本 v2.0")
    print("="*70)

    # 获取配置
    config = get_config()

    # 验证API密钥
    print("\n检查API密钥...")
    api_status = config.validate_api_keys()
    for provider, valid in api_status.items():
        status = "✅" if valid else "❌"
        print(f"  {status} {provider.upper()}")

    if not any(api_status.values()):
        print("\n❌ 未配置任何API密钥")
        print("请在.env文件中配置API密钥")
        sys.exit(1)

    # 选择测试模式
    print("\n" + "="*70)
    print("选择测试模式:")
    print("1. 快速测试 (GPT-3.5-Turbo)")
    print("2. 标准测试 (GPT-4 + Claude Haiku)")
    print("3. 完整测试 (GPT-4 + GPT-3.5 + Claude Haiku)")
    print("4. 测试模式 (只测试前5个prompts)")
    print("="*70)

    choice = input("\n选择 (1-4): ").strip()

    model_configs = []
    test_mode = False

    if choice == "1":
        model_configs = [
            {"type": "openai", "name": "gpt-3.5-turbo"}
        ]
    elif choice == "2":
        model_configs = [
            {"type": "openai", "name": "gpt-4"},
            {"type": "anthropic", "name": "claude-3-haiku-20240307"}
        ]
    elif choice == "3":
        model_configs = [
            {"type": "openai", "name": "gpt-4"},
            {"type": "openai", "name": "gpt-3.5-turbo"},
            {"type": "anthropic", "name": "claude-3-haiku-20240307"}
        ]
    elif choice == "4":
        print("\n⚠️ 测试模式：只测试前5个prompts")
        test_mode = True
        model_configs = [
            {"type": "openai", "name": "gpt-3.5-turbo"}
        ]
    else:
        print("❌ 无效选择")
        sys.exit(1)

    # 显示配置
    print(f"\n将测试 {len(model_configs)} 个模型:")
    for i, cfg in enumerate(model_configs, 1):
        print(f"  {i}. {cfg['name']} ({cfg['type']})")

    # 确认
    confirm = input("\n确认开始? (y/n): ").strip().lower()
    if confirm != 'y':
        print("已取消")
        sys.exit(0)

    # 运行实验
    runner = ExperimentRunner(test_mode=test_mode)
    success = runner.run(model_configs)

    if success:
        print("\n下一步:")
        print("1. 分析结果: python scripts/analyze.py")
        print("2. 可视化: python visualize_results.py")
    else:
        print("\n实验出错，请检查日志")
        sys.exit(1)


if __name__ == "__main__":
    main()
