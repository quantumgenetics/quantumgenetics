#!/usr/bin/env python3


import logging

from datetime import datetime

from qiskit import ClassicalRegister, QuantumCircuit, QuantumRegister


logger = logging.getLogger(__name__)


def map_circuit(circuit_qcount, gate_map, measurements):
    logger.info('Producing circuit...')
    before = datetime.now()

    qr = QuantumRegister(circuit_qcount)
    cr = ClassicalRegister(circuit_qcount)
    circuit = QuantumCircuit(qr, cr)

    for m in measurements:
        gate_map[m](circuit)

    delta = datetime.now() - before
    logger.info('Circuit produced ({} s)'.format(delta.total_seconds()))

    return circuit
