#!/usr/bin/env python3
"""RAG 对比实验脚本

对比「带知识库」vs「不带知识库」的回答质量差异。
用法: python run_comparison.py [--output results.json]
"""

import json
import time
import argparse
from pathlib import Path
from datetime import datetime

from conversation import Conversation


def run_single_test(question: str, use_kb: bool) -> dict:
    """运行单轮测试，返回结果"""
    try:
        # 直接通过初始化参数控制是否使用知识库
        conv = Conversation(use_kb=use_kb)
        answer = conv.turn(question)
        return {
            "answer": answer,
            "turn_count": conv.turn_count,
        }
    except Exception as e:
        return {
            "answer": f"[错误] {str(e)}",
            "turn_count": 0,
            "error": str(e),
        }


def run_comparison(test_file: str = "test_questions.json", output_file: str = None):
    """运行完整对比实验"""
    # 加载测试问题
    test_path = Path(test_file)
    if not test_path.exists():
        print(f"❌ 测试文件不存在: {test_file}")
        return

    with open(test_path, "r", encoding="utf-8") as f:
        questions = json.load(f)

    # 设置输出文件
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"comparison_results_{timestamp}.json"

    output_path = Path(output_file)

    # 如果已有结果，加载继续
    results = []
    completed_ids = set()
    if output_path.exists():
        with open(output_path, "r", encoding="utf-8") as f:
            results = json.load(f)
        completed_ids = {r["id"] for r in results}
        print(f"✓ 检测到已有结果，已跳过 {len(completed_ids)} 个问题")

    print(f"\n{'='*60}")
    print(f"RAG 对比实验")
    print(f"{'='*60}")
    print(f"测试问题数: {len(questions)}")
    print(f"输出文件: {output_file}")
    print(f"{'='*60}\n")

    total = len(questions)
    for i, q in enumerate(questions, 1):
        qid = q["id"]

        if qid in completed_ids:
            print(f"[{i}/{total}] {qid} - 已存在，跳过")
            continue

        print(f"\n[{i}/{total}] {qid} - {q['category']}")
        print(f"问题: {q['question']}")

        # 测试带知识库
        print("  → 带知识库...", end=" ", flush=True)
        start = time.time()
        result_with_kb = run_single_test(q["question"], use_kb=True)
        time_with_kb = round(time.time() - start, 2)
        print(f"✓ ({time_with_kb}s)")

        # 短暂延迟，避免 API 限流
        time.sleep(1)

        # 测试不带知识库
        print("  → 不带知识库...", end=" ", flush=True)
        start = time.time()
        result_without_kb = run_single_test(q["question"], use_kb=False)
        time_without_kb = round(time.time() - start, 2)
        print(f"✓ ({time_without_kb}s)")

        # 保存结果
        result = {
            "id": qid,
            "category": q["category"],
            "question": q["question"],
            "with_kb": {
                "answer": result_with_kb["answer"],
                "time": time_with_kb,
            },
            "without_kb": {
                "answer": result_without_kb["answer"],
                "time": time_without_kb,
            },
        }
        results.append(result)

        # 每完成一个就保存，支持断点续跑
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)

        # 延迟，避免 API 限流
        time.sleep(2)

    print(f"\n{'='*60}")
    print(f"✓ 实验完成！结果已保存至: {output_file}")
    print(f"{'='*60}\n")

    return output_file


def generate_report(results_file: str):
    """生成对比报告"""
    with open(results_file, "r", encoding="utf-8") as f:
        results = json.load(f)

    report_lines = [
        "# RAG 对比实验报告",
        "",
        f"实验时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"测试问题数: {len(results)}",
        "",
        "## 实验设置",
        "",
        "- **带知识库**: 使用 RAG 检索增强，从知识库获取相关信息",
        "- **不带知识库**: 直接使用 LLM 回答，无外部知识支持",
        "",
        "## 详细结果",
        "",
    ]

    for r in results:
        report_lines.extend([
            f"### {r['id']} - {r['category']}",
            "",
            f"**问题**: {r['question']}",
            "",
            f"**带知识库** ({r['with_kb']['time']}s):",
            "",
            f"```\n{r['with_kb']['answer']}\n```",
            "",
            f"**不带知识库** ({r['without_kb']['time']}s):",
            "",
            f"```\n{r['without_kb']['answer']}\n```",
            "",
            "---",
            "",
        ])

    report_file = results_file.replace(".json", "_report.md")
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"✓ 报告已生成: {report_file}")
    return report_file


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="RAG 对比实验")
    parser.add_argument(
        "--test-file",
        default="test_questions.json",
        help="测试问题文件 (默认: test_questions.json)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="输出结果文件 (默认: comparison_results_时间戳.json)",
    )
    parser.add_argument(
        "--report",
        action="store_true",
        help="仅生成报告，不运行实验",
    )

    args = parser.parse_args()

    if args.report:
        # 查找最新的结果文件
        result_files = sorted(Path(".").glob("comparison_results_*.json"))
        if not result_files:
            print("❌ 未找到结果文件，请先运行实验")
        else:
            generate_report(str(result_files[-1]))
    else:
        results_file = run_comparison(args.test_file, args.output)
        generate_report(results_file)
