#!/usr/bin/env python3


import logging

from datetime import datetime

import numpy as np

from circuit_mapper.gate_1_qubit import apply_y_rotation
from qiskit_helpers.initialized_circuit import initialized_empty_circuit
from qiskit_helpers.local_simulator import execute


ROTATION = 0.025

class Gene():

    def __init__(self, circuit):
        self._circuit = circuit.copy()

        self._logger = logging.getLogger(__name__)

    def __getstate__(self):
        return self._circuit

    def __setstate__(self, state):
        self._circuit = state
        self._logger = logging.getLogger(__name__)

    def measure(self, noise_config):
        self._logger.info('Measuring gene...')
        before = datetime.now()
        counts = execute(self._circuit, configuration=noise_config)
        measurement = next(iter(counts))
        delta = datetime.now() - before
        self._logger.info('Gene measured ({} s)'.format(delta.total_seconds()))

        return measurement

    def evolve(self, from_measurement, to_measurement):
        next_circuit = self._circuit.copy()

        for i in range(len(from_measurement)):
            f = from_measurement[i]
            t = to_measurement[i]
            if f == t:
                continue

            sign = 1 if f == '0' and t == '1' else -1
            apply_y_rotation(sign * ROTATION * np.pi, i, next_circuit)

        return Gene(next_circuit)

    @classmethod
    def superposition_gene(cls, qubit_count):
        state_count = 2**qubit_count
        superposition_state = np.repeat(complex(1/np.sqrt(state_count)), state_count)

        return cls.gene(qubit_count, superposition_state)

    @classmethod
    def gene(cls, qubit_count, state):
        return cls(initialized_empty_circuit(qubit_count, state))
