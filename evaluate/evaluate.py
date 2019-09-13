#!/usr/bin/env python3


import logging

from concurrent import futures
from datetime import datetime
from functools import partial

import numpy as np

from qiskit_helpers.initialized_circuit import initialized_circuit
from qiskit_helpers.local_simulator import execute


logger = logging.getLogger(__name__)


def evaluate(circuit, *, use_case):
    logger.info('Evaluating use case...')
    before = datetime.now()

    evaluator = partial(_evaluate_single_case, circuit)
    with futures.ProcessPoolExecutor() as executor:
        evaluations = executor.map(evaluator, use_case)

    raw_summary = list(zip(*evaluations))
    summary = (raw_summary[0], sum(raw_summary[1]))

    delta = datetime.now() - before
    logger.info('Use case evaluated ({} s)'.format(delta.total_seconds()))

    return summary

def _evaluate_single_case(circuit, single_case):
    logger.info('Evaluate circuit')

    circuit_input = single_case[0]
    circuit_outputs = single_case[1]

    qubit_count = len(circuit.qubits)
    state_count = 2**qubit_count

    state = np.repeat(complex(0), state_count)
    state[int(circuit_input, 2)] = complex(1)

    eval_circuit = initialized_circuit(circuit, state)

    shots = sum(circuit_outputs.values())
    counts = execute(eval_circuit, shots=shots)

    diff = []
    for i in range(state_count):
        key = format(i, '0{}b'.format(qubit_count))

        diff.append(abs(circuit_outputs.get(key, 0) - counts.get(key, 0)))

    return ((circuit_input, circuit_outputs, counts), sum(diff))
