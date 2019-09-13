#!/usr/bin/env python3


from .gate_1_qubit import combine as combine_1q
from .gate_1_qubit import repeat_none
from .gate_2_qubit import combine as combine_2q


def make_map(circuit_qcount, measure_qcount, gates_1q, gates_2q):
    gates = combine_1q(circuit_qcount, gates_1q) + combine_2q(circuit_qcount, gates_2q)
    assert len(gates) <= 2**measure_qcount

    gates += repeat_none(0, 2**measure_qcount - len(gates))

    return {format(i, '0{}b'.format(measure_qcount)) : g for i,g in enumerate(gates)}
