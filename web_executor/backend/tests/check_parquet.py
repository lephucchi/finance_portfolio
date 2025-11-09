import pandas as pd

df = pd.read_parquet('data/rag/metadata.parquet')
print('Shape:', df.shape)
print('Columns:', df.columns.tolist())
print('\nSample row 0:')
for col in df.columns:
    val = df.iloc[0][col]
    if isinstance(val, str) and len(val) > 100:
        print(f'{col}: {val[:100]}...')
    else:
        print(f'{col}: {val}')
