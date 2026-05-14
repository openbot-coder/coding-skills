#!/usr/bin/env python3
"""
SKILL 审核脚本 — v2.0
========================
执行 SKILL.md 的可用性审核（Quality Review）和安全性审核（Security Review）。

用法:
    python scripts/review.py <skill-dir>              # 全量审核
    python scripts/review.py <skill-dir> --quality    # 仅可用性审核
    python scripts/review.py <skill-dir> --security   # 仅安全性审核
    python scripts/review.py <skill-dir> --json       # JSON 格式输出
"""

import argparse
import json
import os
import re
import sys
import yaml


# ============================================================
# 可用性审核检查项
# ============================================================

def check_frontmatter_exists(path: str) -> dict:
    """检查 SKILL.md 是否存在"""
    skill_md = os.path.join(path, "SKILL.md")
    if not os.path.isfile(skill_md):
        return {"pass": False, "message": "SKILL.md 文件不存在"}
    return {"pass": True, "message": "SKILL.md 文件存在", "detail": skill_md}


def check_frontmatter_format(path: str) -> dict:
    """检查 front matter 格式是否正确"""
    skill_md = os.path.join(path, "SKILL.md")
    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {"pass": False, "message": f"读取 SKILL.md 失败: {e}"}

    # 检查是否以 --- 开头
    if not content.startswith("---"):
        return {"pass": False, "message": "FRONT MATTER: 必须以 --- 开头"}

    # 提取 front matter
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {"pass": False, "message": "FRONT MATTER: 缺少闭合 ---"}

    yaml_str = parts[1].strip()
    if not yaml_str:
        return {"pass": False, "message": "FRONT MATTER: 内容为空"}

    return {"pass": True, "message": "FRONT MATTER: 格式正确", "raw": yaml_str}


def check_frontmatter_fields(path: str) -> dict:
    """检查 front matter 必填字段"""
    result = check_frontmatter_format(path)
    if not result["pass"]:
        return result

    try:
        meta = yaml.safe_load(result["raw"])
    except yaml.YAMLError as e:
        return {"pass": False, "message": f"FRONT MATTER: YAML 语法错误 - {e}"}

    if not isinstance(meta, dict):
        return {"pass": False, "message": "FRONT MATTER: 解析结果不是字典"}

    errors = []
    if "name" not in meta or not meta["name"]:
        errors.append("缺少必填字段: name")
    if "description" not in meta or not meta["description"]:
        errors.append("缺少必填字段: description")

    # name 格式检查
    if meta.get("name"):
        name = meta["name"]
        if not re.match(r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?$', name):
            errors.append(f"NAME 格式错误: '{name}' — 必须为 kebab-case（小写字母、数字、连字符）")
        if len(name) < 2 or len(name) > 64:
            errors.append(f"NAME 长度错误: {len(name)} 字符 — 需在 2-64 之间")

    # description 质量检查
    if meta.get("description"):
        desc = meta["description"]
        if len(desc) < 10:
            errors.append(f"DESCRIPTION 过短: {len(desc)} 字符 — 至少 10 字符")
        if len(desc) > 1024:
            errors.append(f"DESCRIPTION 过长: {len(desc)} 字符 — 最多 1024 字符")

    if errors:
        return {"pass": False, "message": "字段校验不通过", "errors": errors}
    return {"pass": True, "message": "必填字段完整且格式正确", "meta": meta}


def check_description_quality(path: str) -> dict:
    """检查 description 是否包含 WHAT + WHEN 信息"""
    result = check_frontmatter_fields(path)
    if not result["pass"] or "meta" not in result:
        return {"pass": False, "message": "先修复 front matter 字段问题"}

    desc = result["meta"].get("description", "")
    errors = []

    # 检查触发词
    triggers = ["use when", "use for", "trigger", "适合", "用于", "当"]
    if not any(t in desc.lower() for t in triggers):
        errors.append("缺少触发场景描述（建议包含 'Use when' / '适合' 等触发词）")

    # 检查技能功能描述
    action_keywords = [
        "extract", "create", "generate", "analyze", "convert", "process",
        "manage", "search", "validate", "transform", "build", "scan",
        "fix", "optimize", "review", "test", "deploy", "monitor",
        "检查", "生成", "创建", "分析", "转换", "处理", "管理", "搜索", "验证",
    ]
    if not any(k in desc.lower() for k in action_keywords):
        errors.append("缺少功能动词描述（建议包含 'create' / 'analyze' / '生成' 等动作词）")

    if errors:
        return {"pass": False, "message": "描述质量待优化", "errors": errors}
    return {"pass": True, "message": "描述质量良好（含 WHAT + WHEN）"}


def check_workflow_coherence(path: str) -> dict:
    """检查业务流程是否连贯"""
    skill_md = os.path.join(path, "SKILL.md")
    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return {"pass": False, "message": f"读取失败: {e}"}

    sections = re.findall(r'^##\s+(.+)$', content, re.MULTILINE)
    h3_sections = re.findall(r'^###\s+(.+)$', content, re.MULTILINE)

    warnings = []
    if not sections and not h3_sections:
        warnings.append("SKILL.md 无二级/三级标题，可能缺乏结构化的流程说明")

    # 检查是否存在引用但未定义的脚本
    script_refs = re.findall(r'python\s+scripts/(\w+\.py)', content)
    for ref in script_refs:
        ref_path = os.path.join(path, "scripts", ref)
        if not os.path.isfile(ref_path):
            warnings.append(f"引用的脚本 scripts/{ref} 不存在")

    if warnings:
        return {"pass": False, "message": "流程检查发现警告", "warnings": warnings}
    return {"pass": True, "message": "业务流程结构合理"}


def check_executability(path: str) -> dict:
    """检查引用的脚本/工具是否存在"""
    skill_md = os.path.join(path, "SKILL.md")
    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
    except:
        return {"pass": False, "message": "无法读取 SKILL.md"}

    issues = []

    # 检查 scripts/ 引用
    script_dir = os.path.join(path, "scripts")
    if os.path.isdir(script_dir):
        referenced = set(re.findall(r'python\s+scripts/([\w./-]+)', content))
        existing = set()
        for root, _, files in os.walk(script_dir):
            for f in files:
                if f.endswith(('.py', '.sh', '.js', '.ts')):
                    rel = os.path.relpath(os.path.join(root, f), script_dir)
                    existing.add(rel.replace("\\", "/"))
        missing = referenced - existing
        for m in missing:
            issues.append(f"引用的脚本 scripts/{m} 不存在于 filesystem")

    # 检查 references/ 引用
    ref_dir = os.path.join(path, "references")
    if os.path.isdir(ref_dir):
        refs = re.findall(r'\[.*?\]\(references/([\w./-]+)\)', content)
        for ref in refs:
            if not os.path.isfile(os.path.join(ref_dir, ref)):
                issues.append(f"引用的文档 references/{ref} 不存在")

    if issues:
        return {"pass": False, "message": "可执行性检查发现问题", "issues": issues}
    return {"pass": True, "message": "引用的资源均存在"}


# ============================================================
# 安全性审核检查项
# ============================================================

SECURITY_PATTERNS = [
    # 执行危险函数
    (r'\bexec\s*\([^)]*\)',            "使用 exec() — 存在代码注入风险"),
    (r'\beval\s*\([^)]*\)',            "使用 eval() — 存在代码注入风险"),
    (r'\b__import__\s*\([^)]*\)',      "使用 __import__() — 存在代码注入风险"),

    # shell 命令执行
    (r'os\.system\s*\(',               "使用 os.system() — 存在命令注入风险"),
    (r'subprocess\.\w+\s*\(\s*shell\s*=\s*True', "subprocess shell=True — 存在命令注入风险"),
    (r'\bexec\s*`',                     "反引号命令执行 — 存在命令注入风险"),

    # 凭证泄露
    (r'(?i)password\s*=\s*["\'][^"\']+["\']',      "疑似硬编码密码"),
    (r'(?i)(api_key|apikey)\s*=\s*["\'][^"\']+["\']', "疑似硬编码 API Key"),
    (r'(?i)(secret|token)\s*=\s*["\'][^"\']+["\']',   "疑似硬编码 Secret/Token"),
    (r'(?i)ak\s*=\s*["\'][A-Za-z0-9+/=]{20,}["\']',  "疑似硬编码 Access Key"),
    (r'(?i)sk\s*=\s*["\'][A-Za-z0-9+/=]{20,}["\']',  "疑似硬编码 Secret Key"),

    # 路径穿越
    (r'\.\./|\.\.\\\\',         "路径操作中存在 ../ — 可能存在路径穿越"),

    # 不安全的文件操作
    (r'input\s*\(',             "使用 input() — 在非交互场景中可能有问题"),
    (r'pickle\.loads?\s*\([^)]*\)',  "使用 pickle 反序列化 — 存在反序列化攻击风险"),

    # 外部请求（需确认是否安全）
    (r'requests?\.(get|post)\s*\(f["\']',    "使用 f-string 拼接 URL — 可能存在 SSRF/注入"),

    # 高权限操作
    (r'(?i)sudo\s+',            "使用 sudo 提权 — 确认是否必需"),
    (r'(?i)chmod\s+777',         "设置 777 权限 — 权限过于宽松"),
    (r'(?i)rm\s+-rf\s+/',       "危险的 rm -rf / 操作"),
]


def check_security_in_skill(path: str) -> dict:
    """检查 SKILL.md 和 scripts/ 中的安全隐患"""
    findings = []
    skill_paths = []

    # 收集所有文本文件
    skill_md = os.path.join(path, "SKILL.md")
    if os.path.isfile(skill_md):
        skill_paths.append(skill_md)

    script_dir = os.path.join(path, "scripts")
    if os.path.isdir(script_dir):
        for root, _, files in os.walk(script_dir):
            for f in files:
                if f.endswith(('.py', '.sh', '.js', '.ts', '.md', '.yaml', '.yml', '.json', '.toml')):
                    skill_paths.append(os.path.join(root, f))

    # 逐文件检查
    for filepath in skill_paths:
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
        except Exception:
            continue

        for lineno, line in enumerate(lines, 1):
            for pattern, desc in SECURITY_PATTERNS:
                if re.search(pattern, line):
                    rel_path = os.path.relpath(filepath, path)
                    findings.append({
                        "file": rel_path,
                        "line": lineno,
                        "severity": "HIGH" if "exec" in pattern or "eval" in pattern or "token" in pattern.lower() else "MEDIUM",
                        "description": desc,
                        "code": line.strip()[:120],
                    })
                    # 每个模式每文件只报告一次
                    break  # 继续下一行

    if findings:
        return {"pass": False, "message": f"发现 {len(findings)} 个安全隐患", "findings": findings}
    return {"pass": True, "message": "未发现安全隐患"}


# ============================================================
# 主函数
# ============================================================

def run_all_checks(path: str) -> dict:
    """运行所有审核"""
    results = {
        "quality": {},
        "security": {},
    }

    # 可用性审核
    results["quality"]["frontmatter_exists"] = check_frontmatter_exists(path)
    results["quality"]["frontmatter_fields"] = check_frontmatter_fields(path)
    results["quality"]["description_quality"] = check_description_quality(path)
    results["quality"]["workflow_coherence"] = check_workflow_coherence(path)
    results["quality"]["executability"] = check_executability(path)

    # 安全性审核
    results["security"]["patterns"] = check_security_in_skill(path)

    return results


def print_human_report(results: dict, path: str):
    """打印人类可读的报告"""
    skill_name = os.path.basename(path)
    print(f"\n{'='*60}")
    print(f"  SKILL 审核报告 — {skill_name}")
    print(f"{'='*60}")

    # 可用性
    print(f"\n📋 可用性审核 (Quality Review)")
    print(f"{'-'*40}")
    all_quality_pass = True
    for check_name, check_result in results["quality"].items():
        status = "✅" if check_result["pass"] else "❌"
        print(f"  {status} [{check_name}] {check_result['message']}")
        if not check_result["pass"]:
            all_quality_pass = False
            for key in ["errors", "warnings", "issues"]:
                if key in check_result:
                    for item in check_result[key]:
                        print(f"       - {item}")

    # 安全性
    print(f"\n🔒 安全性审核 (Security Review)")
    print(f"{'-'*40}")
    sec = results["security"]["patterns"]
    if sec["pass"]:
        print(f"  ✅ {sec['message']}")
    else:
        print(f"  ❌ {sec['message']}")
        for f in sec["findings"]:
            severity_icon = "🔴" if f["severity"] == "HIGH" else "🟡"
            print(f"  {severity_icon} [{f['severity']}] {f['file']}:{f['line']}")
            print(f"       {f['description']}")
            print(f"       {f['code']}")

    # 总评
    print(f"\n{'='*40}")
    all_pass = all_quality_pass and sec["pass"]
    if all_pass:
        print(f"  ✅ 审核通过 — SKILL 可发布")
    else:
        print(f"  ⚠️  审核未通过 — 请修复上述问题后重试")
    print(f"{'='*40}\n")


def main():
    parser = argparse.ArgumentParser(description="SKILL 审核工具 v2.0")
    parser.add_argument("path", nargs="?", default=".",
                        help="SKILL 所在目录路径（默认当前目录）")
    parser.add_argument("--quality", action="store_true",
                        help="仅执行可用性审核")
    parser.add_argument("--security", action="store_true",
                        help="仅执行安全性审核")
    parser.add_argument("--json", action="store_true",
                        help="JSON 格式输出")
    args = parser.parse_args()

    path = os.path.abspath(args.path)

    if not os.path.isdir(path):
        print(f"错误: 目录不存在 — {path}", file=sys.stderr)
        sys.exit(1)

    # 判断审核范围
    if args.quality:
        results = {"quality": {}, "security": {"patterns": {"pass": True, "message": "跳过"}}}
        results["quality"]["frontmatter_exists"] = check_frontmatter_exists(path)
        results["quality"]["frontmatter_fields"] = check_frontmatter_fields(path)
        results["quality"]["description_quality"] = check_description_quality(path)
        results["quality"]["workflow_coherence"] = check_workflow_coherence(path)
        results["quality"]["executability"] = check_executability(path)
    elif args.security:
        results = {
            "quality": {"skipped": {"pass": True, "message": "跳过"}},
            "security": {"patterns": check_security_in_skill(path)},
        }
    else:
        results = run_all_checks(path)

    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print_human_report(results, path)

    # 返回码：审核通过 0，不通过 1
    quality_pass = all(c["pass"] for c in results["quality"].values())
    security_pass = results["security"]["patterns"]["pass"]
    sys.exit(0 if quality_pass and security_pass else 1)


if __name__ == "__main__":
    main()
