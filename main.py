#!/usr/bin/env python3


import logging

from datetime import datetime
from functools import partial

import circuit_mapper.gate_1_qubit as g_1q
import circuit_mapper.gate_2_qubit as g_2q
import numpy as np

from chromosome.chromosome import Chromosome
from circuit_mapper.circuit_mapper import map_circuit
from circuit_mapper.gate_map import make_map
from evaluate.evaluate import evaluate
from qiskit_helpers.local_simulator import ibm_noise_configuration


CIRCUIT_QCOUNT = 2
GATES_1Q = [
    g_1q.apply_hadamard,
    partial(g_1q.apply_z_rotation, np.pi / 4)
]
GATES_2Q = [
    g_2q.apply_controlled_not
]
GENE_COUNT = 8
MAX_GENERATIONS = 100
MEASUREMENT_QCOUNT = 3
USE_CASE = [
    ('00', {'01': 1024}),
    ('01', {'00': 1024}),
    ('10', {'10': 1024}),
    ('11', {'11': 1024})
]


def main():
    logging.basicConfig(level=logging.WARNING)
    logger = logging.getLogger(__name__)

    gate_map = make_map(CIRCUIT_QCOUNT, MEASUREMENT_QCOUNT, GATES_1Q, GATES_2Q)

    chromosome = Chromosome.superposition_chromosome(GENE_COUNT, MEASUREMENT_QCOUNT)
    configuration = ibm_noise_configuration()
    measurements = chromosome.measure(configuration)

    winner = map_circuit(CIRCUIT_QCOUNT, gate_map, measurements)
    winner_eval = evaluate(winner, use_case=USE_CASE)
    winner_measurements = measurements

    gen_count = 0
    while gen_count < MAX_GENERATIONS and winner_eval[1] > 0:
        logger.warning('Running generations {}'.format(gen_count))

        logger.warning('Producing candidate...')
        before = datetime.now()
        candidate_measurements = chromosome.measure(configuration)
        candidate = map_circuit(CIRCUIT_QCOUNT, gate_map, candidate_measurements)
        candidate_eval = evaluate(candidate, use_case=USE_CASE)
        delta = datetime.now() - before
        logger.warning('Candidate produced ({} s)'.format(delta.total_seconds()))

        if candidate_eval[1] < winner_eval[1]:
            logger.warning('Found new winner')

            chromosome = chromosome.evolve(winner_measurements, candidate_measurements)

            winner = candidate
            winner_eval = candidate_eval
            winner_measurements = candidate_measurements

        logger.warning('Generation {}'.format(gen_count))
        logger.warning('Current winner eval: {}'.format(winner_eval))

        gen_count += 1

    logger.warning('Winner circuit:\n{}'.format(winner))
    logger.warning('Winner eval: {}'.format(winner_eval))


if __name__ == '__main__':
    main()
