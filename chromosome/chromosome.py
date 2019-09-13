#!/usr/bin/env python3


import logging

from concurrent import futures
from datetime import datetime
from functools import partial

from .gene import Gene


class Chromosome():

    def __init__(self, genes):
        self._genes = genes.copy()

        self._logger = logging.getLogger(__name__)

    def measure(self, noise_config):
        self._logger.info('Measuring chromosome...')
        before = datetime.now()
        measurer = partial(_measure, noise_config)
        with futures.ProcessPoolExecutor() as executor:
            measurements = executor.map(measurer, self._genes)
        delta = datetime.now() - before
        self._logger.info('Chromosome measured ({} s)'.format(delta.total_seconds()))

        return measurements

    @classmethod
    def superposition_chromosome(cls, gene_count, qubit_count_per_gene):
        gene = Gene.superposition_gene(qubit_count_per_gene)
        genes = [gene for _ in range(gene_count)]

        return cls(genes)


def _measure(noise_config, gene):
    return gene.measure(noise_config)
