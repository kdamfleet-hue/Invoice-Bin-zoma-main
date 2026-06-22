import pandas as pd
import sys
sys.stdout.reconfigure(encoding='utf-8')

df = pd.read_excel('static/تقرير الورشة.xlsx', header=None)
print(df.to_string())
