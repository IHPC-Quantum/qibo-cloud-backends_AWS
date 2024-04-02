from qibo.backends import NumpyBackend
from qibo.config import raise_error
from qibo.result import MeasurementOutcomes, QuantumState

import re
import importlib.util
import sys

# names of aws module requirements, dict for whether module is importable
names = {'braket': False, 'boto3': False, 'awscli': False}
# whether aws requirements are installed
AWS_REQUIREMENTS = False

error_messages = []

# iter through names, check if module is importable
for name, value in names.items():
    if name in sys.modules:
        names[name] = True
    elif (spec := importlib.util.find_spec(name)) is not None:
        names[name] = True
    else:
        names[name] = False

# if any module is not importable, print missing modules, else imports requriements
if any(value == False for name, value in names.items()):
    error_messages.append('The following modules are missing:')
    for name, value in names.items():
        if value == False:
            error_messages.append(f'    {name}')
    error_messages.append('Please install the modules from the aws-requirements.txt file.')
    error_message = '\n'.join(error_messages)
    print(f'The required module is not installed\n\n{error_message}')
else:
    from braket.aws import AwsDevice, AwsQuantumTask
    from braket.circuits import Circuit, Gate, observables
    from braket.device_schema import DeviceActionType
    from braket.devices import Devices, LocalSimulator
    from braket.parametric import FreeParameter
    from braket.ir.openqasm import Program
    AWS_REQUIREMENTS = True
    print('Modules are imported.')

if AWS_REQUIREMENTS:
    class AWSClientBackend(NumpyBackend):
        """Backend for the remote execution of AWS circuits on the AWS backends.

        Args:
            access_key (str): Access key of the AWS IAM account.
            secret_key (str): Secret key of the AWS IAM account.
            device (str): The AWS platform. Defaults to `"LocalSimulator()"`.
        """

        def __init__(self, platform=None, provider=None, device=None):
            super().__init__()

            if provider is None:
                provider = "aws"

            if platform is None:
                platform = "LocalSimulator"

            if device is None:
                device = LocalSimulator()
            self.device = device
            self.name = "aws"

        def remove_qelib1_inc(self, qasm_string):
            # Remove the "include "qelib1.inc";\n" line
            modified_code = re.sub(r'include\s+"qelib1.inc";\n', '', qasm_string)
            return modified_code

        def execute_aws_circuit(self, circuit, initial_state=None, nshots=1000, **kwargs):
            """Executes the passed circuit.

            Args:
                circuit (qibo.models.Circuit): The circuit to execute.
                initial_state (ndarray): The initial state of the circuit. Defaults to `|00...0>`.
                nshots (int): Total number of shots.
                kwargs (dict): Additional keyword arguments passed to the AWS backends' `run()` method. At the moment, I dont know of any.
            returns:
            (qibo.measurement.MeasurementOutcomes) The outcome of the circuit execution.
            """
            if initial_state is not None:
                raise_error(
                    NotImplementedError,
                    "The use of an `initial_state` is not supported yet.",
                )
            if kwargs:
                raise_error(
                    NotImplementedError,
                    "The use of additional arguments to `run()` is not supported yet.",
                )
            measurements = circuit.measurements
            if not measurements:
                raise_error(RuntimeError, "No measurement found in the provided circuit.")
            nqubits = circuit.nqubits
            circuit_qasm = circuit.to_qasm()
            qasm_program = self.remove_qelib1_inc(circuit_qasm)
            qasm_program = Program(source = qasm_program)
            result = self.device.run(qasm_program, shots=nshots).result()
            samples = result.measurements

            print('measurements\n', measurements)
            print('backend=self \n', self)
            return MeasurementOutcomes(
                measurements=measurements, backend=self, samples=samples, nshots=nshots
            )

else:
    class AWSClientBackend():
        """
        Dummy class to disable AWS backend if requirements are not installed.
        """
        def __init__(self):
            raise ImportError(f'The required module is not installed\n\n{error_message}')

if __name__ == '__main__':
    test = AWSClientBackend()
