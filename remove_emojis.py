import sys, re

with open('src/app.py', 'r', encoding='utf-8') as f:
    c = f.read()

emojis = ['🌐', '🔬', '📊', '📋', '🛡️', '🧪', '✅', '▶', '🚨', '⚠️', '❌', '🔴', '🟢', '🟡', '🔍', '💾', '🛡', '⚙️', '⚙', '👉']

for e in emojis:
    c = c.replace(e, '')

# Cleanup potential double spaces and orphaned formatting
c = c.replace('page_icon=""', 'page_icon="NetSage"')

# General unicode range removal for any other emojis (excluding standard ascii)
# We will just remove any characters > 0xFFFF (mostly emojis) and some specific ranges
cleaned_chars = []
for char in c:
    if ord(char) > 0xFFFF:
        continue
    # Block miscellaneous symbols and dingbats
    if 0x2600 <= ord(char) <= 0x27BF:
        continue
    cleaned_chars.append(char)

c = "".join(cleaned_chars)
c = c.replace("  ", " ") # clean up double spaces

with open('src/app.py', 'w', encoding='utf-8') as f:
    f.write(c)
