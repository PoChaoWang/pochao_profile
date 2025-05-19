# Ad Performance Data Pipeline

## Project Introduction

This project is my first attempt at implementing data flow and automation. To avoid wasting your time, I put project background at the end.

Since the advertising platform APIs require company information and this project is purely personal, I was unable to integrate the APIs of major advertising platforms. All the data used in this project is simulated data created using Chat GPT.

### This project is an advertising performance data processing pipeline, with its main functions including:

1. Use Python to merge CSV files from a specified folder and remove duplicates.
2. Insert the processed data into a PostgreSQL database.
3. Use dbt in the staging layer to modify column names, and generate a combined file in the marts layer.
4. Schedule daily updates with Airflow.
5. Package Airflow into Docker.

![image](https://github.com/PoChaoWang/Ad_Performance_Data_Pipeline/blob/main/images/process.png)

### Project Objective:

- Reduce the time cost of manual data processing.
- Conduct cross-platform performance comparison and analysis.
- Optimize advertising placement strategies.

### Technical Architecture:

- Programming Language: Python 3.9.6
- Data Processing: Pandas
- Data Storage: PostgreSQL, SQLAlchemy
- Database Connection: psycopg2
- File Handling: os, glob
- Time Management: datetime
- Scheduling Tool: Apache Airflow
- Containerization and Deployment: Docker 27.4.0

## Installation Instructions:

### Installing Docker

If Docker is not installed on your system, follow the steps below to install it:
**For Linux**

1. Update your package list:

```
sudo apt update
```

2. Install Docker using the package manager:

```
sudo apt install docker.io
```

3. Verify the installation:

```
docker --version
```

**For Mac**

1. Download Docker Desktop for Mac from the [Docker Docs](https://docs.docker.com/desktop/setup/install/mac-install/).
2. Open the downloaded .dmg file and follow the installation instructions.
3. Start Docker Desktop and verify the installation by running:

```
docker --version
```

**For Window**

1. Download Docker Desktop for Windows from the [Docker Docs](<[https://docs.docker.com/desktop/setup/install/mac-install/](https://docs.docker.com/desktop/setup/install/windows-install/)>).
2. Open the downloaded .dmg file and follow the installation instructions.
3. Start Docker Desktop and verify the installation by running:

```
docker --version
```

### ETL Script

The file path: etl/etl_script.py

**1. Database Connection Configuration**
Please modify the following database connection parameters in the `def main()` function based on your actual database settings:

```
db_params = {
        'host': 'host.docker.internal  ',
        'database': 'destination_db',
        'user': 'postgres',
        'password': 'password',
        'port': '5434'
    }
```

**2. Data File Path Structure**
The experimental data for this project is stored in the following structure, for example: raw-dat/ga/ga_fake_data_20241221.csv

```
raw-data/
    ├── ga/
    │   └── ga_fake_data_*.csv
    ├── facebook/
    │   └── facebook_fake_data_*.csv
    ├── google/
    │   └── google_fake_data_*.csv
    ├── yahoo/
    │   └── yahoo_fake_data_*.csv
    └── criteo/
        └── criteo_fake_data_*.csv
```

It is recommended not to modify the structure after "platform", only change the base_path in the `def main()` function.

```
base_path = 'raw-data'
```

**3. Custom CSV Format**

- In the `def __init__(self, dest_conn_string)` method, you can add your own data to the table_configs.

```
'new_platform': {
    'table_name': 'new_platform_data',
    'schema': '''
        your_custom_schema_here
    ''',
    "primary_keys": ["your_primary_keys"],
    "update_columns": ["your_update_columns"]
}
```

- Ensure that your CSV file is placed in the correct directory:

```
raw-data/
    └── new_platform/
        └── new_platform_fake_data_*.csv
```

- Because most of the test files use date, campaign, and ad group as the primary key, if there are special requirements, please use `else if` in the `def process_platform_data(self, files, platform)` method.

```
        if platform == 'ga':
            combined_df = combined_df.drop_duplicates(
                subset=['day', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content']
            )
        else if plaform == 'new platform'
            combined_df = combined_df.drop_duplicates(
                subset=['your column']
            )
        else:
            combined_df = combined_df.drop_duplicates(
                subset=['day', 'campaign', 'adgroup']
            )
```

### DBT

**1. custom_ad_data**
If you have already installed dbt core, please add the relevant settings for the `custom_ad_data` project in the `.dbt/profiles.yml` file as follows:

```
custom_ad_data:
  outputs:
    dev:
      dbname: destination_db
      host: host.docker.internal
      pass: password
      port: 5434
      schema: platform_data
      threads: 1
      type: postgres
      user: postgres
  target: dev
```

If you haven't installed dbt core yet, please use the following command to install it:

```
pip install dbt-core
```

**2. Staging**
If you have custom CSV data that you are loading into a database, you can add its information to the `source.yml` file in the `staging` folder of your dbt project. Here's an example of how to do this:

```
- name: new_table
description: "Your csv data"
```

Then, you need to clean up and organize the data in the `stg_yourData.sql` file. This file is responsible for transforming the raw data (from your CSV or other sources) into a standardized format, so it can be used effectively in the rest of your dbt models.

```
WITH source AS (
    SELECT
        *
    FROM
        {{ source(
            'destination_db',
            'your_csv_data'
        ) }}
),
renamed AS (
    SELECT
        *
    FROM
        source
)
SELECT
    *
FROM
    renamed
```

In the `schema.yml` file, you can define the metadata for your new data tables, as well as set up tests for specific fields. Here's an example of how to do both:

```
  - name: stg_yourData
    description: "Your new data"
    columns:
      - name: day
        description: "Date the data was driven"
        tests:
          - not_null
      - name: campaign
        description: "Campaign information"
        tests:
          - not_null
      - name: adgroup
        description: "Ad group information"
        tests:
          - not_null
      - name: impressions
        description: "Impressions"
      - name: clicks
        description: "Clicks"
      - name: cost
        description: "Cost"
    tests:
      - unique:
          combination:
            - day
            - campaign
            - adgroup
```

**2. Marts**
The purpose of `marts` is for tables that require merging and additional calculations. They will ultimately be presented in PostgreSQL for direct use by users.

### Airflow

You need to insert the absolute path of your own `custom_ad_data` folder in task2 of the `elt_dag.py` file.

```
Mount(source='/Users/pochaowang/Documents/Profile/ad_performance_data_pipeline/custom_ad_data', target='/dbt', type='bind')
```

Additionally, you also need to insert the absolute path of the `.dbt` directory.

```
Mount(source='/Users/pochaowang/.dbt',target='/root',type='bind')
```

### Docker

Once the above tools are set up, you can use the following command in the terminal within the main directory:

```
docker-compose up
```

## Project Background

The purpose of this project was simply to learn how to implement data automation. When I first started working at a digital marketing agency, I spent a lot of time downloading and organizing data in order to create reports. At that time, I wanted to automate the tasks I had, but I didn't know how to proceed. It wasn't until I moved to another agency that I was exposed to some knowledge, which helped me understand how to achieve the goal I had back then. This also pushed me further toward developing skills in data engineering, which led to the birth of this project. I anticipate that others will face many challenges when using this project, so I’m very open to feedback and would greatly appreciate any suggestions.
