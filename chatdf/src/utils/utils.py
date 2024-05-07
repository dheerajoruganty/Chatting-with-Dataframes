from dotenv import load_dotenv
import os
import google.generativeai as genai
from openai import OpenAI
import polars as pl
import duckdb

load_dotenv()

class GeminiAPI:
    """
    Class to handle operations related to Google's Gemini API.
    """
    def __init__(self):
        """
        Initializes Google's API endpoint for Gemini Access by configuring the API key and listing supported models.
        """
        self.api_key = os.getenv("API_KEY")
        genai.configure(api_key=self.api_key)
        self.models = self.list_supported_models()

    def list_supported_models(self):
        """
        List models that support content generation.
        """
        try:
            return [m for m in genai.list_models() if "generateContent" in m.supported_generation_methods]
        except Exception:
            raise Exception("Please check your API key")

    def print_models(self):
        """
        Prints the names of models supporting content generation.
        """
        for model in self.models:
            print(model.name)


class OpenAIAPI:
    """
    Class to handle operations related to OpenAI's GPT.
    """
    def __init__(self):
        """
        Initializes OpenAI's API endpoint for GPT-4 Access and returns an OpenAI client instance.
        """
        self.api_key = os.getenv("OpenAI")
        self.client = OpenAI(api_key=self.api_key)

    def get_client(self):
        """
        Returns the OpenAI client.
        """
        return self.client


class PolarsSQL:
    """
    Class to handle operations with Polars and SQL queries.
    """
    @staticmethod
    def load_lazy(data_path, response_message):
        """
        Loads a Polars dataframe lazily from a given path and executes an SQL query using Polars' SQL context.

        Args:
            data_path (str): Path where the dataset is located.
            response_message (str): SQL query to be executed.

        Returns:
            pl.DataFrame: Resulting dataframe after executing the query.
        """
        nyctlc = pl.read_parquet(data_path).lazy()
        with pl.SQLContext(register_globals=True) as nyctlc:
            res = nyctlc.execute(response_message + ";").collect()

        return res

    @staticmethod
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
        df = pl.read_parquet(data_path)
        con = duckdb.connect()
        con.register(df_name, df)
        arrow_table = con.execute(query).fetch_arrow_table()
        result = pl.from_arrow(arrow_table)
        con.close()

        return result
