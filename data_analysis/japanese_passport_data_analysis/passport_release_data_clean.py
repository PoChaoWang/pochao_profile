import pandas as pd
import os
import glob
import difflib

def find_closest_sheet(excel_file, target_name):
    sheet_names = excel_file.sheet_names
    closest_match = difflib.get_close_matches(target_name, sheet_names, n=1, cutoff=0.6)
    return closest_match[0] if closest_match else None

def translate_city(city):
    city_map = {
        "北海道": "Hokkaido", "青森": "Aomori", "岩手": "Iwate", "宮城": "Miyagi",
        "秋田": "Akita", "山形": "Yamagata", "福島": "Fukushima", "茨城": "Ibaraki",
        "栃木": "Tochigi", "群馬": "Gunma", "埼玉": "Saitama", "千葉": "Chiba",
        "東京": "Tokyo", "神奈川": "Kanagawa", "新潟": "Niigata", "富山": "Toyama",
        "石川": "Ishikawa", "福井": "Fukui", "山梨": "Yamanashi", "長野": "Nagano",
        "岐阜": "Gifu", "静岡": "Shizuoka", "愛知": "Aichi", "三重": "Mie",
        "滋賀": "Shiga", "京都": "Kyoto", "大阪": "Osaka", "兵庫": "Hyogo",
        "奈良": "Nara", "和歌山": "Wakayama", "鳥取": "Tottori", "島根": "Shimane",
        "岡山": "Okayama", "広島": "Hiroshima", "山口": "Yamaguchi", "徳島": "Tokushima",
        "香川": "Kagawa", "愛媛": "Ehime", "高知": "Kochi", "福岡": "Fukuoka",
        "佐賀": "Saga", "長崎": "Nagasaki", "熊本": "Kumamoto", "大分": "Oita",
        "宮崎": "Miyazaki", "鹿児島": "Kagoshima", "沖縄": "Okinawa"
    }
    return city_map.get(city, city)

def category_clean(file_path):
    year = os.path.basename(file_path).split('.')[0]
    excel_file = pd.ExcelFile(file_path)
    target_sheet_name = '月別・種類別発行数'
    sheet_name = find_closest_sheet(excel_file, target_sheet_name)
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    df_category = df.iloc[1:].reset_index(drop=True)
    
    df_category = df_category.rename(columns={df_category.columns[0]: "month"})

    categories = ['general_5_years', 'general_10_years', 'information_changing','subtotal', 'diplomatic', 'official', 'subtotal2','total']
    if len(df_category.columns) - 1 == len(categories):
        df_category.columns = ["month"] + categories
    else:
        print(f"Warning: Category column number mismatch, expected {len(categories)} columns, actual {len(df_category.columns) - 1} columns")
    

    df_category = df_category.drop(['subtotal', 'subtotal2','total'], axis=1)
    categories = [cat for cat in categories if cat not in ['subtotal', 'subtotal2','total']]
    df_long = df_category.melt(id_vars=["month"], var_name="category", value_name="application")

    df_long.insert(0, 'year', year)
    
    df_long['month'] = pd.to_numeric(df_long['month'], errors='coerce')
    df_long = df_long.dropna(subset=['month'])
    df_long['month'] = df_long['month'].astype(int)
    
    return df_long

def age_clean(file_path):
    year = os.path.basename(file_path).split('.')[0]
    excel_file = pd.ExcelFile(file_path)
    target_sheet_name = '年代別・月別発行数'
    sheet_name = find_closest_sheet(excel_file, target_sheet_name)
    
    df_age = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Rename the column names

    age_groups = ['under_19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', 'over_80', 'total']
    
    df_age = df_age.rename(columns={df_age.columns[0]: "month"})

    if len(df_age.columns) - 1 == len(age_groups):
        df_age.columns = ["month"] + age_groups
    else:
        print(f"Warning: Age group column number mismatch, expected {len(age_groups)} columns, actual {len(df_age.columns) - 1} columns")
    
    # Check if 'total' column exists before dropping it
    if 'total' in df_age.columns:
        df_age = df_age.drop(['total'], axis=1)
        age_groups = [cat for cat in age_groups if cat not in ['total']]

    df_long = df_age.melt(id_vars=["month"], var_name="age_group", value_name="application")
    df_long["application"] = pd.to_numeric(df_long["application"], errors="coerce")
    df_long["application"] = df_long["application"].round().astype('Int64')
    df_long = df_long.dropna(subset=["application"])
    
    # Add year column
    df_long.insert(0, 'year', year)
    
    df_long['month'] = pd.to_numeric(df_long['month'], errors='coerce')
    df_long = df_long.dropna(subset=['month'])
    df_long['month'] = df_long['month'].astype(int)
    return df_long

def gender_clean(file_path):
    year = os.path.basename(file_path).split('.')[0]
    excel_file = pd.ExcelFile(file_path)
    target_sheet_name = '性別・月別発行数'
    sheet_name = find_closest_sheet(excel_file, target_sheet_name)
    df_gender = pd.read_excel(file_path, sheet_name=sheet_name)

    start_row = df_gender.index[df_gender.iloc[:, 0].apply(lambda x: isinstance(x, (int, float)) and 1 <= x <= 12)].min()
    if pd.isna(start_row):
        print(f"Warning: No valid month data found in file {file_path}")
        return None

    # Extract the data part
    df_gender = df_gender.iloc[start_row:].reset_index(drop=True)

    df_gender = df_gender.rename(columns={df_gender.columns[0]: "month"})

    genders = ['male', 'female','total']
    if len(df_gender.columns) - 1 == len( genders):
        df_gender.columns = ["month"] +  genders
    else:
        print(f"警告：年齡組列數不匹配，預期 {len( genders)} 列，實際 {len(df_gender.columns) - 1} 列")

    if 'total' in df_gender.columns:
        df_gender = df_gender.drop(['total'], axis=1)
        genders = [cat for cat in genders if cat not in ['total']]

    df_long = df_gender.melt(id_vars=["month"], var_name="gender", value_name="application")

    df_long['month'] = pd.to_numeric(df_long['month'], errors='coerce')
    df_long = df_long.dropna(subset=['month'])
    df_long['month'] = df_long['month'].astype(int)
    df_long.insert(0, 'year', year)
    print(sheet_name)

    return df_long

def city_clean(file_path):
    year = os.path.basename(file_path).split('.')[0]
    excel_file = pd.ExcelFile(file_path)
    target_sheet_name = '月別・都道府県別発行数'
    sheet_name = find_closest_sheet(excel_file, target_sheet_name)
    
    if not sheet_name:
        print(f"Warning: No matching sheet found in file {file_path}")
        return None
    
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    start_row = df.index[df.iloc[:, 0].apply(lambda x: isinstance(x, str) and '北海道' in str(x))].tolist()
    
    if not start_row:
        print(f"Warning: No row containing '北海道' found in file {file_path}")
        return None
    
    start_row = start_row[0]
    
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=start_row)
    df = df.rename(columns={df.columns[0]: "city"})
    df = df.iloc[:, :-1]
    month_columns = [col for col in df.columns if col != "city"]
    if len(month_columns) == 12:
        df.columns = ["city"] + list(range(1, 13))
    
    df_long = df.melt(id_vars=["city"], var_name="month", value_name="application")
    df_long = df_long[~df_long["city"].isin(["計", "外務省", "合計"])]
    df_long = df_long.dropna(subset=["city", "month", "application"])
    df_long["city"] = df_long["city"].apply(translate_city)
    df_long = df_long[~df_long["city"].str.contains("小計", na=False)]
    
    df_long["month"] = pd.to_numeric(df_long["month"], errors="coerce")
    df_long = df_long.dropna(subset=["month"])
    df_long["month"] = df_long["month"].astype(int)
    
    
    
    df_long.insert(0, 'year', year)
    df_long = df_long.sort_values(["year", "month"])
    
    
    return df_long

def age_city_clean(file_path):
    year = os.path.basename(file_path).split('.')[0]
    excel_file = pd.ExcelFile(file_path)
    target_sheet_name = '年代別・都道府県別発行数'
    sheet_name = find_closest_sheet(excel_file, target_sheet_name)
    
    if not sheet_name:
        print(f"Warning: No matching sheet found in file {file_path}")
        return None
    
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    start_row = df.index[df.iloc[:, 0].apply(lambda x: isinstance(x, str) and '北海道' in str(x))].tolist()
    
    if not start_row:
        print(f"Warning: No row containing '北海道' found in file {file_path}")
        return None
    
    start_row = start_row[0]
    
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=start_row)
  
    df = df.rename(columns={df.columns[0]: "city"})
    
    
    df = df.iloc[:, :-1]

    if 'total' in df.columns:
        df = df.drop(['total'], axis=1)
    
    age_groups = ['under_19', '20-29', '30-39', '40-49', '50-59', '60-69', '70-79', 'over_80']
    if len(df.columns) - 1 == len(age_groups):
        df.columns = ["city"] + age_groups
    else:
        print(f"Warning: Age group column number mismatch, expected {len(age_groups)} columns, actual {len(df.columns) - 1} columns")
    
    df_long = df.melt(id_vars=["city"], var_name="age_group", value_name="application")
    df_long = df_long[~df_long["city"].isin(["計", "外務省", "合計"])]
    df_long = df_long.dropna(subset=["city", "age_group", "application"])
    df_long["city"] = df_long["city"].apply(translate_city)
    df_long = df_long[~df_long["city"].str.contains("小計", na=False)]
    df_long["application"] = pd.to_numeric(df_long["application"], errors="coerce")
    df_long = df_long.dropna(subset=["application"])
    
    df_long.insert(0, 'year', year)

    df_long = df_long.sort_values(["year", "city", "age_group"])
    
    return df_long

def general_passport_amount(file_path):
    year = os.path.basename(file_path).split('.')[0]
    excel_file = pd.ExcelFile(file_path)
    target_sheet_name = '有効旅券'
    sheet_name = find_closest_sheet(excel_file, target_sheet_name)
    
    if not sheet_name:
        target_sheet_name = '一般旅券有効旅券数'
        sheet_name = find_closest_sheet(excel_file, target_sheet_name)
    
    print(file_path)
    print(sheet_name)
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)  # 不使用第一行作為列名

    df = df.iloc[1:].reset_index(drop=True)

    # 檢查列數是否匹配
    expected_columns = ['city', 'na1', 'na2', '5_years', '10_years', 'total']
    if len(df.columns) >= len(expected_columns):
        df.columns = expected_columns + df.columns[len(expected_columns):].tolist()
    else:
        print(f"Warning: Column number mismatch, expected at least {len(expected_columns)} columns, actual {len(df.columns)} columns")
        return None

    df = df[df['city'] == '合計']
    df = df.drop(columns=['city','na1', 'na2', '5_years', '10_years'])

    df.insert(0, 'year', year)
    df = df[['year', 'total']]
    print(df.columns)
        
    return df

# ------------------------------------------------------------
# check folder and file

folder_path = 'raw'  
# print(f"foler path: {os.path.abspath(folder_path)}")

excel_files = glob.glob(os.path.join(folder_path, '*.xlsx'))
# print(f"test_Found the Excel files:\n{'\n'.join(excel_files)}")

if not excel_files:
    print("Can't find any excel file.")
else:
    print(f"Found the Excel files:\n{'\n'.join(excel_files)}")

# ------------------------------------------------------------
# category

category_all_data = []
for file in excel_files:
    category_df = category_clean(file)
    if category_df is not None and not category_df.empty:
        category_all_data.append(category_df)

if category_all_data:
    combined_category_df = pd.concat(category_all_data, ignore_index=True)
combined_category_df = combined_category_df.sort_values(['year', 'month'], ascending=[False, False])

print(combined_category_df)
# Save data to the parent directory
parent_directory = os.path.dirname(folder_path)
csv_output_path = os.path.join(parent_directory, 'data/category.csv')
combined_category_df.to_csv(csv_output_path, index=False, encoding='utf-8-sig')
print(f"save as: {csv_output_path}")

# ------------------------------------------------------------
# age

age_all_data = []
for file in excel_files:
    age_df = age_clean(file)
    if age_df is not None and not age_df.empty:
        age_all_data.append(age_df)

if age_all_data:
    combined_age_df = pd.concat(age_all_data, ignore_index=True)
combined_age_df = combined_age_df.sort_values(['year', 'month'], ascending=[False, False])

# print(combined_age_df)
parent_directory = os.path.dirname(folder_path)
csv_output_path = os.path.join(parent_directory, 'data/age.csv')
combined_age_df.to_csv(csv_output_path, index=False, encoding='utf-8-sig')
print(f"save as: {csv_output_path}")

# ------------------------------------------------------------
# gender

gender_all_data = []
for file in excel_files:
    gender_df = gender_clean(file)
    if gender_df is not None and not gender_df.empty:
        gender_all_data.append(gender_df)

if gender_all_data:
    combined_gender_df = pd.concat(gender_all_data, ignore_index=True)
combined_gender_df = combined_gender_df.sort_values(['year', 'month'], ascending=[False, False])

# print(combined_gender_df)
parent_directory = os.path.dirname(folder_path)
csv_output_path = os.path.join(parent_directory, 'data/gender.csv')
combined_gender_df.to_csv(csv_output_path, index=False, encoding='utf-8-sig')
print(f"save as: {csv_output_path}")

# ------------------------------------------------------------
# city

city_all_data = []
for file in excel_files:
    city_df = city_clean(file)
    if city_df is not None and not city_df.empty:
        city_all_data.append(city_df)

if city_all_data:
    combined_city_df = pd.concat(city_all_data, ignore_index=True)
    combined_city_df = combined_city_df.sort_values(['year', 'month'], ascending=[False, False])

    print(combined_city_df)
    parent_directory = os.path.dirname(folder_path)
    csv_output_path = os.path.join(parent_directory, 'data/city.csv')
    combined_city_df.to_csv(csv_output_path, index=False, encoding='utf-8-sig')
    print(f"save as: {csv_output_path}")
else:
    print("No valid city data to process.")

# ------------------------------------------------------------
# age_city

age_city_all_data = []
for file in excel_files:
    age_city_df = age_city_clean(file)
    if age_city_df is not None and not age_city_df.empty:
        age_city_all_data.append(age_city_df)

if age_city_all_data:
    combined_age_city_df = pd.concat(age_city_all_data, ignore_index=True)
    combined_age_city_df = combined_age_city_df.sort_values(['year', 'city'], ascending=[False, False])

    print(combined_age_city_df)
    parent_directory = os.path.dirname(folder_path)
    csv_output_path = os.path.join(parent_directory, 'data/age_city.csv')
    combined_age_city_df.to_csv(csv_output_path, index=False, encoding='utf-8-sig')
    print(f"save as: {csv_output_path}")
else:
    print("No valid age & city data to process.")

# ------------------------------------------------------------
# general_passport_amount

general_passport_all_data = []
for file in excel_files:
    general_passport_df = general_passport_amount(file)
    if general_passport_df is not None and not general_passport_df.empty:
        general_passport_all_data.append(general_passport_df)

if general_passport_all_data:
    combined_general_passport_df = pd.concat(general_passport_all_data, ignore_index=True)
    combined_general_passport_df = combined_general_passport_df.sort_values(['year'], ascending=[False])


    print(combined_general_passport_df)
    parent_directory = os.path.dirname(folder_path)
    csv_output_path = os.path.join(parent_directory, 'data/general_passport.csv')
    combined_general_passport_df.to_csv(csv_output_path, index=False, encoding='utf-8-sig')
    print(f"save as: {csv_output_path}")
else:
    print("No valid general passport data to process.")