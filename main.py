#!/usr/bin/env python3


import logging

from chromosome.chromosome import Chromosome
from circuit_mapper.circuit_mapper import map_circuit
from circuit_mapper.gate_1_qubit import apply_not, apply_phase_flip
from circuit_mapper.gate_2_qubit import apply_controlled_not
from circuit_mapper.gate_map import make_map
from evaluate.evaluate import evaluate
from qiskit_helpers.local_simulator import noise_configuration


CIRCUIT_QCOUNT = 2
GATES_1Q = [apply_phase_flip]
GATES_2Q = [apply_controlled_not]
GENE_COUNT = 16
MEASUREMENT_QCOUNT = 3
USE_CASE = [
    ('00', {'01': 1024}),
    ('01', {'00': 1024}),
    ('10', {'10': 1024}),
    ('11', {'11': 1024})
]


def main():
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)

    gate_map = make_map(CIRCUIT_QCOUNT, MEASUREMENT_QCOUNT, GATES_1Q, GATES_2Q)

    chromosome = Chromosome.superposition_chromosome(GENE_COUNT, MEASUREMENT_QCOUNT)
    configuration = noise_configuration()
    measurements = chromosome.measure(configuration)

    circuit = map_circuit(CIRCUIT_QCOUNT, gate_map, measurements)
    logger.info('\n{}'.format(circuit))

    evaluation = evaluate(circuit, use_case=USE_CASE)
    logger.info('Eval: {}'.format(evaluation))


if __name__ == '__main__':
    main()
