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

def apply_hadamard(index, circuit):
    qr = circuit.qregs[0]

    circuit.h(qr[index])

def apply_y_rotation(theta, index, circuit):
    qr = circuit.qregs[0]

    circuit.ry(theta, qr[index])

def apply_z_rotation(phi, index, circuit):
    qr = circuit.qregs[0]

    circuit.rz(phi, qr[index])
