# -*- coding: utf-8 -*-
"""
企业微信日报推送脚本
功能：自动读取今天的日报 Markdown 文件 → 推送企业微信群 → 清理 15 天前旧文件

Webhook 地址读取优先级：
  1. 环境变量 WECHAT_WEBHOOK
  2. 项目根目录的 .env 文件（WECHAT_WEBHOOK=xxx）
  3. 脚本同目录的 webhook.txt（只写 URL）
"""

import os
import re
import sys
import glob
from datetime import datetime, timedelta
from pathlib import Path

# ─── 配置 ────────────────────────────────────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def load_webhook_url():
    """多途径读取 Webhook 地址"""
    # 1. 环境变量
    url = os.environ.get("WECHAT_WEBHOOK", "").strip()
    if url:
        return url

    # 2. .env 文件
    env_file = PROJECT_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("WECHAT_WEBHOOK="):
                url = line.split("=", 1)[1].strip().strip('"').strip("'")
                if url:
                    return url

    # 3. webhook.txt
    wh_file = Path(__file__).parent / "webhook.txt"
    if wh_file.exists():
        url = wh_file.read_text(encoding="utf-8").strip()
        if url:
            return url

    return None


# ─── 企业微信推送 ────────────────────────────────────────────────

def convert_to_wework_markdown(md_text):
    """将标准 Markdown 转为企业微信兼容格式，并控制长度"""
    lines = md_text.split("\n")
    out = []
    for line in lines:
        stripped = line.strip()
        if not stripped:
            out.append("")
            continue
        if stripped.startswith(">") and ("数据说明" in stripped or "下期预告" in stripped or "数据来源" in stripped):
            continue
        if stripped == "---":
            out.append("---")
            continue
        if stripped.startswith("### "):
            out.append(f"**{stripped[4:]}**")
        elif stripped.startswith("## "):
            out.append(f"> **{stripped[3:]}**")
        elif stripped.startswith("# "):
            out.append(f"> **{stripped[2:]}**")
        elif stripped.startswith("|") and stripped.endswith("|"):
            continue
        else:
            out.append(stripped)

    result = "\n".join(out)

    MAX_BYTES = 3800
    encoded = result.encode("utf-8")
    if len(encoded) > MAX_BYTES:
        current_bytes = 0
        truncated_lines = []
        for line in out:
            line_bytes = len(line.encode("utf-8")) + 1
            if current_bytes + line_bytes > MAX_BYTES - 100:
                break
            truncated_lines.append(line)
            current_bytes += line_bytes
        result = "\n".join(truncated_lines) + "\n\n> ...(剩余内容请查看完整报告)"

    return result


def push_to_wechat(content, webhook_url):
    """通过企业微信 Webhook 发送 Markdown 消息"""
    try:
        import urllib.request
        import json as _json

        payload = {
            "msgtype": "markdown",
            "markdown": {"content": content}
        }
        data = _json.dumps(payload, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            webhook_url,
            data=data,
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = _json.loads(resp.read().decode("utf-8"))

        if result.get("errcode") == 0:
            print(f"[OK] Push succeeded ({len(data)} bytes)")
            return True
        else:
            print(f"[ERROR] Push failed: {result}")
            return False
    except Exception as e:
        print(f"[ERROR] Push exception: {e}")
        return False


# ─── 清理旧文件 ──────────────────────────────────────────────────

def cleanup_old_reports(days=15):
    """删除 days 天前的旧日报文件"""
    cutoff = datetime.now() - timedelta(days=days)
    pattern = str(PROJECT_ROOT / "AI日报_*.md")
    removed = 0
    for fpath in glob.glob(pattern):
        fname = Path(fpath).name
        # 提取日期：AI日报_2026-04-10.md
        m = re.search(r"(\d{4}-\d{2}-\d{2})", fname)
        if m:
            try:
                file_date = datetime.strptime(m.group(1), "%Y-%m-%d")
                if file_date < cutoff:
                    Path(fpath).unlink()
                    print(f"[CLEAN] Removed old file: {fname}")
                    removed += 1
            except ValueError:
                pass
    if removed == 0:
        print("[INFO] No old files to clean")


# ─── 主流程 ──────────────────────────────────────────────────────

def main():
    today = datetime.now().strftime("%Y-%m-%d")
    report_file = PROJECT_ROOT / f"AI日报_{today}.md"

    print(f"\n{'='*50}")
    print(f"[PUSH] WeChat Daily Report - {today}")
    print(f"{'='*50}\n")

    # 读取日报文件
    if not report_file.exists():
        print(f"[ERROR] Report file not found: {report_file}")
        sys.exit(1)

    content_md = report_file.read_text(encoding="utf-8")
    print(f"[OK] Loaded: {report_file.name} ({len(content_md)} chars)")

    # 加载 Webhook 地址
    webhook_url = load_webhook_url()
    if not webhook_url:
        print("[ERROR] WECHAT_WEBHOOK not configured.")
        print("  Options:")
        print("  1. Set env var: WECHAT_WEBHOOK=<url>")
        print("  2. Create .env file in project root: WECHAT_WEBHOOK=<url>")
        print("  3. Create scripts/webhook.txt with the Webhook URL")
        sys.exit(1)

    # 转换并推送
    wx_content = convert_to_wework_markdown(content_md)
    push_to_wechat(wx_content, webhook_url)

    # 清理旧文件
    cleanup_old_reports(days=15)

    print(f"\n[DONE] Completed at {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    main()
