import json
from ralph import Ralph

with open('tokens.json') as f:
    tokens = json.load(f)

ralph_obj = Ralph(tokens['google_sheets'], tokens['kroger_secret'], tokens['westwood_ralphs_id'])

ralph_obj.launch()