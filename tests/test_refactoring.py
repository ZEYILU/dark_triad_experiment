"""
测试重构后的代码
验证所有模块可以正常导入和使用
"""

import sys
import os
from pathlib import Path

# 设置UTF-8编码（Windows兼容）
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加src目录到路径
sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("测试重构后的代码")
print("="*70)

# 测试1: 导入配置模块
print("\n1. 测试配置模块...")
try:
    from src.config import get_config
    config = get_config()
    print(f"   ✅ 配置模块导入成功")
    print(f"   配置: {config}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 测试2: 导入LLM模块
print("\n2. 测试LLM模块...")
try:
    from src.llm import BaseLLMClient, OpenAIClient, AnthropicClient
    print(f"   ✅ LLM模块导入成功")
    print(f"   - BaseLLMClient: {BaseLLMClient}")
    print(f"   - OpenAIClient: {OpenAIClient}")
    print(f"   - AnthropicClient: {AnthropicClient}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 测试3: 导入分析模块
print("\n3. 测试分析模块...")
try:
    from src.analysis import ResponseClassifier
    classifier = ResponseClassifier()
    print(f"   ✅ 分析模块导入成功")
    print(f"   分类器: {classifier}")

    # 测试分类
    test_response = "I can't assist with that request."
    result = classifier.classify(test_response)
    print(f"   测试分类: {result['classification']} (置信度: {result['confidence']})")
except Exception as e:
    print(f"   ❌ 错误: {e}")
    import traceback
    traceback.print_exc()

# 测试4: 导入数据模块
print("\n4. 测试数据模块...")
try:
    from src.data import DatasetLoader
    print(f"   ✅ 数据模块导入成功")
    print(f"   DatasetLoader: {DatasetLoader}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 测试5: 导入工具模块
print("\n5. 测试工具模块...")
try:
    from src.utils.logger import get_logger, setup_logger
    logger = get_logger("test")
    print(f"   ✅ 工具模块导入成功")
    logger.info("日志系统测试")
    logger.warning("警告测试")
except Exception as e:
    print(f"   ❌ 错误: {e}")

# 测试6: 验证配置文件
print("\n6. 验证配置文件...")
try:
    config = get_config()

    # 检查关键词
    refusal_kw = config.get_keywords("refusal")
    print(f"   ✅ REFUSAL关键词: {len(refusal_kw)}个")

    corrective_kw = config.get_keywords("corrective")
    print(f"   ✅ CORRECTIVE关键词: {len(corrective_kw)}个")

    # 检查模型
    models = config.get_models()
    print(f"   ✅ 配置的模型数: {len(models)}个")

    # 检查路径
    print(f"   ✅ 数据集路径: {config.get_path('dataset')}")
    print(f"   ✅ 结果路径: {config.get_path('results')}")
except Exception as e:
    print(f"   ❌ 错误: {e}")
    import traceback
    traceback.print_exc()

# 测试7: API密钥验证
print("\n7. API密钥状态...")
try:
    config = get_config()
    api_status = config.validate_api_keys()
    for provider, valid in api_status.items():
        status = "✅ 已配置" if valid else "❌ 未配置"
        print(f"   {status} {provider.upper()}")
except Exception as e:
    print(f"   ❌ 错误: {e}")

print("\n" + "="*70)
print("测试完成!")
print("="*70)
