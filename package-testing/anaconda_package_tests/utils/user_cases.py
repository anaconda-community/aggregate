import scipy
import scipy.misc
from scipy import optimize


class Cases:
    """
    Class Used For Calculation of Harmonic Motion and Optimization
    This class helps solve the use case for harmonic motion
    and optimization to test scipy
    """

    def __init__(self):
        # Set the variables for harmonic motion
        self.k_spring_constant = 100
        self.mass = 20
        self.w = scipy.sqrt(self.k_spring_constant / self.mass)
        self.phi = 2
        self.A = 2
        self.period = 2 * scipy.pi / self.w
        self.frequency = 1 / self.period

    # ------- Harmonic Motion Section --------

    def position(self, t):
        """
        Object position function
        Document to refer the use case:
        https://github.com/qxresearch/Simple-Harmonic-Motion
        """
        result = self.A * scipy.sin(self.w * t + self.phi)
        return result

    def velocity(self, t):
        """
        Velocity function
        Document to refer the use case:
        https://github.com/qxresearch/Simple-Harmonic-Motion
        """
        result = self.A * self.w * scipy.cos(self.w * t + self.phi)
        return result

    def acceleration(self, t):
        """
        Acceleration function
        Document to refer the use case:
        https://github.com/qxresearch/Simple-Harmonic-Motion
        """
        result = -(self.A) * self.w**2 * scipy.sin(self.w * t + self.phi)
        return result

    def percent_difference(self, generated_input, expected_input):
        """
        This funnction calculates the percent difference between generated and expected values
        Document to refer the use case:
        https://github.com/qxresearch/Simple-Harmonic-Motion
        """

        # declare variables
        result = 0

        # Make sure that the expected value is a float
        expected_input = float(expected_input)

        # get the average or mean value
        mean_value = (generated_input + expected_input) / (2.0)

        # generate the percent difference
        # check if the average or mean is greater than zero
        if mean_value != 0:
            result = abs((abs(generated_input - expected_input)) / mean_value) * 100

        return result

    def generate_data(self):
        """
        This function generates actual values of position,
        velocity, and acceleration using scipy package
        Document to refer the use case:
        https://github.com/qxresearch/Simple-Harmonic-Motion
        """

        # declare variables
        time = 0.0
        result = []

        while time < 10:
            # get the position velocity and acceleration of the point
            point_position = self.position(time)
            point_velocity_calculated = self.velocity(time)
            point_acceleration_calculated = self.acceleration(time)

            # display the values at each point in time
            line = [
                round(time, 1),
                point_position,
                point_velocity_calculated,
                point_acceleration_calculated,
            ]
            result.append(line)

            time += 0.1  # increment time count

        return result

    # --------- Optimization Section ----------

    def cost_function(self, x):
        """
        This function generates the cost value over time
        used to test the optimization function in scipy
        Document to refer the use case:
        https://tutorial.math.lamar.edu/Classes/CalcI/Optimization.aspx
        """

        # cost function
        cost = 0.25 * (x + 10) ** 2 - 20 * (scipy.sin(x))

        return cost

    def generate_x_y_values(self):
        """
        This function generates a range of values
        to generate the cost graph
        Document to refer the use case:
        https://tutorial.math.lamar.edu/Classes/CalcI/Optimization.aspx
        """

        x = scipy.arange(0, 10, 0.1)
        y = self.cost_function(x)
        return x, y

    def optimal_point(self):
        """
        This function finds the optimal point
        of the cost function
        Document to refer the use case:
        https://tutorial.math.lamar.edu/Classes/CalcI/Optimization.aspx
        """

        optimized_value = optimize.minimize(self.cost_function, x0=0)
        first_solution_x = optimized_value.x[0]
        success_result = optimized_value.success
        first_solution_y = self.cost_function(first_solution_x)

        return first_solution_x, first_solution_y, success_result
