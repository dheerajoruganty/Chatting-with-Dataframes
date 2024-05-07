from dotenv import load_dotenv

load_dotenv()
import os
import google.generativeai as genai
from openai import OpenAI
import polars as pl
import streamlit as st
import duckdb


def gemini_setup():
    """
    Initializes Google's API endpoint for Gemini Access by configuring the API key and listing supported models.
    """
    api_key = os.getenv("API_KEY")
    genai.configure(api_key=api_key)

    try:
        for m in genai.list_models():
            if "generateContent" in m.supported_generation_methods:
                print(m.name)
    except Exception:
        raise Exception("Please check your API key")


def openai_setup():
    """
    Initializes OpenAI's API endpoint for GPT-4 Access and returns an OpenAI client instance.
    """
    client = OpenAI(api_key=os.environ.get("OpenAI"))
    return client


def pl_loadLazy(data_path, response_message):
    """
    Loads a Polars dataframe lazily from a given path and executes an SQL query using Polars' SQL context.

    Args:
        data_path (str): Path where the dataset is located.
        response_message (str): SQL query to be executed.

    Returns:
        pl.DataFrame: Resulting dataframe after executing the query.
    """
    NYCTLC = pl.read_parquet(data_path).lazy()
    with pl.SQLContext(register_globals=True) as NYCTLC:
        res = NYCTLC.execute(response_message + ";").collect()

    return res


def execute_sql_query(data_path, query, df_name):
    """
    Executes an SQL query on a Polars dataframe using DuckDB, given a path to a dataset.

    Args:
        data_path (str): Path where the dataset is located.
        query (str): SQL query to be executed.
        df_name (str): Name of the dataframe to be used as an alias in the SQL context.

    Returns:
        pl.DataFrame: Resulting dataframe after executing the query.
    """
    # Load the dataset with Polars
    df = pl.read_parquet(data_path)
    # Initialize a DuckDB connection
    con = duckdb.connect()
    # Register the Polars DataFrame as a view within DuckDB, using df_name as the alias in the SQL context
    con.register(df_name, df)
    # Execute the query and fetch results as an Arrow table
    arrow_table = con.execute(query).fetch_arrow_table()
    # Convert Arrow Table to Polars DataFrame
    result = pl.from_arrow(arrow_table)
    # Close the connection
    con.close()

    return result
