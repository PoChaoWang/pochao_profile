import pandas as pd
import os
import io
import difflib

files = [
    'japan_population_data_0003459019.csv',
    'japan_population_data_0003448229.csv',
    'japan_population_data_0004008041.csv'
]

columns_to_keep = ['男女別', '人口', '年齢５歳階級', 'time_code', 'value']

def find_closest_match(column, choices):
    return difflib.get_close_matches(column, choices, n=1, cutoff=0.6)[0]

def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = pd.read_csv(io.StringIO(f.read()))
    
    columns_to_keep_matched = [find_closest_match(col, data.columns) for col in columns_to_keep]
    data = data[columns_to_keep_matched]

    gender_column = find_closest_match('男女別', data.columns)
    population_column = find_closest_match('人口', data.columns)
    age_column = find_closest_match('年齢５歳階級', data.columns)
    time_code_column = find_closest_match('time_code', data.columns)
    value_column = find_closest_match('value', data.columns)

    data = data[(data[gender_column] != '男女計') & (data[population_column] != '総人口')]

    for word in ['歳', '（再掲）', 'うち']:
        data[age_column] = data[age_column].str.replace(word, '', regex=False)
    data[age_column] = data[age_column].str.strip()

    exclude_age_groups = ['総数', '15未満', '15～64', '65以上','75以上', '85以上']
    data = data[~data[age_column].isin(exclude_age_groups)]

    data = data.rename(columns={age_column: 'age', gender_column: 'gender', time_code_column: 'time_code', value_column: 'value'})

    age_groups = {
        'under_19': ['0～4', '5～9','10～14', '15～19'],
        '20-29': ['20～24', '25～29'],
        '30-39': ['30～34', '35～39'],
        '40-49': ['40～44', '45～49'],
        '50-59': ['50～54', '55～59'],
        '60-69': ['60～64', '65～69'],
        '70-79': ['70～74', '75～79'],
        'over_80': ['80～84', '85～89', '90～94', '95～99', '100以上']
    }

    new_data = []
    for new_group, old_groups in age_groups.items():
        group_data = data[data['age'].isin(old_groups)]
        if not group_data.empty:
            group_sum = group_data.groupby(['gender', 'time_code'])['value'].sum().reset_index()
            group_sum['age'] = new_group
            new_data.append(group_sum)

    data = pd.concat(new_data, ignore_index=True)

    data['time_code'] = data['time_code'].astype(str)
    data['year'] = data['time_code'].str[:4].astype(int)
    data['month'] = data['time_code'].str[6:8].astype(int)
    data = data.drop('time_code', axis=1)

    return data[['year', 'month', 'gender', 'age', 'value']]

all_data = pd.concat([process_file(os.path.join('raw', file)) for file in files], ignore_index=True)

all_data['gender'] = all_data['gender'].map({'男': 'male', '女': 'female'})

all_data = all_data.groupby(['year', 'month', 'gender', 'age'])['value'].sum().reset_index()

duplicates = all_data.duplicated(['year', 'month', 'gender', 'age'])
if duplicates.any():
    print("Warning: Found {duplicates.sum()} rows of duplicate data")
    print("Duplicate data example:")
    print(all_data[duplicates].head())
else:
    print("Did not find duplicate data")

all_data = all_data.sort_values(['year', 'month', 'gender', 'age']).reset_index(drop=True)

print(all_data.head(10))

all_data.to_csv('data/japan_population_data.csv', index=False, encoding='utf-8-sig')
print(f"Data saved to japan_population_data.csv")   