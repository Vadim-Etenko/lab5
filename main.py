import re
from time import time
from itertools import combinations
from operator import itemgetter
import pandas as pd

FILE_PATH = 'Online Retail.xlsx'
FILE_PATH2 = 'Книга1.xlsx'
df = pd.read_excel(FILE_PATH2)

df_filtered = df[~df["InvoiceNo"].str.contains("C", na=False)][['StockCode', 'CustomerID']].dropna()

val_list = list(df_filtered['StockCode'].unique())
count = 1
my_dict = {}
for item in val_list:
    if item not in my_dict:
        my_dict[item] = count
        count += 1
backwards_dict = {value: key for key, value in my_dict.items()}
df_filtered = df_filtered.replace({"StockCode": my_dict}).astype(str)
grouped = df_filtered.groupby(['CustomerID'], as_index=False).agg({'StockCode': ', '.join})

def perform_apriori(data, support_count):
    single_items = (data['StockCode'].str.split(", ", expand=True)).apply(pd.value_counts).sum(axis=1).where(lambda value: value > support_count).dropna()

    apriori_data = pd.DataFrame(
        {'StockCode': single_items.index.astype(int), 'support_count': single_items.values, 'set_size': 1})

    data['set_size'] = data['StockCode'].str.count(",") + 1

    data['StockCode'] = data['StockCode'].apply(lambda row: set(map(int, row.split(","))))

    single_items_set = set(single_items.index.astype(int))
    for length in range(2, len(single_items_set) + 1):
        data = data[data['set_size'] >= length]
        d = data['StockCode'].apply(lambda st: pd.Series(s if set(s).issubset(st) else None for s in combinations(single_items_set, length))).apply(lambda col: [col.dropna().unique()[0], col.count()] if col.count() >= support_count else None).dropna()
        if d.empty:
            break
        apriori_data = apriori_data.append(pd.DataFrame(
            {'StockCode': list(map(itemgetter(0), d.values)), 'support_count': list(map(itemgetter(1), d.values)),
             'set_size': length}), ignore_index=True)

    return apriori_data

result = perform_apriori(data=grouped[['StockCode']], support_count=11).astype(str)

d = result[result["StockCode"].str.contains("\\(", na=False)][["StockCode", "support_count"]]

print(d)

res_string = ' '.join(d['StockCode'].values[0:])
res_string = re.sub("\\) \\(", "\n", res_string)
res_string = re.sub("\\(", "", res_string)
res_string = re.sub("\\)", "", res_string)

new_str = ''

for word in res_string.split():
    if word[len(word) - 1] == ',':
        new_str += str(backwards_dict.get(int(re.sub(",", "", word)))) + ' '
        continue
    new_str += str(backwards_dict.get(int(word))) + '\n'
print(new_str)