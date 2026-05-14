#!/usr/bin/env python3
"""
SKILL 自我进化模块 — v2.0
===========================
基于审计日志和历史数据，自动分析失败模式、优化模板、更新审核规则。

用法:
    python scripts/self_evolve.py analyze          # 分析失败模式
    python scripts/self_evolve.py suggest           # 建议优化方向
    python scripts/self_evolve.py report            # 生成进化报告
    python scripts/self_evolve.py update-rules      # 根据历史数据更新审核规则
"""

import argparse
import json
import os
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from pathlib import Path


def get_log_dir() -> str:
    base = Path(__file__).resolve().parent.parent
    log_dir = base / "logs" / "skill-audit"
    return str(log_dir)


def get_stats_path(log_dir: str) -> str:
    return os.path.join(log_dir, "skill-call-stats.json")


def get_audit_log_path(log_dir: str) -> str:
    return os.path.join(log_dir, "skill-builder-audit.log")


# ============================================================
# 失败模式分析
# ============================================================

FAILURE_PATTERNS = {
    "frontmatter_error": {
        "keywords": ["FRONT MATTER", "frontmatter", "字段校验", "缺少必填"],
        "template": "frontmatter 结构问题（必填字段缺失 / 分隔符错误 / 格式不正确）",
        "suggestion": "在模板生成后立即进行 frontmatter 格式预检",
    },
    "name_format": {
        "keywords": ["kebab-case", "NAME 格式", "命名规范"],
        "template": "name 不符合 kebab-case 规范（应使用小写字母、数字、连字符）",
        "suggestion": "模板中添加 name 自动规范化函数（驼峰→kebab）",
    },
    "description_quality": {
        "keywords": ["描述质量", "DESCRIPTION", "缺少触发场景", "缺少功能动词", "过短"],
        "template": "description 质量不足（缺少 WHEN 或 WHAT 信息）",
        "suggestion": "描述模板增加占位符提示：'[WHAT]... Use when [WHEN]...'",
    },
    "security_credential": {
        "keywords": ["硬编码", "password", "API Key", "Secret", "Secret Key", "Token", "Access Key"],
        "template": "SKILL 中包含硬编码凭证",
        "suggestion": "在创建后自动扫描硬编码凭证并标记",
    },
    "security_injection": {
        "keywords": ["exec()", "eval()", "系统命令", "注入"],
        "template": "SKILL 中存在代码注入风险",
        "suggestion": "提供安全的替代方案模板（如 subprocess.run 代替 os.system）",
    },
    "missing_script": {
        "keywords": ["引用的脚本", "不存在"],
        "template": "SKILL 引用了不存在的脚本/资源文件",
        "suggestion": "在引用资源前先检查文件是否存在，并给出提示",
    },
    "security_unsafe": {
        "keywords": ["chmod 777", "sudo", "rm -rf"],
        "template": "SKILL 包含不安全的高危操作",
        "suggestion": "高危操作需要增加人工确认提示或安全替代方案",
    },
}


def analyze_failures(log_dir: str = None) -> dict:
    """分析失败模式"""
    if not log_dir:
        log_dir = get_log_dir()
    log_path = get_audit_log_path(log_dir)

    if not os.path.exists(log_path):
        return {"error": "暂无日志数据", "need_more_data": True}

    # 读取所有日志
    failures = []
    with open(log_path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if entry.get("result") == "fail":
                    failures.append(entry)
            except json.JSONDecodeError:
                continue

    if not failures:
        return {"total_failures": 0, "patterns": {}, "message": "暂无失败记录"}

    # 分析失败模式
    pattern_counts = Counter()
    pattern_skills = defaultdict(list)
    pattern_reasons = defaultdict(list)

    for entry in failures:
        reason = entry.get("reason", "")
        checks = entry.get("checks", {})
        skill_name = entry.get("skill_name", "unknown")

        # 提取失败原因文本
        combined_text = reason
        for check_name, check_result in checks.items():
            if isinstance(check_result, dict) and not check_result.get("pass", True):
                combined_text += f" {check_result.get('message', '')}"
                for key in ["errors", "warnings", "issues", "findings"]:
                    items = check_result.get(key, [])
                    if items:
                        combined_text += " " + " ".join(
                            [str(i) if isinstance(i, str) else str(i.get("description", i)) for i in items]
                        )

        # 匹配已知模式
        matched = set()
        for pattern_name, pattern_info in FAILURE_PATTERNS.items():
            for kw in pattern_info["keywords"]:
                if kw.lower() in combined_text.lower():
                    pattern_counts[pattern_name] += 1
                    pattern_skills[pattern_name].append(skill_name)
                    pattern_reasons[pattern_name].append(combined_text[:200])
                    matched.add(pattern_name)
                    break

    # 统计结果
    total_failures = len(failures)
    top_patterns = pattern_counts.most_common(10)

    result = {
        "total_failures": total_failures,
        "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "patterns": {},
        "top_recommendations": [],
    }

    for pattern_name, count in top_patterns:
        info = FAILURE_PATTERNS[pattern_name]
        result["patterns"][pattern_name] = {
            "count": count,
            "percentage": f"{count / total_failures * 100:.1f}%",
            "template": info["template"],
            "suggestion": info["suggestion"],
            "affected_skills": list(set(pattern_skills[pattern_name])),
        }

    # 生成建议
    threshold = max(2, total_failures * 0.1)  # 超过10%或至少2次
    for pattern_name, count in top_patterns:
        if count >= threshold:
            result["top_recommendations"].append(FAILURE_PATTERNS[pattern_name]["suggestion"])

    return result


# ============================================================
# 优化建议
# ============================================================

def suggest_improvements(log_dir: str = None) -> dict:
    """基于分析结果给出优化建议"""
    analysis = analyze_failures(log_dir)
    if "error" in analysis:
        return analysis

    stats_path = get_stats_path(log_dir or get_log_dir())
    stats = {}
    if os.path.exists(stats_path):
        with open(stats_path, "r", encoding="utf-8") as f:
            stats = json.load(f)

    # 计算失败率趋势（最近7天 vs 前7天）
    today = datetime.now()
    recent7 = sum(d["total"] for date, d in stats.items()
                  if date >= (today - timedelta(days=7)).strftime("%Y-%m-%d"))
    recent7_fail = sum(d["fail"] for date, d in stats.items()
                       if date >= (today - timedelta(days=7)).strftime("%Y-%m-%d"))

    previous7 = sum(d["total"] for date, d in stats.items()
                    if (today - timedelta(days=14)).strftime("%Y-%m-%d") <= date < (today - timedelta(days=7)).strftime("%Y-%m-%d"))
    previous7_fail = sum(d["fail"] for date, d in stats.items()
                         if (today - timedelta(days=14)).strftime("%Y-%m-%d") <= date < (today - timedelta(days=7)).strftime("%Y-%m-%d"))

    suggestions = []

    # 根据失败模式生成建议
    for pname, pinfo in analysis.get("patterns", {}).items():
        suggestions.append({
            "priority": "HIGH" if pinfo["count"] >= 5 else "MEDIUM" if pinfo["count"] >= 2 else "LOW",
            "pattern": pname,
            "suggestion": pinfo["suggestion"],
            "occurrences": pinfo["count"],
        })

    # 趋势分析建议
    if recent7 > 0:
        recent_rate = recent7_fail / recent7 * 100
        if previous7 > 0:
            prev_rate = previous7_fail / previous7 * 100
            if recent_rate > prev_rate * 1.2:
                suggestions.append({
                    "priority": "HIGH",
                    "pattern": "failure_trend_up",
                    "suggestion": f"失败率上升 ({prev_rate:.0f}% → {recent_rate:.0f}%)，建议暂停大规模创建并排查根因",
                    "occurrences": recent7_fail,
                })

    return {
        "suggestions": sorted(suggestions, key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}[x["priority"]]),
        "stats": {
            "recent_7d_total": recent7,
            "recent_7d_fail": recent7_fail,
            "recent_7d_rate": f"{recent7_fail / max(recent7, 1) * 100:.1f}%",
        },
    }


# ============================================================
# 审核规则更新
# ============================================================

def update_review_rules(log_dir: str = None) -> dict:
    """根据历史数据更新审核规则"""
    analysis = analyze_failures(log_dir)
    if "error" in analysis:
        return analysis

    new_rules = []
    for pname, pinfo in analysis.get("patterns", {}).items():
        if pinfo["count"] >= 3:  # 出现3次以上的模式 -> 作为新规则
            new_rules.append({
                "rule_name": f"auto_{pname}",
                "description": pinfo["template"],
                "source": f"基于 {pinfo['count']} 次失败历史自动生成",
                "suggestion": pinfo["suggestion"],
            })

    # 写入规则文件
    if new_rules:
        rules_file = Path(get_log_dir()) / "auto_rules.json"
        rules = {"generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                 "rules": new_rules}
        with open(rules_file, "w", encoding="utf-8") as f:
            json.dump(rules, f, ensure_ascii=False, indent=2)
        return {"message": f"已生成 {len(new_rules)} 条新审核规则", "rules": new_rules}

    return {"message": "数据不足，暂无新规则生成", "rules": []}


# ============================================================
# 报告生成
# ============================================================

def generate_report(log_dir: str = None):
    """生成完整的自我进化报告"""
    print(f"\n{'='*60}")
    print(f"  SKILL 自我进化报告")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")

    # 失败模式分析
    print(f"\n📊 失败模式分析")
    print(f"{'-'*40}")
    analysis = analyze_failures(log_dir)
    if "error" in analysis:
        print(f"  {analysis['error']}")
    else:
        print(f"  总失败次数: {analysis['total_failures']}")
        for pname, pinfo in sorted(analysis.get("patterns", {}).items(),
                                    key=lambda x: x[1]["count"], reverse=True):
            bar = "█" * min(pinfo["count"], 40)
            affected = ", ".join(pinfo["affected_skills"][:3])
            print(f"  {bar} {pinfo['count']}x  {pname}")
            print(f"     📝 {pinfo['template']}")
            print(f"     💡 {pinfo['suggestion']}")
            if pinfo["affected_skills"]:
                print(f"     🎯 影响: {affected}")

    # 优化建议
    print(f"\n💡 优化建议")
    print(f"{'-'*40}")
    suggestions = suggest_improvements(log_dir)
    for s in suggestions.get("suggestions", []):
        icon = "🔴" if s["priority"] == "HIGH" else "🟡" if s["priority"] == "MEDIUM" else "🟢"
        print(f"  {icon} [{s['priority']}] {s['suggestion']}")

    # 规则更新
    print(f"\n⚙️  审核规则更新")
    print(f"{'-'*40}")
    rules_result = update_review_rules(log_dir)
    print(f"  {rules_result['message']}")
    for r in rules_result.get("rules", []):
        print(f"    - {r['rule_name']}: {r['description']}")

    print(f"\n{'='*60}\n")


# ============================================================
# 主函数
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="SKILL 自我进化模块 v2.0")
    parser.add_argument("command", nargs="?", default="analyze",
                        choices=["analyze", "suggest", "report", "update-rules"],
                        help="操作类型")
    parser.add_argument("--log-dir", default=None, help="日志目录路径")
    args = parser.parse_args()

    log_dir = args.log_dir or get_log_dir()

    if args.command == "analyze":
        result = analyze_failures(log_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "suggest":
        result = suggest_improvements(log_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    elif args.command == "report":
        generate_report(log_dir)

    elif args.command == "update-rules":
        result = update_review_rules(log_dir)
        print(json.dumps(result, ensure_ascii=False, indent=2))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
