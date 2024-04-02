from qibo import Circuit
from qibo import gates
import numpy as np
from braket.aws import AwsDevice
from qibo_cloud_backends import aws_client

circuit_qibo = Circuit(1)
circuit_qibo.add(gates.RX(0, np.pi/7))
circuit_qibo.add(gates.M(0))
circuit_qibo.measurements

# Local simulator test, does not cost money
AWS = aws_client.AWSClientBackend()
# AWS device tests, cost money
#AWS = aws_client.AWSClientBackend(device = AwsDevice("arn:aws:braket:eu-west-2::device/qpu/oqc/Lucy"))
#AWS = aws_client.AWSClientBackend(device = AwsDevice("arn:aws:braket:::device/quantum-simulator/amazon/sv1"))

test = AWS.execute_aws_circuit(circuit_qibo, nshots=1000)

print(test.probabilities())