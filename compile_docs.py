import os
import glob

workspace = r"c:\Users\SeanTeng\Desktop\Anime Model Chatbot"
output_file = os.path.join(workspace, "FINAL_SYSTEM_PROMPT.md")

md_files = glob.glob(os.path.join(workspace, "*.md"))

content = []
content.append("# FINAL SYSTEM PROMPT & KNOWLEDGE BASE\n")
content.append("## 1. SYSTEM CONFIGURATION\n")

# Add character_config.py
char_config_path = os.path.join(workspace, "backend", "app", "config", "character_config.py")
if os.path.exists(char_config_path):
    with open(char_config_path, "r", encoding="utf-8") as f:
        content.append("### backend/app/config/character_config.py\n```python\n" + f.read() + "\n```\n")

# Add system prompt generation context from ai_service.py
ai_service_path = os.path.join(workspace, "backend", "app", "services", "ai_service.py")
if os.path.exists(ai_service_path):
    with open(ai_service_path, "r", encoding="utf-8") as f:
        # Just extracting relevant routing / system instructions could be hard, let's just dump the file or excerpt
        content.append("### backend/app/services/ai_service.py\n```python\n" + f.read() + "\n```\n")


# Add tools
tools_dir = os.path.join(workspace, "backend", "app", "tools")
if os.path.exists(tools_dir):
    content.append("## 2. SYSTEM TOOLS\n")
    for tool_file in glob.glob(os.path.join(tools_dir, "*.json")):
        with open(tool_file, "r", encoding="utf-8") as f:
            content.append(f"### {os.path.basename(tool_file)}\n```json\n" + f.read() + "\n```\n")

content.append("## 3. PROJECT DOCUMENTATION (MARKDOWN INSTRUCTIONS)\n")
for md_file in sorted(md_files):
    name = os.path.basename(md_file)
    if name == "FINAL_SYSTEM_PROMPT.md": continue
    with open(md_file, "r", encoding="utf-8") as f:
        content.append(f"### File: {name}\n")
        content.append(f.read() + "\n\n---\n")

with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(content))

print(f"Compilation complete. Output saved to {output_file}")
print(f"Total size: {os.path.getsize(output_file)} bytes")
