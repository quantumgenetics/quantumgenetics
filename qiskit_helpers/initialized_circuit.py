#!/usr/bin/env python3


import logging

from datetime import datetime

from qiskit import QuantumCircuit


logger = logging.getLogger(__name__)


def initialized_empty_circuit(qubit_count, state):
    logger.info('Produce circuit')

    return initialized_circuit(QuantumCircuit(qubit_count, qubit_count), state)

def initialized_circuit(circuit, state):
    qubit_count = len(circuit.qubits)
    assert len(state) == 2**qubit_count

    pre_circuit = QuantumCircuit(circuit.qregs[0], circuit.cregs[0])

    logger.info('Initializing circuit...')
    before = datetime.now()
    pre_circuit.initialize(state, range(qubit_count))
    delta = datetime.now() - before
    logger.info('Circuit initialized ({} s)'.format(delta.total_seconds()))

    post_circuit = circuit.copy()
    post_circuit.barrier(post_circuit.qregs[0])
    post_circuit.measure(range(qubit_count), range(qubit_count))

    return pre_circuit + post_circuit
