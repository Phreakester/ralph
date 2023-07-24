import json
import requests

from ralph import Ralph

with open('tokens.json') as f:
    tokens = json.load(f)

print(tokens)

ralph_obj = Ralph(tokens['google_sheets'], tokens['kroger_secret'])
print(ralph_obj)