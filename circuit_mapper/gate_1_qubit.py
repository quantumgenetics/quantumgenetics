#!/usr/bin/env python3


from functools import partial


def combine(qubit_count, gates):
    return [partial(g, i) for g in gates for i in range(qubit_count)]

def repeat_none(index, count):
    return [partial(apply_none, index)] * count

def apply_none(index, circuit):
    pass

def apply_not(index, circuit):
    qr = circuit.qregs[0]

    circuit.x(qr[index])

def apply_phase_flip(index, circuit):
    qr = circuit.qregs[0]

    circuit.z(qr[index])
