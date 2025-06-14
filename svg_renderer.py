# svg_renderer.py

import subprocess
import uuid
import os
import shutil

def render_mermaid_to_svg(mmd_content, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    if mmd_content.strip().startswith("```mermaid"):
        mmd_content = mmd_content.strip()
        mmd_content = mmd_content.replace("```mermaid", "", 1)
        mmd_content = mmd_content.replace("```", "", 1).strip()

    temp_id = str(uuid.uuid4())
    mmd_path = os.path.join(output_dir, f"temp_{temp_id}.mmd")
    svg_path = os.path.join(output_dir, "diagram.svg")
    with open(mmd_path, "w", encoding="utf-8") as f:
        f.write(mmd_content)

    # 清理一下：把 Windows 反斜杠转正斜杠（Mermaid 有时更友好）
    mmd_path = mmd_path.replace("\\", "/")
    svg_path = svg_path.replace("\\", "/")

    # 查找 mmdc
    mmdc_cmd = shutil.which("mmdc") or shutil.which("mmdc.cmd")
    if not mmdc_cmd:
        # 回退用 npx
        cmd = ["npx", "mmdc", "-i", mmd_path, "-o", svg_path]
        shell = True
    else:
        cmd = [mmdc_cmd, "-i", mmd_path, "-o", svg_path]
        shell = False

    # 执行并捕获输出
    proc = subprocess.run(
        cmd,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if proc.returncode != 0:
        # 打印 stderr 帮助调试
        print("===== mmdc STDERR =====")
        print(proc.stderr)
        print("===== mmdc STDOUT =====")
        print(proc.stdout)
        raise RuntimeError(
            f"SVG 渲染失败 (exit {proc.returncode})\n"
            f"命令: {' '.join(cmd)}\n"
            f"See mmdc stderr above."
        )

    # 删除临时文件
    os.remove(mmd_path)
