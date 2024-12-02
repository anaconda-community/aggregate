import logging
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pytest
from PIL import Image

logger = logging.getLogger(__name__)


@pytest.mark.pandas
def test_pandas_series():
    """
    To validate pandas series functionality
    Document to refer the use case:
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.Series.html
    """
    # Declare Series Data Frame
    s_df = pd.Series([1, 3, 5, np.nan, 6, 8])
    # assert that the Series Data Frame at index 4 is the expected value
    assert s_df.iloc[4] == 6.0, f"failed to validate the series data frame value {s_df}"


@pytest.mark.pandas
def test_pandas_operations():
    """
    test case to validate the selection by column functionality
    Document to refer the use case:
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
    """
    # Declare Series Data Frame
    df = pd.DataFrame(
        {
            "name": ["TeamA", "TeamB", "TeamC"],
            "date_of_birth": ["27/05/2001", "16/02/2011", "25/09/2021"],
        }
    )[["name", "date_of_birth"]]
    # Assert that the data frame is configured as expected
    assert (
        df["date_of_birth"].iloc[0] == "27/05/2001"
    ), "Failed to create the name DOB data frame  {}".format(df["date_of_birth"].iloc[0])
    df["date_of_birth"] = pd.to_datetime(df["date_of_birth"], format="%d/%m/%Y")
    df["date_of_birth"] = df["date_of_birth"].dt.date
    try:
        pd.to_datetime(df["date_of_birth"], format="%Y-%m-%d", errors="raise")
        logging.info("Successfully validate pandas operations methods.")
    except ValueError as error:
        logging.debug(f"PANDAS operation Validation failed and error message is {error}")


@pytest.mark.numpy
def test_create_df_validate_df_column_data():
    """
    validate the column values from the dataframe.
    Document to refer the use case:
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html
    """
    data = [["numpy", True], ["pandas", True], ["matplotlib", True]]
    # Create the pandas DataFrame
    df = pd.DataFrame(data, columns=["Package_name", "is_updated"])
    # grab is_updated column data
    is_updated_data = df["is_updated"].to_numpy()
    # validate all the data in is_updated column is same.
    assert (is_updated_data[0] == is_updated_data).all(
        0
    ), " Failed to validate the is_updated column and the actual column output is {}".format(
        df["is_updated"]
    )


@pytest.mark.matplotlib
def test_pd_csv_and_matplotlib():
    """
    To get the data from  csv and create a DF and plot the dat and validate the plotted data.
    Document to refer the use case:
    https://pandas.pydata.org/docs/user_guide/io.html#csv-text-files
    """
    test_file_folder = os.path.dirname(os.path.realpath(__file__))
    dataframe = pd.read_csv(
        test_file_folder + "/test_data/packages_test_data.csv"
    )  # declare dataframe
    x = dataframe.No_Of_Downloads > 10000
    y = dataframe.Product_Name
    fig, ax = plt.subplots(nrows=1, ncols=1)  # create figure & 1 axis
    ax.plot(x, y)
    fig.savefig("to.png")  # save the figure to file
    plt.close(fig)  # close the plot figure
    # assertions
    file_name = "to.png"
    try:
        im = Image.open(file_name)
        assert im.format.lower() == "png", "unable to assert the plotted data"
    except OSError as message:
        logging.debug(f"Error being raised {message}")
