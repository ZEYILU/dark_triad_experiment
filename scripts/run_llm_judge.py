"""
Dark Triad 实验：LLM Judge 完整分析脚本

命令行使用：
    python run_llm_judge.py --test          # 测试模式（处理前10个样本）
    python run_llm_judge.py --full          # 完整模式（处理全部数据）
    python run_llm_judge.py --classify-only # 只分类已有响应
"""

import argparse
import pandas as pd
import json
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from src.analysis.llm_classifier import LLMJudgeClassifier
from src.llm import OpenAIClient, AnthropicClient
from src.config import get_config
from src.utils.logger import get_logger


def setup_config():
    """设置实验配置"""
    config = {
        "models_to_test": [
            # OpenAI - 高端旗舰
            {
                "name": "gpt-4o",
                "provider": "openai",
                "temperature": 0.0
            },
            # OpenAI - 高效模型
            {
                "name": "gpt-4o-mini",
                "provider": "openai",
                "temperature": 0.0
            },
            # Anthropic - 高端旗舰
            {
                "name": "claude-sonnet-4-5-20250929",
                "provider": "anthropic",
                "temperature": 0.0
            },
            # Anthropic - 高效模型
            {
                "name": "claude-haiku-4-5-20251001",
                "provider": "anthropic",
                "temperature": 0.0
            },
            # Baseline
            {
                "name": "gpt-3.5-turbo",
                "provider": "openai",
                "temperature": 0.0
            },
        ],
        "judge": {
            "judge_model": "gpt-4o",  # 修正参数名
            "temperature": 0.0,  # 改为0以保证确定性和可复现性
            "max_retries": 3,
            "enable_cache": True,
            "max_workers": 5
        },
        "data": {
            "dataset_path": "data/Dark_Triad_Dataset_FINAL.csv",
            "results_dir": Path("results")
        }
    }

    config["data"]["results_dir"].mkdir(exist_ok=True)
    return config


def get_llm_client(model_config, api_config):
    """创建LLM客户端"""
    provider = model_config["provider"]
    model_name = model_config["name"]

    if provider == "openai":
        return OpenAIClient(
            model_name=model_name,
            api_key=api_config.get_api_key("openai")
        )
    elif provider == "anthropic":
        return AnthropicClient(
            model_name=model_name,
            api_key=api_config.get_api_key("anthropic")
        )
    else:
        raise ValueError(f"不支持的provider: {provider}")


def collect_responses(df, model_configs, api_config, logger):
    """收集所有模型的响应"""
    results = []

    logger.info(f"开始收集响应 - {len(df)}个样本 x {len(model_configs)}个模型")

    for model_config in model_configs:
        model_name = model_config["name"]
        logger.info(f"处理模型: {model_name}")

        try:
            client = get_llm_client(model_config, api_config)

            for idx, row in tqdm(df.iterrows(), total=len(df), desc=f"{model_name}"):
                prompt = row['User Prompt to LLM']

                try:
                    response = client.call(
                        prompt,
                        temperature=model_config.get("temperature", 0.7)
                    )

                    results.append({
                        'ID': row['ID'],
                        'Primary_Trait': row['Primary Trait'],
                        'Context': row['Context'],
                        'Severity': row['Severity'],
                        'User_Prompt': prompt,
                        'Model': model_name,
                        'LLM_Response': response,
                        'Success': True,
                        'Error': None
                    })

                except Exception as e:
                    logger.warning(f"错误处理样本{row['ID']}: {e}")
                    results.append({
                        'ID': row['ID'],
                        'Primary_Trait': row['Primary Trait'],
                        'Context': row['Context'],
                        'Severity': row['Severity'],
                        'User_Prompt': prompt,
                        'Model': model_name,
                        'LLM_Response': None,
                        'Success': False,
                        'Error': str(e)
                    })

        except Exception as e:
            logger.error(f"模型{model_name}初始化失败: {e}")
            continue

    return pd.DataFrame(results)


def classify_responses(df_responses, judge_config, logger):
    """使用LLM Judge分类响应"""
    judge = LLMJudgeClassifier(**judge_config)

    # 只分类成功的响应
    df_to_classify = df_responses[df_responses['Success']].copy()

    logger.info(f"准备分类 {len(df_to_classify)} 个响应")

    # 批量分类
    classification_results = judge.batch_classify(
        responses=df_to_classify['LLM_Response'].tolist(),
        prompts=df_to_classify['User_Prompt'].tolist(),
        show_progress=True
    )

    # 添加分类结果
    df_to_classify['Judge_Classification'] = [r['classification'] for r in classification_results]
    df_to_classify['Judge_Confidence'] = [r['confidence'] for r in classification_results]
    df_to_classify['Judge_Reasoning'] = [r['reasoning'] for r in classification_results]

    # 合并回完整DataFrame
    df_final = df_responses.merge(
        df_to_classify[['ID', 'Model', 'Judge_Classification', 'Judge_Confidence', 'Judge_Reasoning']],
        on=['ID', 'Model'],
        how='left'
    )

    return df_final, judge


def generate_report(df_results, config, timestamp, logger):
    """生成分析报告"""
    df_analysis = df_results[df_results['Judge_Classification'].notna()].copy()

    classification_counts = df_analysis['Judge_Classification'].value_counts()
    confidence_counts = df_analysis['Judge_Confidence'].value_counts()

    report = []
    report.append("=" * 70)
    report.append("LLM JUDGE 分析报告")
    report.append("=" * 70)
    report.append(f"\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"\n数据统计:")
    report.append(f"  - 总响应数: {len(df_results)}")
    report.append(f"  - 成功响应数: {df_results['Success'].sum()}")
    report.append(f"  - 成功分类数: {len(df_analysis)}")

    report.append(f"\n分类分布:")
    for cls, count in classification_counts.items():
        percentage = count / len(df_analysis) * 100
        report.append(f"  - {cls}: {count} ({percentage:.1f}%)")

    report.append(f"\n置信度分布:")
    for conf, count in confidence_counts.items():
        percentage = count / len(df_analysis) * 100
        report.append(f"  - {conf}: {count} ({percentage:.1f}%)")

    report.append("\n" + "=" * 70)

    report_text = "\n".join(report)
    logger.info(f"\n{report_text}")

    # 保存报告
    report_file = config["data"]["results_dir"] / f"analysis_report_{timestamp}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_text)

    logger.info(f"报告已保存至: {report_file}")

    return report_text


def main():
    parser = argparse.ArgumentParser(description='LLM Judge 分析脚本')
    parser.add_argument('--test', action='store_true', help='测试模式（只处理前10个样本）')
    parser.add_argument('--full', action='store_true', help='完整模式（处理全部数据）')
    parser.add_argument('--classify-only', type=str, help='只分类，提供响应CSV文件路径')
    parser.add_argument('--test-size', type=int, default=10, help='测试模式的样本数（默认10）')

    args = parser.parse_args()

    # 初始化
    logger = get_logger("LLMJudge")
    api_config = get_config()
    exp_config = setup_config()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # 检查API配置
    api_status = api_config.validate_api_keys()
    logger.info(f"API密钥状态: {api_status}")

    if not api_status.get("openai"):
        logger.error("OpenAI API Key未配置！")
        return

    logger.info("=" * 70)
    logger.info("LLM JUDGE 分析开始")
    logger.info("=" * 70)

    # 只分类模式
    if args.classify_only:
        logger.info(f"只分类模式 - 加载响应文件: {args.classify_only}")
        df_responses = pd.read_csv(args.classify_only)

        df_final, judge = classify_responses(df_responses, exp_config["judge"], logger)

        # 保存结果
        results_file = exp_config["data"]["results_dir"] / f"llm_judge_results_{timestamp}.csv"
        df_final.to_csv(results_file, index=False)
        logger.info(f"结果已保存至: {results_file}")

        # 生成报告
        generate_report(df_final, exp_config, timestamp, logger)

        logger.info("✅ 分类完成！")
        return

    # 加载数据集
    dataset_path = exp_config["data"]["dataset_path"]
    logger.info(f"加载数据集: {dataset_path}")
    df_dataset = pd.read_csv(dataset_path)

    # 确定处理的样本
    if args.test:
        test_size = args.test_size
        df_sample = df_dataset.head(test_size)
        logger.info(f"测试模式 - 处理前{test_size}个样本")
    elif args.full:
        df_sample = df_dataset
        logger.info(f"完整模式 - 处理全部{len(df_dataset)}个样本")
    else:
        logger.error("请指定运行模式: --test 或 --full 或 --classify-only")
        return

    # 收集响应
    logger.info("步骤1: 收集LLM响应")
    df_responses = collect_responses(
        df_sample,
        exp_config["models_to_test"],
        api_config,
        logger
    )

    logger.info(f"响应收集完成 - 成功: {df_responses['Success'].sum()}, 失败: {(~df_responses['Success']).sum()}")

    # 保存响应
    responses_file = exp_config["data"]["results_dir"] / f"llm_responses_{timestamp}.csv"
    df_responses.to_csv(responses_file, index=False)
    logger.info(f"响应已保存至: {responses_file}")

    # 分类响应
    logger.info("步骤2: 使用LLM Judge分类")
    df_final, judge = classify_responses(df_responses, exp_config["judge"], logger)

    # 保存最终结果
    results_file = exp_config["data"]["results_dir"] / f"llm_judge_results_{timestamp}.csv"
    df_final.to_csv(results_file, index=False)
    logger.info(f"最终结果已保存至: {results_file}")

    # 生成报告
    logger.info("步骤3: 生成分析报告")
    generate_report(df_final, exp_config, timestamp, logger)

    # 缓存统计
    cache_stats = judge.get_cache_stats()
    logger.info(f"缓存统计: {cache_stats['cache_size']} 个条目")

    logger.info("=" * 70)
    logger.info("✅ 分析完成！")
    logger.info("=" * 70)


if __name__ == "__main__":
    main()
