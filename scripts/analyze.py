"""
重构后的结果分析脚本
使用模块化的分类器
"""

import sys
import os
from pathlib import Path
import pandas as pd
import json
from datetime import datetime
import glob

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_config
from src.analysis import ResponseClassifier
from src.utils.logger import setup_logger


class ResultAnalyzer:
    """结果分析器 - 分析实验结果"""

    def __init__(self):
        """初始化分析器"""
        self.config = get_config()
        self.logger = setup_logger("analyzer", use_colors=True)
        self.classifier = ResponseClassifier()

    def find_result_files(self) -> list:
        """查找所有结果CSV文件"""
        results_dir = self.config.get_path("results")
        pattern = os.path.join(results_dir, "results_*.csv")
        files = glob.glob(pattern)

        # 排除已分析的文件
        files = [f for f in files if "_analyzed.csv" not in f]

        return sorted(files, key=os.path.getmtime, reverse=True)

    def analyze_file(self, csv_path: str) -> pd.DataFrame:
        """
        分析单个结果文件

        Args:
            csv_path: CSV文件路径

        Returns:
            添加了分析列的DataFrame
        """
        self.logger.info(f"分析文件: {os.path.basename(csv_path)}")

        df = pd.read_csv(csv_path)
        self.logger.info(f"  共{len(df)}条响应")

        # 添加分析列
        classifications = []
        corrective_scores = []
        reinforcing_scores = []
        confidences = []
        word_counts = []

        for idx, row in df.iterrows():
            response = row.get('LLM Response', '')

            # 分类
            result = self.classifier.classify(response)
            classifications.append(result['classification'])
            corrective_scores.append(result['corrective_score'])
            reinforcing_scores.append(result['reinforcing_score'])
            confidences.append(result['confidence'])

            # 长度分析
            length = self.classifier.analyze_length(response)
            word_counts.append(length['words'])

        # 添加新列
        df['Response_Classification'] = classifications
        df['Corrective_Score'] = corrective_scores
        df['Reinforcing_Score'] = reinforcing_scores
        df['Classification_Confidence'] = confidences
        df['Word_Count'] = word_counts

        self.logger.info("  分析完成")
        return df

    def generate_summary(self, df: pd.DataFrame, model_name: str) -> dict:
        """
        生成统计摘要

        Args:
            df: 分析后的DataFrame
            model_name: 模型名称

        Returns:
            摘要字典
        """
        summary = {
            "model": model_name,
            "total_responses": len(df),
            "successful_responses": df['Success'].sum() if 'Success' in df.columns else len(df),
        }

        # 分类分布
        if 'Response_Classification' in df.columns:
            class_counts = df['Response_Classification'].value_counts().to_dict()
            summary['classification_distribution'] = class_counts
            summary['classification_percentages'] = {
                k: round(v / len(df) * 100, 1) for k, v in class_counts.items()
            }

        # 按严重程度统计
        if 'Severity' in df.columns and 'Response_Classification' in df.columns:
            severity_stats = {}
            for severity in ['LOW', 'MEDIUM', 'HIGH']:
                subset = df[df['Severity'] == severity]
                if len(subset) > 0:
                    severity_stats[severity] = {
                        "count": len(subset),
                        "corrective_pct": round((subset['Response_Classification'] == 'CORRECTIVE').sum() / len(subset) * 100, 1),
                        "reinforcing_pct": round((subset['Response_Classification'] == 'REINFORCING').sum() / len(subset) * 100, 1),
                    }
            summary['by_severity'] = severity_stats

        # 按特质统计
        if 'Primary Trait' in df.columns and 'Response_Classification' in df.columns:
            trait_stats = {}
            for trait in df['Primary Trait'].unique():
                subset = df[df['Primary Trait'] == trait]
                if len(subset) > 0:
                    trait_stats[trait] = {
                        "count": len(subset),
                        "corrective_pct": round((subset['Response_Classification'] == 'CORRECTIVE').sum() / len(subset) * 100, 1),
                    }
            summary['by_trait'] = trait_stats

        # 响应长度统计
        if 'Word_Count' in df.columns:
            summary['response_length'] = {
                "mean_words": round(df['Word_Count'].mean(), 1),
                "median_words": round(df['Word_Count'].median(), 1),
                "min_words": int(df['Word_Count'].min()),
                "max_words": int(df['Word_Count'].max()),
            }

        return summary

    def run(self):
        """运行分析"""
        self.logger.info("="*70)
        self.logger.info("结果分析工具 v2.0")
        self.logger.info("="*70)

        # 查找结果文件
        csv_files = self.find_result_files()

        if not csv_files:
            self.logger.error("未找到结果文件")
            self.logger.info("请先运行实验: python scripts/run_experiment.py")
            return False

        self.logger.info(f"\n找到{len(csv_files)}个结果文件:")
        for i, f in enumerate(csv_files, 1):
            size = os.path.getsize(f) / 1024
            self.logger.info(f"  {i}. {os.path.basename(f)} ({size:.1f} KB)")

        # 分析所有文件
        all_summaries = []
        results_dir = self.config.get_path("results")

        for csv_file in csv_files:
            # 提取模型名称
            basename = os.path.basename(csv_file)
            model_name = basename.replace("results_", "").split("_202")[0]

            # 分析
            df_analyzed = self.analyze_file(csv_file)

            # 保存分析结果
            output_path = csv_file.replace(".csv", "_analyzed.csv")
            df_analyzed.to_csv(output_path, index=False, encoding='utf-8-sig')
            self.logger.info(f"  已保存: {os.path.basename(output_path)}")

            # 生成摘要
            summary = self.generate_summary(df_analyzed, model_name)
            all_summaries.append(summary)

        # 保存汇总报告
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(results_dir, f"analysis_report_{timestamp}.json")

        report = {
            "timestamp": timestamp,
            "analyzed_files": len(csv_files),
            "summaries": all_summaries
        }

        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        self.logger.info(f"\n汇总报告已保存: {os.path.basename(report_path)}")

        # 打印摘要
        self._print_summaries(all_summaries)

        self.logger.info("\n下一步:")
        self.logger.info("1. 查看详细结果: results/*_analyzed.csv")
        self.logger.info("2. 生成可视化: python visualize_results.py")

        return True

    def _print_summaries(self, summaries: list):
        """打印摘要"""
        self.logger.info("\n" + "="*70)
        self.logger.info("分析摘要")
        self.logger.info("="*70)

        for summary in summaries:
            self.logger.info(f"\n模型: {summary['model']}")
            self.logger.info(f"  总响应数: {summary['total_responses']}")

            if 'classification_percentages' in summary:
                self.logger.info("  响应分类:")
                for cls, pct in summary['classification_percentages'].items():
                    self.logger.info(f"    {cls}: {pct}%")

            if 'response_length' in summary:
                self.logger.info(f"  平均长度: {summary['response_length']['mean_words']} 词")

        self.logger.info("="*70)


def main():
    """主函数"""
    analyzer = ResultAnalyzer()
    success = analyzer.run()

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
