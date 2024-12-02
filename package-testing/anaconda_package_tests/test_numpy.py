import os

import numpy as np
import pytest
#from scipy import sparse

from .utils.validations import Assertions


@pytest.mark.numpy
def test_numpy_array():
    """
    test to validate the numpy array
    Document to refer the use case:
    https://numpy.org/doc/stable/reference/generated/numpy.array.html
    """
    # declare arrays
    unique_matrix = np.eye(6)
    unique_matrix_2 = np.eye(6)
    # assert that the arrays are equal
    obj = Assertions(actual=unique_matrix, desired=unique_matrix_2)
    obj.arrays_assert_equal()


@pytest.mark.numpy
def test_quality_of_product():
    """
    Using numpy package  to get the quality of the product from
    product data in a csv file.
    Document to refer the use case:
    https://numpy.org/doc/stable/reference/generated/numpy.array.html
    """
    # All the above code can be achieved by numpuy getfromtxt function
    test_file_folder = os.path.dirname(os.path.realpath(__file__))
    wines = np.genfromtxt(
        test_file_folder + "/test_data/product_quality.csv", delimiter=";", skip_header=1
    )
    int_wines = wines.astype(np.int32)
    # get the last column of the csv or quality column of the csv
    quality_Array = int_wines[:, 11]
    max_ = max(quality_Array)
    high_quality = wines[:, 11] >= max_
    data = wines[high_quality, :][:3, :]
    # assert to determine the highest quality product
    assert len(data) == 2, f"unable to determine the highest quality product {data}"


#@pytest.mark.scipy
#def test_numpy_scipy_pkgs():
#    """
#    Create a 2D numpy array with ones and zeros.
#    And create a matrix out of numpy array and validate the
#    matrix with all ones.
#    Document to refer the use case:
#    https://docs.scipy.org/doc/scipy-1.8.0/html-scipyorg/reference/sparse.html
#    """
#    # declare the matrix
#    eye = np.eye(3)
#    sparse_matrix = sparse.csr_matrix(eye)
#    # assert that the matrix was created properly
#    assert sparse_matrix is not None, "matrix created is None"
