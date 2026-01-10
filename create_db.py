import pandas as pd
import sqlite3
import os

data_path = "Dataset"

db="ecommerce.db"
if os.path.exists(db):
    os.remove(db)

conn = sqlite3.connect(db)

def load(name):
    df = pd.read_csv(f"{data_path}/{name}")

    table_name = name.replace("olist", "").replace("_dataset", "").replace(".csv", "")


    # storing df into sql
    df.to_sql(table_name, conn, index=False, if_exists="replace")


# customers_data = pd.read_csv("Dataset/olist_customers_dataset.csv")

# # print(customers_data.head())

# geo_location_data = pd.read_csv("Dataset/olist_geolocation_dataset.csv")


# order_items_data = pd.read_csv("Dataset/olist_order_items_dataset.csv")

# order_payments_data = pd.read_csv("Dataset/olist_order_payments_dataset.csv")

# order_reviews_data = pd.read_csv("Dataset/olist_order_reviews_dataset.csv")

# orders_data = pd.read_csv("Dataset/olist_orders_dataset.csv")

# products_data = pd.read_csv("Dataset/olist_products_dataset.csv")

# sellers_data = pd.read_csv("Dataset/olist_sellers_dataset.csv")

# category_translation = pd.read_csv("Dataset/product_category_name_translation.csv")



# Load all datasets
load("olist_customers_dataset.csv")
load("olist_orders_dataset.csv")
load("olist_order_items_dataset.csv")
load("olist_order_payments_dataset.csv")
load("olist_order_reviews_dataset.csv")
load("olist_products_dataset.csv")
load("olist_sellers_dataset.csv")
load("olist_geolocation_dataset.csv")
load("product_category_name_translation.csv")

conn.close()
print(f"\nDatabase created: {db}")