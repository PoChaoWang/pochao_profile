import pandas as pd
import os

files = [
    'japan_population_data_0003459019.csv',
    'japan_population_data_0003448229.csv',
    'japan_population_data_0004008041.csv'
]

def data_clean(files, input_file_path, output_filename, output_file_path):
    columns_to_drop = [
            'tab_code', '表章項目', 'cat01_code', '男女別', 'cat02_code', '人口', 
            'cat03_code', '年齢5歳階級', 'area_code', '全国', 'time_code', 
            '時間軸（月）', 'unit', 'annotation'
        ]
    dataframes = []

    for file in files:
        full_file_path = os.path.join(input_file_path, file)  
        df = pd.read_csv(full_file_path) 
        # if year is not 2023, then only keep the data of December.
        # if year is 2023, then only keep the data of October.
        df['time_code'] = df['time_code'].astype(str)
        if '2023' not in df['time_code'].str[:4].values:
            df = df[(df['time_code'].str[6:8] == '12')]
        else:
            df = df[(df['time_code'].str[6:8] == '10')]

        # exclude the data of '人口' not '総人口'
        df = df[df['人口'] == '総人口']

        # exclude the data of '男女別' not '男女計'
        df = df[df['男女別'] == '男女計']

        df = df[df['年齢5歳階級'] == '総数']

        df['value'] = df['value'] * 1000

        df['value'] = df['value'].astype(int)

        df['year'] = df['time_code'].str[:4].astype(int)
        # exclude the data of year less than 2014
        df = df[df['year'] >= 2014]
        print(df)

        # reorder the columns
        columns_order = ['year'] + [col for col in df.columns if col != 'year']
        df = df[columns_order]

        
        df = df.drop(columns=columns_to_drop, errors='ignore')

        # add the processed dataframe to the list
        dataframes.append(df)
    
    # combine all the dataframes
    combined_df = pd.concat(dataframes, ignore_index=True)
    combined_df = combined_df.sort_values(by='year')

    # save the combined dataframe to the output file path
    output_path = os.path.join(output_file_path, output_filename)
    combined_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"Data saved to {output_path}")
    

    

files = [
    'japan_population_data_0003459019.csv',
    'japan_population_data_0003448229.csv',
    'japan_population_data_0004008041.csv'
]


data_clean(files,'raw', 'japan_population_yoy.csv', 'data')













