import math

# a single perceptron in the network
# params:
#   input_connection: an array of Connections that are connected as inputs
class Perceptron:
  LEARNING_CONSTANT = 1
  counter = 0

  def __init__(self, input_connections):
    self.input_connections = input_connections
    self.output_connections = []
    self.last_output = None
    self.last_delta = None

    # update all inputs to recognize this perceptron as the input
    for conn in self.input_connections:
      conn.set_sink(self)

    # create an unique identifier for easier logging
    self.identifier = 'Perceptron #{0}'.format(Perceptron.counter)
    Perceptron.counter += 1
    print("Created %s" % self.identifier)

  def __str__(self):
     return self.identifier

  def get_delta(self):
    # make sure we have calculated the delta for this training set
    if self.last_delta is None:
      self.calculate_delta()
    return self.last_delta

  def reset_delta(self):
    # before each round of training, we need to reset the delta
    self.last_delta = None

    # recet all previous perceptrons' delta values
    for conn in self.input_connections:
      if isinstance(conn.get_source(), Perceptron):
        conn.get_source().reset_delta()

  # add a new output connection to this perceptron that it feeds it's result into
  def add_output_connection(self, output_connection):
    self.output_connections.append(output_connection)

  def output(self, is_training = False):
    total_sum = 0
    for conn in self.input_connections:
      total_sum += conn.get_source().output(is_training) * conn.get_weight()

    # determine the final result, we only use the sigmoid function when performing training
    # otherwise we just use the weighted sums
    final_result = 0
    if is_training:
      final_result = self.sigmoid(total_sum)
    else:
      if total_sum >= 0:
        final_result = 1

    print("%s produced total sum: %f and final result (sigmoid/threshold): %f" % (self.identifier, total_sum, final_result))

    self.last_output = final_result
    return final_result

  def get_last_output(self):
    return self.last_output

  def get_input_connections(self):
    return self.input_connections

  # calculate the sigmoid value
  def sigmoid(self, x):
    return 1 / (1 + math.exp(-x))

  # update connection weights based of calculated delta values
  def update_connections(self):
    # update all previous layers (order doesn't matter since we've already calculated deltas)
    for conn in self.input_connections:
      new_weight = conn.get_weight() + Perceptron.LEARNING_CONSTANT * self.last_delta * conn.get_source().get_last_output()
      conn.update_weight(new_weight)

      if isinstance(conn.get_source(), Perceptron):
        conn.get_source().update_connections()

  # calculate the delta of error for the final output node
  # TODO(skovy): likely a bug with a network of config [2, 2, 1] because of a single hidden
  # node requiring two back props - update connections to also have a sink/output perceptron
  def calculate_output_delta(self, desired):
    self.last_delta = self.last_output * (1 - self.last_output) * (desired - self.last_output)
    print("%s produced delta value: %f" % (self.identifier, self.last_delta))

    self.calculate_previous_layer_delta()

  # call the next layers perceptrons and calculate their delta's using this delta value
  def calculate_previous_layer_delta(self):
    for conn in self.input_connections:
      if isinstance(conn.get_source(), Perceptron):
        conn.get_source().calculate_delta()

  # calculate the delta of error for a hidden layer perceptron
  def calculate_delta(self):
    self.last_delta = 0

    # read in all deltas from the perceptrons this perceptron outputs its value to
    # use the weighted delta and generate this perceptrons delta
    for conn in self.output_connections:
      weighted_delta = (conn.get_sink().get_delta() * conn.get_weight())
      self.last_delta += self.last_output * (1 - self.last_output) * weighted_delta

    print("%s produced delta value: %f" % (self.identifier, self.last_delta))
    self.calculate_previous_layer_delta()

  def final_weights(self):
    for conn in self.get_input_connections():
      # only print other perceptrons in the network and ignore biases/inputs/etc
      if isinstance(conn.get_source(), Perceptron):
        conn.get_source().final_weights()

      print("%s with final weight: %f" % (conn, conn.get_weight()))
