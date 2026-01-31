import pandas as pd
try:
    df = pd.read_excel('app/analytics/faers_random_1000.xlsx')
    print("ALL_COLUMNS_START")
    for col in df.columns:
        print(col)
    print("ALL_COLUMNS_END")
except Exception as e:
    print("Error:", e)
