#!/usr/bin/env python3


import logging

from datetime import datetime

import numpy as np

from qiskit_helpers.initialized_circuit import initialized_empty_circuit
from qiskit_helpers.local_simulator import execute


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

    @classmethod
    def superposition_gene(cls, qubit_count):
        state_count = 2**qubit_count
        superposition_state = np.repeat(complex(1/np.sqrt(state_count)), state_count)

        return cls.gene(qubit_count, superposition_state)

    @classmethod
    def gene(cls, qubit_count, state):
        return cls(initialized_empty_circuit(qubit_count, state))
