import csv
import os

import matplotlib.pyplot as plt
import pytest

from .utils.user_cases import Cases

__author__ = "Maxwell Varlack"
__version__ = "0.0.1"


@pytest.mark.scipy
def get_csv_data(file_name):
    """
    test the csv file
    """
    test_file_folder = os.path.dirname(os.path.realpath(__file__))
    with open(test_file_folder + "/test_data/" + file_name) as csv_file:
        csv_reader = csv.reader(csv_file)
        fields = list(csv_reader)  # convert the csv reader object to a list
    assert len(fields) > 1, "There is an issue reading the CSV File"
    return fields


@pytest.mark.scipy
def test_generate_data():
    """
    This function generates actual values of position,
    velocity, and acceleration using scipy package
    Notice that the image must be generated in order for the tests to pass
    Document to refer the use case:
    https://github.com/qxresearch/Simple-Harmonic-Motion
    """
    # validate that the generate data method is the harmonic motion class is working as intended
    motion = Cases()
    result = motion.generate_data()
    # gather data
    generated_data = list(motion.generate_data())
    expected_data = get_csv_data("harmonic_motion_data.csv")
    # declare variables
    img_gen_time = []
    img_gen_position = []
    img_gen_velocity = []
    img_gen_acceleration = []
    img_exp_time = []
    img_exp_position = []
    img_exp_velocity = []
    img_exp_acceleration = []

    # prepare data
    # generated data
    for line in generated_data:
        img_gen_time.append(line[0])
        img_gen_position.append(line[1])
        img_gen_velocity.append(line[2])
        img_gen_acceleration.append(line[3])

    # expected data (get values from the csv file data skip heather and convert to floats)
    for i in range(1, len(expected_data)):
        line = expected_data[i]
        img_exp_time.append(float(line[0]))
        img_exp_position.append(float(line[1]))
        img_exp_velocity.append(float(line[2]))
        img_exp_acceleration.append(float(line[3]))

    # set the plot area
    plt.figure(1)
    plt.style.use("seaborn")

    fig, (fig1, fig2, fig3) = plt.subplots(nrows=3, ncols=1)

    # generate plot
    fig1.plot(img_gen_time, img_gen_position, color="#07113A", label="Generated")
    fig1.plot(img_exp_time, img_exp_position, color="#FFAAAA", linestyle="--", label="Expected")
    fig2.plot(img_gen_time, img_gen_velocity, color="k", label="Generated")
    fig2.plot(img_gen_time, img_exp_velocity, color="#7B85AD", linestyle="--", label="Expected")
    fig3.plot(img_gen_time, img_gen_acceleration, color="b", label="Generated")
    fig3.plot(img_gen_time, img_exp_acceleration, color="#8DCF8A", linestyle="--", label="Expected")

    # set the position plot
    fig1.legend()
    fig1.set_title("Time vs Position")
    fig1.set_xlabel("Time")
    fig1.set_ylabel("Position")

    # set the velocity plot
    fig2.legend()
    fig2.set_title("Time vs Velocity")
    fig2.set_xlabel("Time")
    fig2.set_ylabel("Velocity")

    # set the acceleration plot
    fig3.legend()
    fig3.set_title("Time vs Acceleration")
    fig3.set_xlabel("Time")
    fig3.set_ylabel("Acceleration")

    plt.tight_layout()

    # save the figure in the temp folder
    test_file_folder = os.path.dirname(os.path.realpath(__file__))
    fig.savefig(test_file_folder + "/harmonic_motion_plot.png")

    # assert that the data is generated properly
    assert len(result) > 1, "could not generate the data"


@pytest.mark.scipy
def test_validate_data():
    """
    This function validates actual values and expected values of position,
    velocity, and acceleration generated by scipy and using expected values
    Document to refer the use case:
    https://github.com/qxresearch/Simple-Harmonic-Motion
    """
    # test generate data
    motion = Cases()
    # gather data
    generated_data = list(motion.generate_data())
    expected_data = get_csv_data("harmonic_motion_data.csv")
    # declare variables
    generated_data_size = len(generated_data)
    maximum_difference = 1  # declare the maximum allowed percent difference
    pass_or_fail = True  # pass or fail value, if true, it passes otherwise it fails
    # declare object
    motion = Cases()

    for index in range(generated_data_size):
        expected_index = index + 1  # index to get expected data
        # get generated  and expected lines
        line_gen = generated_data[index]
        line_exp = expected_data[expected_index]
        # get generated values on each line
        generated_time = line_gen[0]
        generated_position = line_gen[1]
        generated_velocity = line_gen[2]
        generated_acceleration = line_gen[3]
        # get expected values on each line
        expected_time = line_exp[0]
        expected_position = line_exp[1]
        expected_velocity = line_exp[2]
        expected_acceleration = line_exp[3]
        # calculated percent differences
        time_diff = motion.percent_difference(generated_time, expected_time)
        position_diff = motion.percent_difference(generated_position, expected_position)
        velocity_diff = motion.percent_difference(generated_velocity, expected_velocity)
        acceleration_diff = motion.percent_difference(generated_acceleration, expected_acceleration)

        print(
            f"Difference: (Time {time_diff}% Position {position_diff}% \
                Velocity {velocity_diff}% Acceleration {acceleration_diff}% )"
        )

        # final data validation
        if (
            time_diff > maximum_difference
            or position_diff > maximum_difference
            or velocity_diff > maximum_difference
            or acceleration_diff > maximum_difference
        ):
            pass_or_fail = False

    # validate that the image was created
    test_file_folder = os.path.dirname(os.path.realpath(__file__))
    image_exists = os.path.exists(test_file_folder + "/harmonic_motion_plot.png")
    assert image_exists is True, "The Image Could Not Be Generated"
    assert pass_or_fail is True, "There Is An Issue With The Data"


@pytest.mark.scipy
def test_generate_optimization_image():
    """
    generate the image for the cost curve and optimal point
    Document to refer the use case:
    https://tutorial.math.lamar.edu/Classes/CalcI/Optimization.aspx
    """
    # Call the Optimization Class
    optimal = Cases()
    # get the data for the cost curve
    xValue, yValue = optimal.generate_x_y_values()
    # get the optimal point
    first_solution_x, first_solution_y, success_result = optimal.optimal_point()
    # generate plot
    plt.close()  # reset image
    plt.figure(2)
    plt.title("Cost Optimization Graph")
    plt.xlabel("Time")
    plt.ylabel("Cost - ($USD)")
    plt.plot(xValue, yValue, label="cost function")  # plot cost curve
    # plot the optimal point
    plt.scatter(first_solution_x, first_solution_y, color="r", label="Optimal Point")
    plt.legend()
    # save image
    test_file_folder = os.path.dirname(os.path.realpath(__file__))
    plt.savefig(test_file_folder + "/Cost_Optimization.png")
    # verify that the image was saved
    image_exists = os.path.exists(test_file_folder + "/Cost_Optimization.png")
    assert success_result is True, "could not generate image optimal point"
    assert image_exists is True, "Could not located the Cost_Optimization.png file"


@pytest.mark.scipy
def test_cost_function():
    """
    This function is used to test
    the cost function
    Document to refer the use case:
    https://tutorial.math.lamar.edu/Classes/CalcI/Optimization.aspx
    """
    # Call the Optimization Class
    optimal = Cases()
    # generate xy values for the cost curve
    xValue, yValue = optimal.generate_x_y_values()
    # get the size of the data
    generated_data_size = len(xValue)
    # get the expected data from the csv file
    expected_data = get_csv_data("optimization_data.csv")
    optimal_point_data = get_csv_data("optimal_point_data.csv")
    maximum_difference = 1  # declare the maximum allowed percent difference
    pass_or_fail = True  # pass or fail value, if true, it passes otherwise it fails
    pass_fail_opt_point = True  # pass or fail value, for the optimal point
    # loop to compare the generated data with the expected data
    for index in range(generated_data_size):

        expected_index = index + 1  # index to get expected data
        # get generated  and expected lines
        line_exp = expected_data[expected_index]
        # declare variables
        time_exp = line_exp[0]
        cost_exp = line_exp[1]
        time_gen = xValue[index]
        cost_gen = yValue[index]
        # get the time and cost difference
        time_diff = optimal.percent_difference(time_gen, time_exp)
        cost_diff = optimal.percent_difference(cost_gen, cost_exp)
        print(f"time difference: {time_diff}% cost difference {cost_diff}%  ")
        # final data validation
        if time_diff > maximum_difference or cost_diff > maximum_difference:
            pass_or_fail = False
    # test the optimal point
    # get calculated values
    optimal_time, optimal_cost, success_result = optimal.optimal_point()
    # get expected values
    optimal_time_exp = optimal_point_data[1][0]
    optimal_cost_exp = optimal_point_data[1][1]
    # verify the optimal point difference
    point_x_diff = optimal.percent_difference(optimal_time, optimal_time_exp)
    point_y_diff = optimal.percent_difference(optimal_cost, optimal_cost_exp)
    # display the point difference
    print(f"optimal time difference: {point_x_diff}% optimal cost difference: {point_y_diff}%")
    # optimal point validation
    if point_x_diff > maximum_difference or point_y_diff > maximum_difference:
        pass_fail_opt_point = False

    assert pass_or_fail is True, "There is an issue with the data"
    assert success_result is True, "There was an error finding the optimal point"
    assert pass_fail_opt_point is True, "There is an issue with the optimization"
