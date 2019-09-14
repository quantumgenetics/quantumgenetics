from multiprocessing import Pool
from qiskit import Aer
import numpy as np
from collections import deque
from copy import deepcopy
import math
from qiskit import QuantumCircuit, ClassicalRegister, QuantumRegister, execute
import random

class Genetic_Executor:
	'''
	It is just a class to keep things together.
	'''
	def __init__(\
		self,
		number_of_processors,
		population_initializer,
		population_size,
		parallel_population_initialization_flag=True):
		'''

		number_of_processors -> positive integer
			the number of processes that will be spawned

		population_initializer -> function
			a function that returns an iterable representing the population

		'''
		self.processs_pool = Pool(number_of_processors)

		self.population = population_initializer(population_size, self.processs_pool)

		self.population_size = population_size

	def apply_operation(self, operation_on_population):
		'''
		operation_on_population -> function
			It receives the process pool and the population. It is called here
		'''
		return operation_on_population(self.processs_pool, self.population)


def get_number_gate_seq_relation(depth, available_gates):
	'''
	Based on how many gates can there be, after a qubit,
	all the possible combinations of the gates are generated in a list and
	returned.
	'''
	av_gates_tuple = tuple()
	for key in available_gates.keys():
		av_gates_tuple += available_gates[key]
	av_gates_tuple += ('i',)
	mapping_list = []
	current_seq_gates_list = []
	dq = deque([(gate,0) for gate in av_gates_tuple])
	while dq:
		gate, d = dq.pop()

		current_seq_gates_list = current_seq_gates_list[:d]

		current_seq_gates_list.append(gate)

		if d == depth - 1:
			mapping_list.append(deepcopy(current_seq_gates_list))
		elif d < depth - 1:
			for g in av_gates_tuple:
				dq.append((g,d+1,))

	return mapping_list

def get_binary(decimal):
	'''
	Gets a decimal as input. Outputs a list of the decimals binary representation.
	e.g. If the nuber of binaries in the list is 3 and decimal is 3, then the
	function outputs [0,1,1].
	'''
	key = [0 for _ in range(number_of_qubits_in_possible_circuit)]
	s_i = format(decimal, "b")
	k = number_of_qubits_in_possible_circuit - 1
	j = len(s_i)-1
	while j >= 0:
		if s_i[j] == '1': key[k] = 1
		k-=1
		j-=1
	return key

def get_binary_from_str(s):
	key = []
	for ch in s:
		if ch == '0':
			key.append(0)
		else:
			key.append(1)
	return key

def get_decimal(binary):
	'''
	Gets a binary list and returns the decimal representaion.
	'''
	i = len(binary)-1
	a = 0
	for b in binary:
		a += b**i
		i -= 1
	return a

def get_random_goal_function(number_of_qubits_in_possible_circuit):
	'''
	Generates a random binary function of "number_of_qubits_in_possible_circuit"
	bits.
	'''
	goal_function_dict = dict()
	for i in range(2**number_of_qubits_in_possible_circuit):
		goal_function_dict[tuple(get_binary(i))] = np.random.choice(2,
			number_of_qubits_in_possible_circuit)
	return goal_function_dict

def chromosome_initialzer(a):
	'''
	Randomly initializez and returns a chromosome (a tuple of 3 elements:
	theta, and amplitudes based on theta). Argument "a" is not used anywhere.
	'''
	theta_arr = 2 * math.pi * np.random.random(number_of_qubits_in_individual)
	return (theta_arr,\
		np.cos(theta_arr),\
		np.sin(theta_arr))

def initializer1(pop_size, p_pool):
	return p_pool.map(chromosome_initialzer, [None for _ in range(pop_size)])


def get_pop_fitness(p_pool, population_iterable):
	'''
	Collapses the individuals and then evalueates the circuit.
	'''
	fitness_list = []

	for theta_arr, _, _ in population_iterable:
		qr = QuantumRegister(number_of_qubits_in_individual)
		cr = ClassicalRegister(number_of_qubits_in_individual)
		qc = QuantumCircuit(qr, cr,)
		for i in range(number_of_qubits_in_individual):
			qc.u3(theta_arr[i], 0, 0, qr[i])
		qc.measure(qr,cr)
		job = execute(qc, backend=backend, shots=1,)
		results = job.result()
		answer = results.get_counts()

		binary_list = get_binary_from_str(tuple(answer.keys())[0])

		binary_bu_list = deepcopy(binary_list)

		qubits_per_line = len(binary_list)//number_of_qubits_in_possible_circuit

		v = 0

		for key in goal_function.keys():

			qr = QuantumRegister(number_of_qubits_in_individual)
			cr = ClassicalRegister(number_of_qubits_in_individual)
			qc = QuantumCircuit(qr, cr,)

			for i in range(number_of_qubits_in_possible_circuit):
				if key[i] == 1: qc.x(qr[i])

			a = 0
			for i in range(number_of_qubits_in_possible_circuit):
				config = config_list[get_decimal(binary_bu_list[a:a+qubits_per_line])]

				for gate in config:
					if gate == 'i':
						qc.iden(qr[i])
					elif gate == 's':
						qc.u3(0,0,math.pi/4,qr[i])
					elif gate == 'h':
						qc.h(qr[i])
					else:
						qc.cx(qr[i],qr[(i+1)%number_of_qubits_in_possible_circuit])

				a += qubits_per_line

			qc.measure(qr,cr)

			job = execute(qc, backend=backend, shots=global_shots,\
				backend_options={\
					"max_parallel_threads":0,
					'max_parallel_shots':0})
			results = job.result()
			answer = results.get_counts()

			goal_value = get_decimal(goal_function[key])

			if goal_value not in answer:
				v += global_shots
			else:
				v += global_shots - answer[goal_value]

		fitness_list.append((v,binary_bu_list))
	return fitness_list


def main0():
	global number_of_qubits_in_individual,backend,number_of_qubits_in_possible_circuit,config_list

	number_of_qubits_in_individual = 18

	number_of_qubits_in_possible_circuit = 3

	available_gates = {
		1 : ('s', 'h'),
		2 : ('cnot',),
	}

	depth = 3

	global global_shots,goal_function

	global_shots = 2048

	backend = Aer.get_backend('qasm_simulator',)

	config_list = get_number_gate_seq_relation(depth, available_gates)

	goal_function = get_random_goal_function(number_of_qubits_in_possible_circuit)

	ge = Genetic_Executor(7, initializer1, 10,)

	print(ge.apply_operation(get_pop_fitness))

if __name__ == '__main__':
	main0()
