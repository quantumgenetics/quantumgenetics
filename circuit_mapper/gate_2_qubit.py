#!/usr/bin/env python3


from functools import partial


def combine(qubit_count, gates):
    return [partial(g, a, b)
            for g in gates
            for a in range(qubit_count)
            for b in range(qubit_count)
            if a != b]

def apply_controlled_not(control, target, circuit):
    qr = circuit.qregs[0]

    circuit.cx(qr[control], qr[target])
