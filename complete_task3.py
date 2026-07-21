path = r"C:\Users\user\.gemini\antigravity-ide\brain\6538c63a-cec9-41d7-841c-3f9554019e91\task.md"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

content = content.replace("[ ]", "[x]")

with open(path, "w", encoding="utf-8") as f:
    f.write(content)
