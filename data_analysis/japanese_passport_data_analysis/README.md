# Japanese Passport Data
Data analysis on the background that not many Japanese hold passports
## [Tableau Dashboard](https://public.tableau.com/views/JapanPassport/RateofJapanpeoplewhoholdthepassport?:language=zh-CN&publish=yes&:sid=&:redirect=auth&:display_count=n&:origin=viz_share_link) 

# Library
Please make sure you have installed the library below.
## pandas
`pip3 install pandas`
## request
`pip3 install requests`
## dotenv
`pip3 install python-dotenv`

# Data
## Passport
The passport releases were downloaded from **https://www.mofa.go.jp/mofaj/toko/tokei/passport/index.html**. You can find the raw data that the name is 20xx.xlsx and the data after cleaning were saved in the data folder.
### age_city.csv
This is the number of passport applications by age group in each city.
### age.csv
This is the number of passport applications by age group.
### category.csv
This is the number of passport applications by category.
### city.csv
This is the number of passport applications by city.
### gender.csv
This is the number of passport applications by gender.
### general_passport.csv
Number of valid general passports.

## Population
The data was obtained by API. I will explain how to connect it below. 
The data was saved in the raw with the 'japan_population_data_xxxxxxxx' file name and saved the cleaning data in the data with the 'japan_population_data.csv' and 'japan_population_yoy.csv'.
### japan_population_data.csv
This is the number of population by age group.
### japan_population_yoy.csv
Total population per year.

## Exchange rate
The exchange rate data was downloaded in the [yahoo finance](https://finance.yahoo.com/).

# API
The code uses the [**E-Stat**](https://e-stat.go.jp/en) API to request the population data. If you want to use the API, you should sign up and create the API key, and save the key in the .env file.
## How do you set up the API key in E-Stat?
1. After you sign up, you can go to **my page** and **API function (application ID issuance)**
  ![截圖 2024-09-03 下午4 06 33](https://github.com/user-attachments/assets/5f11f6c4-e386-47fd-95c3-db99cca6cfee)

2. Naming the API name and fill in the URL of the application or http://test.localhost/.
  ![截圖 2024-09-03 下午4 12 34](https://github.com/user-attachments/assets/2cdec7e9-3899-42e4-b459-c4e719e84bc6)

# Code
## japan_population_api_request.py
This Python script fetches population statistics data from the Japanese government's e-Stat API and saves it as CSV files.

### Features

- Retrieves multiple statistical datasets using the e-Stat API
- Parses API responses into pandas DataFrames
- Saves data as CSV files
- Handles different CSV delimiters (comma and tab)
- Prints API response and data previews

### Notes

- Ensure you have a valid e-Stat API key
- The script fetches three statistical datasets by default; you can modify the `stats_data_ids` list as needed
- If data parsing issues occur, the script attempts to use different delimiters

### Output

The script creates a CSV file for each successful API request in the format:
`raw/japan_population_raw_{stats_data_id}.csv`

## japan_population_data_clean.py
This Python script processes and cleans Japanese population statistics data.

### Features

- Reads raw population data from multiple CSV files
- Cleans and standardizes data format
- Reclassifies age groups into broader categories
- Merges data from different files
- Detects and reports duplicate data
- Saves processed data as a new CSV file

### Usage

1. Ensure raw CSV files are in the `raw` directory
2. Run the script:
   ```
   python japan_population_data_clean.py
   ```
3. Processed data will be saved in `data/japan_population_data.csv`

### Data Format

The output CSV file contains the following columns:
- year: Year
- month: Month
- gender: Gender (male/female)
- age: Age group (under_19, 20-29, 30-39, 40-49, 50-59, 60-69, 70-79, over_80)
- value: Population count

### Notes

- The script automatically handles slight differences in column names
- Duplicate data is detected and reported
- Ensure the pandas library is installed in your Python environment

## japan_population_yoy.py
### Overview
This Python script processes and cleans Japanese population statistics data. It reads data from multiple CSV files, cleans and merges the information, then outputs a single CSV file containing annual total population data.

### Features
- Reads population data from multiple CSV files
- Cleans data, keeping only total population figures (combined male and female)
- For non-2023 data, retains only December data; for 2023, keeps October data
- Converts population values from thousands to individual units
- Excludes data prior to 2014
- Merges all processed data into a single CSV file

### Usage
1. Ensure input files are located in the `raw` directory
2. Run the script:
   ```
   python japan_population_yoy.py
   ```
3. Processed data will be saved in `japan_population_yoy.csv` file in the `data` directory

### Input Files
The script processes the following CSV files:
- japan_population_data_0003459019.csv
- japan_population_data_0003448229.csv
- japan_population_data_0004008041.csv

### Output
The script generates a file named `japan_population_yoy.csv` containing the processed annual population data.

### Notes
- Ensure input files are in the correct format with required column names
- The script assumes specific structure and naming conventions for input data

## passport_release_data_clean.py
This Python script processes and cleans data related to Japanese passport issuance. It extracts various types of passport data from Excel files and converts them into structured CSV format.

### Features

The script can process the following types of data:

1. Passport category data
2. Age group data
3. Gender data
4. City data
5. Age and city combination data
6. Total valid passport data

### Usage

1. Place the raw Excel files in a folder named 'raw'.
2. Run the script.
3. Processed CSV files will be saved in the 'data' folder.

### Output

The script will generate the following CSV files:

- category.csv
- age.csv
- gender.csv
- city.csv
- age_city.csv
- general_passport.csv

### Notes

- The script uses fuzzy matching to find relevant sheets in Excel files.
- For city names, the script converts Japanese names to English.
- The script will output warning messages if the data format doesn't match expectations.
