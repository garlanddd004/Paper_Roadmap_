import os
import requests
import json
import re

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 你的固定研究过程
FIXED_PROCESS_STEPS = [
    "泛读文献确定选题",
    "精读文献分类梳理",
    "理论分析与研究假设",
    "模型设定与数据选择",
    "实证分析",
    "结论建议"
]

def extract_steps_from_text(text):
    """
    只让模型输出 content_steps，process_steps 完全由代码硬编码填充。
    """
    messages = [
        {
            "role": "system",
            "content": (
                "你是科研技术路线图专家。请只从下面的论文内容中提取“研究内容”部分的关键步骤，包括但不限于引言（理论综述与理论基础），理论分析与研究假设，模型设定与数据选择，实证结构与分析，结论与建议这几部分。"
                "按自上而下的顺序输出。"
                "请只返回 JSON，格式如下：\n"
                "{\n"
                '  "content_steps": ["步骤1", "步骤2", ...]\n'
                "}\n"
                "不要返回任何 process_steps，也不要添加多余的解释。"
            )
        },
        {"role": "user", "content": f"论文内容：\n{text}"}
    ]
    payload = {
        "model": "deepseek-reasoner",
        "messages": messages
    }
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    resp = requests.post(
        "https://api.deepseek.com/v1/chat/completions",
        headers=headers,
        json=payload
    )
    resp.raise_for_status()
    result = resp.json()

    raw = result["choices"][0]["message"]["content"]
    print("===== [DEBUG] LLM 原始回复 =====")
    print(raw)
    print("================================")

    # 清洗 Markdown 或 ```json
    cleaned = re.sub(r"^.*?```json\s*", "", raw, flags=re.DOTALL)
    cleaned = cleaned.replace("```", "").strip()

    m = re.search(r"(\{[\s\S]*\})", cleaned)
    if not m:
        print("[ERROR] 未匹配到 JSON，返回空 content_steps")
        return {"content_steps": [], "process_steps": FIXED_PROCESS_STEPS}

    json_str = m.group(1)
    try:
        data = json.loads(json_str)
        content_steps = data.get("content_steps", [])
    except Exception as e:
        print(f"[ERROR] JSON 解析失败：{e}")
        print(json_str)
        content_steps = []

    return {
        "content_steps": content_steps,
        # 绝不从 data 里取 process_steps，始终返回固定流程
        "process_steps": FIXED_PROCESS_STEPS
    }
