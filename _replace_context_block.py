from pathlib import Path

path = Path('fun_fact_poster.py')
text = path.read_text()
old = """    context = (
        f\"Title: {article['title']}\r\n\"
        f\"Description: {article['description']}\r\n\"
        f\"Content: {article['content']}\r\n\"
        f\"Source: {article['source']}\r\n\"
        f\"URL: {article['url']}\"
    )
"""
new = """    context = (
        f\"Title: {article['title']}\\n\"
        f\"Description: {article['description']}\\n\"
        f\"Content: {article['content']}\\n\"
        f\"Source: {article['source']}\\n\"
        f\"URL: {article['url']}\"
    )
"""
if old not in text:
    raise SystemExit('old block not found')
text = text.replace(old, new)
path.write_text(text)
