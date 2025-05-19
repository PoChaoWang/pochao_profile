from sqlalchemy import create_engine, inspect, text
import psycopg2
import os
import pandas as pd
from datetime import datetime
import glob

class ETLPipeline:
    def __init__(self, dest_conn_string):
        self.dest_engine = create_engine(dest_conn_string)

        self.table_configs = {
            'ga': {
                'table_name': 'ga_data',
                'schema': '''
                    day DATE NOT NULL,
                    utm_source VARCHAR(255) NOT NULL,
                    utm_medium VARCHAR(255) NOT NULL,
                    utm_campaign VARCHAR(255) NOT NULL,
                    utm_content VARCHAR(255) NOT NULL,
                    total_users INT,
                    first_time_purchasers INT,	
                    new_users INT,	
                    bounce_rate DECIMAL,	
                    sessions INT,	
                    engaged_sessions INT,	
                    purchase_revenue DECIMAL,	
                    purchases INT,
                    PRIMARY KEY (day, utm_source, utm_medium, utm_campaign, utm_content)
                ''',
                "primary_keys": ["day", "utm_source", "utm_medium", "utm_campaign", "utm_content"],
                "update_columns": ["total_users", "first_time_purchasers", "new_users", "bounce_rate", "sessions", "engaged_sessions", "purchase_revenue", "purchases"]
            },
            'facebook': {
                'table_name': 'facebook_data',
                'schema': '''
                    day DATE NOT NULL,
                    campaign VARCHAR(255) NOT NULL,
                    adgroup VARCHAR(255) NOT NULL,
                    impressions INT,
                    clicks INT,
                    cost DECIMAL,
                    PRIMARY KEY (day, campaign, adgroup)
                ''',
                "primary_keys": ["day", "campaign", "adgroup"],
                "update_columns": ["impressions", "clicks", "cost"]
            },
            'google': {
                'table_name': 'google_data',
                'schema': '''
                    day DATE NOT NULL,
                    campaign VARCHAR(255) NOT NULL,
                    adgroup VARCHAR(255) NOT NULL,
                    impressions INT,
                    clicks INT,
                    cost DECIMAL,
                    PRIMARY KEY (day, campaign, adgroup)
                ''',
                "primary_keys": ["day", "campaign", "adgroup"],
                "update_columns": ["impressions", "clicks", "cost"]
            },
            'yahoo': {
                'table_name': 'yahoo_data',
                'schema': '''
                    day DATE NOT NULL,
                    campaign VARCHAR(255) NOT NULL,
                    adgroup VARCHAR(255) NOT NULL,
                    impressions INT,
                    clicks INT,
                    cost DECIMAL,
                    PRIMARY KEY (day, campaign, adgroup)
                ''',
                "primary_keys": ["day", "campaign", "adgroup"],
                "update_columns": ["impressions", "clicks", "cost"]
            },
            'criteo': {
                'table_name': 'criteo_data',
                'schema': '''
                    day DATE NOT NULL,
                    campaign VARCHAR(255),
                    adgroup VARCHAR(255),
                    impressions INT,
                    clicks INT,
                    cost DECIMAL,
                    PRIMARY KEY (day, campaign, adgroup)
                ''',
                "primary_keys": ["day", "campaign", "adgroup"],
                "update_columns": ["impressions", "clicks", "cost"]
            }
        }

    def initialize_tables(self, db_params):
        conn = None
        cur = None
        try:
            conn = psycopg2.connect(**db_params)
            cur = conn.cursor()
            
            existing_tables = inspect(self.dest_engine).get_table_names()
            
            for config in self.table_configs.values():
                table_name = config['table_name']
                if table_name not in existing_tables:
                    create_table_query = f'''
                        CREATE TABLE {table_name} (
                            {config['schema']}
                        )
                    '''
                    cur.execute(create_table_query)
                    print(f"Table '{table_name}' created successfully.")
                else:
                    print(f"Table '{table_name}' already exists. Skipping creation.")
            
            conn.commit()

        except Exception as e:
            print(f"Error creating tables: {e}")
            if conn:
                conn.rollback()
                
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def get_csv_files(self, base_path, platform):
        path = os.path.join(base_path, platform, f'{platform}_fake_data_*.csv')
        platform_dir = os.path.join(base_path, platform)
        
        if os.path.exists(platform_dir):
            files = os.listdir(platform_dir)
            print(f"Files in directory:")
            for file in files:
                print(f"- {file}")
        
        matching_files = glob.glob(path)
        return matching_files

    def process_platform_data(self, files, platform):
        all_data = []
        
        for file in files:
            df = pd.read_csv(file, parse_dates=['day'])
            all_data.append(df)
            
        if not all_data:
            return None
            
        combined_df = pd.concat(all_data, ignore_index=True)
        
        if platform == 'ga':
            combined_df = combined_df.drop_duplicates(
                subset=['day', 'utm_source', 'utm_medium', 'utm_campaign', 'utm_content']
            )
        else:
            combined_df = combined_df.drop_duplicates(
                subset=['day', 'campaign', 'adgroup']
            )
            
        return combined_df

    def load_to_database(self, df, table_name, primary_keys, update_columns):
        try:
            temp_table = f"temp_{table_name}"
            df.to_sql(temp_table, self.dest_engine, if_exists='replace', index=False)
            
            primary_key_str = ", ".join(primary_keys)
            update_columns_str = ", ".join([f"{col} = EXCLUDED.{col}" for col in update_columns])
            
        
            with self.dest_engine.begin() as conn:
                sql = f"""
                    INSERT INTO {table_name}
                    SELECT * FROM {temp_table}
                    ON CONFLICT ({primary_key_str})
                    DO UPDATE SET
                        {update_columns_str}
                """ 
                conn.execute(text(sql))
                
                conn.execute(text(f"DROP TABLE {temp_table}"))
    
        except Exception as e:
            print(f"Error loading data to {table_name}: {e}")

    def run_etl_pipeline(self, base_path):
        for platform in self.table_configs.keys():
            print(f"\nProcessing {platform} data...")
            print(f"Looking for files in path: {os.path.join(base_path, platform, f'{platform}_fake_data_*.csv')}")
            csv_files = self.get_csv_files(base_path, platform)
            if not csv_files:
                print(f"No CSV files found for {platform}")
                continue
                
            processed_data = self.process_platform_data(csv_files, platform)
            if processed_data is None:
                print(f"No data to process for {platform}")
                continue
                
            table_config = self.table_configs[platform]
            table_name = table_config['table_name']
            primary_keys = table_config.get('primary_keys', [])
            update_columns = table_config.get('update_columns', [])
            if not primary_keys or not update_columns:
                print(f"Missing primary_keys or update_columns configuration for {platform}")
                continue
            try:
                self.load_to_database(processed_data, table_name, primary_keys, update_columns)
                print(f"Data successfully loaded into {table_name}")
            except Exception as e:
                print(f"Error loading data for {platform}: {e}")

def main():
    # dest_conn = "postgresql://postgres:password@destination_postgres:5432/destination_db"
    db_params = {
        'host': 'host.docker.internal',
        'database': 'destination_db',
        'user': 'postgres',
        'password': 'password',
        'port': '5434'
    }
    dest_conn = f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['database']}"
    
    pipeline = ETLPipeline(dest_conn)
    pipeline.initialize_tables(db_params)
    base_path = 'raw-data'
    pipeline.run_etl_pipeline(base_path)

if __name__ == "__main__":
    main()
