#!/usr/bin/env python3


import logging

from datetime import datetime

from qiskit import Aer, IBMQ
from qiskit import execute as qiskit_execute
from qiskit.providers.aer import noise
from qiskit.providers.aer.noise import NoiseModel
from qiskit.providers.aer.noise.errors import pauli_error


# List of gate times for ibmq_14_melbourne device
_EXEC_SHOTS = 1
_GATE_TIMES = [
    ('u1', None, 0), ('u2', None, 100), ('u3', None, 200),
    ('cx', [1, 0], 678), ('cx', [1, 2], 547), ('cx', [2, 3], 721),
    ('cx', [4, 3], 733), ('cx', [4, 10], 721), ('cx', [5, 4], 800),
    ('cx', [5, 6], 800), ('cx', [5, 9], 895), ('cx', [6, 8], 895),
    ('cx', [7, 8], 640), ('cx', [9, 8], 895), ('cx', [9, 10], 800),
    ('cx', [11, 10], 721), ('cx', [11, 3], 634), ('cx', [12, 2], 773),
    ('cx', [13, 1], 2286), ('cx', [13, 12], 1504), ('cx', [], 800)
]
_LOCAL_BACKEND_NAME = 'qasm_simulator'
_P_RESET = 0.8
_P_MEAS = 0.6
_P_GATE1 = 0.7
_REMOTE_BACKEND_NAME = 'ibmq_16_melbourne'


logger = logging.getLogger(__name__)


def ibm_noise_configuration(remote_backend=_REMOTE_BACKEND_NAME, gate_times=_GATE_TIMES):
    logger.info('Produce IBM noise configuration')

    logger.info('Loading IBM account...')
    before = datetime.now()
    provider = IBMQ.load_account()
    delta = datetime.now() - before
    logger.info('IBM account loaded ({} s)'.format(delta.total_seconds()))

    device = provider.get_backend(remote_backend)

    noise_model = noise.device.basic_device_noise_model(device.properties(),
                                                        gate_times=gate_times)
    coupling_map = device.configuration().coupling_map

    return (noise_model, coupling_map)

def custom_noise_configuration(remote_backend=_REMOTE_BACKEND_NAME):
    logger.info('Produce custom noise configuration')

    logger.info('Loading IBM account...')
    before = datetime.now()
    provider = IBMQ.load_account()
    delta = datetime.now() - before
    logger.info('IBM account loaded ({} s)'.format(delta.total_seconds()))

    device = provider.get_backend(remote_backend)
    coupling_map = device.configuration().coupling_map

    # QuantumError objects
    error_reset = pauli_error([('X', _P_RESET), ('I', 1 - _P_RESET)])
    error_meas = pauli_error([('X', _P_MEAS), ('I', 1 - _P_MEAS)])
    error_gate1 = pauli_error([('X', _P_GATE1), ('I', 1 - _P_GATE1)])
    error_gate2 = error_gate1.tensor(error_gate1)

    # Add errors to noise model
    noise_bit_flip = NoiseModel()
    noise_bit_flip.add_all_qubit_quantum_error(error_reset, "reset")
    noise_bit_flip.add_all_qubit_quantum_error(error_meas, "measure")
    noise_bit_flip.add_all_qubit_quantum_error(error_gate1, ["u1", "u2", "u3"])
    noise_bit_flip.add_all_qubit_quantum_error(error_gate2, ["cx"])

    return (noise_bit_flip, coupling_map)

def execute(circuit,
            *,
            configuration=None,
            local_simulator=_LOCAL_BACKEND_NAME,
            shots=_EXEC_SHOTS):
    logger.info('Execute circuit')

    simulator = Aer.get_backend(local_simulator)

    logger.info('Executing...')
    before = datetime.now()
    if configuration:
        noise_model = configuration[0]
        coupling_map = configuration[1]

        result = qiskit_execute(circuit,
                                simulator, 
                                noise_model=noise_model,
                                coupling_map=coupling_map,
                                basis_gates=noise_model.basis_gates,
                                shots=shots,
                                backend_options={
                                    "max_parallel_threads":0,
                                    'max_parallel_shots':0}
                                ).result()
    else:
        result = qiskit_execute(circuit, simulator, shots=shots).result()

    delta = datetime.now() - before
    logger.info('Execution completed ({} s)'.format(delta.total_seconds()))

    return result.get_counts(circuit)
