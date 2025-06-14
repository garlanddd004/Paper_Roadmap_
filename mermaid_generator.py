import os
from openai import OpenAI

# 创建 OpenAI 客户端，指向 DeepSeek 接口
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com/v1"
)

# Mermaid 图模板结构（固定部分）
TEMPLATE = r'''
graph TD
    subgraph 研究过程
        A[研究问题] --> B[泛读文献<br>确定选题]
        B --> C[精读文献<br>分类筛选]
        C --> D{理论分析<br>研究假设}
        D --> E[模型设定<br>数据选择]
        E --> F[实证分析]
        F --> G[结论建议]
    end

    subgraph 研究内容
        H[论文标题] --> I[引言]
        I --> J(理论综述)
        I --> K(理论基础)
        J & K --> L{理论分析<br>研究假设}
        L --> L1[信息优化机制]
        L --> L2[风险改善机制]
        L --> L3[创新驱动机制]
        L1 & L2 & L3 --> M[模型设定<br>与数据选择]
        M --> N{实证结构<br>与分析}
        N --> O1[描述性统计]
        N --> O2[相关性分析]
        N --> O3[实证分析]
        N --> O4[稳健性检验]
        O1 & O2 & O3 & O4 --> P[结论建议]
    end
'''

# 默认的研究过程节点（不建议变动）
DEFAULT_PROCESS_NODES = [
    "研究问题",
    "泛读文献 确定选题",
    "精读文献 分类筛选",
    "理论分析 研究假设",
    "模型设定 数据选择",
    "实证分析",
    "结论建议"
]

def build_mermaid_prompt(content_steps, process_steps=None):
    """
    构造 ChatPrompt，让 LLM 根据模板输出 Mermaid 结构图代码。
    """
    process_nodes = process_steps or DEFAULT_PROCESS_NODES

    node_mapping = []
    for idx, text in enumerate(process_nodes, 1):
        node_id = chr(ord('A') + idx - 1)
        node_mapping.append(f"{node_id}: {text}")

    for idx, text in enumerate(content_steps, 1):
        node_id = chr(ord('H') + idx - 1)
        node_mapping.append(f"{node_id}: {text}")

    prompt = (
        "你是一位具备结构分析能力的学术图谱绘制专家，现在需要你仿照下方 Mermaid 示例模板，"
        "生成符合当前研究内容的 Mermaid 图代码。请严格按照以下约定进行操作：\n"
        "1. 模板中的【研究内容】分支结构由 content_steps 填充，请依次替换；\n"
        "2. 文本根据语义换行，推荐使用 <br> 作为换行标记；\n"
        "3. 保证研究过程与研究内容流程节点数量大致对齐；\n"
        "4. 所有连接线为直线或直角折线，禁止使用曲线；\n"
        "5. 禁止更改 subgraph 名称与主结构框架；\n"
        "6. 仅返回 Mermaid 代码块（不要输出解释说明）。\n\n"
        "这是 Mermaid 模板：\n"
        f"{TEMPLATE.strip()}\n\n"
        "以下是当前节点映射关系：\n"
        + "\n".join(node_mapping)
    )
    return prompt


def steps_to_mermaid(content_steps, process_steps=None):
    """
    给定研究内容步骤（content_steps），返回符合结构规范的 Mermaid 图代码。
    """
    prompt = build_mermaid_prompt(content_steps, process_steps)

    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[{"role": "system", "content": prompt}],
        temperature=0
    )

    return response.choices[0].message.content.strip()
