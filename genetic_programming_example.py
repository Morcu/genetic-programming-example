# -*- coding: utf-8 -*-
import random
import sympy
import numpy as np
import requests
from copy import deepcopy
#from qesf import fitness

import time
import os
import importlib.util
spec = importlib.util.spec_from_file_location("qesf", os.getcwd() + "/qesf.pyc")
#qesf = importlib.util.module_from_spec(spec)
#spec.loader.exec_module(qesf)
import sys
sys.setrecursionlimit(1000)


NIVELMAXIMO = 4
TAMPOBLACION = 10
QESF = 'qesf'
PI = 'pi'
NOMBREFUNCION = ""
TASAMUTACION = 0.2
NUMEROCICLOS = 50
CONTADOR = 0
TIPOFUNCION = None


BEST = [None,10e10, 0]

URL = 'http://memento.evannai.inf.uc3m.es/age/<fn>/?c=<expr>'
import sys

PARA = 0  #variable global para parar el algoritmo de mezcla en caso de intersección

poblation =[]
p_next = []

class Node:
    """
    Class Node
    """
    def __init__(self, value, nivel, option = None):
        if option == 0:
            opcion = {
                0: float(np.random.randint(1,3)),
                1: 'a',
                2: 'b',
                3: 'c',
                4: 'sqrt',
                5: '+',
                6: '-',
                7: '*',
                8: '/',
                9: '**'

            }
            self.parent = None
            self.data = opcion[value]
            self.nivel = nivel
            if(value > 3):
                self.left = None
            if(value > 4):
                self.right = None
        elif option == 1:
            opcion = {
                0: float(np.random.randint(1, 3)),
                1: 'x',
                2: 'sqrt',
                3: 'sin',
                4: 'cos',
                5: 'tan',
                #a partir de aqui son de 2
                6: '+',
                7: '-',
                8: '*',
                9: '/',
                10: '**'
            }
            self.parent = None
            self.data = opcion[value]
            self.nivel = nivel
            if (value > 1):
                self.left = None
            if (value > 5):
                self.right = None

class Tree:
    """
    Class tree will provide a tree as well as utility functions.
    """
    def generateTree(self, opcion, nivel_max):
        nivel = 0
        if opcion == 0:
            return self.recursiveGenerator(nivel, nivel_max)
        elif opcion == 1:
            return self.recursiveGeneratorPI(nivel, nivel_max)

    def recursiveGeneratorPI(self, nivel, nivelMaximo):
        nodo = None
        if (nivel == nivelMaximo):
            #solo los que son constante o numeros
            nodo = Node(np.random.randint(0,1), nivel, 1)
        else:
            if (nivel == 0):
                #lo que no sea cte o numero
                nodo = Node(np.random.randint(2, 10), nivel, 1)
            else:
                #cualquier cosa
                nodo = Node(np.random.randint(0, 10), nivel, 1)
            nivel = nivel + 1
            if (hasattr(nodo, "left")):
                nodo.left = self.recursiveGeneratorPI(nivel, NIVELMAXIMO)
                nodo.left.parent = nodo
            if(hasattr(nodo,"right")):
                nodo.right = self.recursiveGeneratorPI(nivel, NIVELMAXIMO)
                nodo.right.parent = nodo
        return nodo

    def recursiveGenerator(self, nivel, nivelMaximo):
        nodo = None
        if (nivel == nivelMaximo):
            # solo los que son constante o numeros
            nodo = Node(np.random.randint(0,3), nivel, 0)
        else:
            if (nivel == 0):
                # lo que no sea cote o numero
                nodo = Node(np.random.randint(4, 9), nivel, 0)
            else:
                # cualquier cosa
                nodo = Node(np.random.randint(0, 9), nivel, 0)
            nivel = nivel + 1
            if (hasattr(nodo, "left")):
                nodo.left = self.recursiveGenerator(nivel, NIVELMAXIMO)
                nodo.left.parent = nodo
            if(hasattr(nodo,"right")):
                nodo.right = self.recursiveGenerator(nivel, NIVELMAXIMO)
                nodo.right.parent = nodo
        return nodo

    def imprimeNodo(self, nodo, auxArr):

        if (hasattr(nodo, "right")):

            auxArr.append("(")
            self.imprimeNodo(nodo.left, auxArr)

            auxArr.append(str(nodo.data))
            self.imprimeNodo(nodo.right, auxArr)

            auxArr.append(")")
        elif (hasattr(nodo, "left")):
            auxArr.append(str(nodo.data))
            auxArr.append("(")


            self.imprimeNodo(nodo.left, auxArr)

            auxArr.append(")")
        else:
            
            auxArr.append(str(nodo.data))
        return auxArr

    def buscaNodo(self, nodo, objetivo):
        global CONTADOR
        CONTADOR = CONTADOR + 1
        if (CONTADOR == objetivo):
            CONTADOR = 0
            return nodo
        else:
            salida = None
            if (hasattr(nodo, "right")):
                salida = self.buscaNodo(nodo.left, objetivo)
                if (salida != None):
                    CONTADOR = 0
                    return salida
                else:
                    salida = self.buscaNodo(nodo.right, objetivo)
                    return salida

            else:
                if (hasattr(nodo, "left")):
                    salida = self.buscaNodo(nodo.left, objetivo)
                    return salida
                else:
                    return None

    def count_nodes(self, node):
        count = 1
        if (hasattr(node, "right")):
            #r_node = node.right
            count += self.count_nodes(node.right)
        if (hasattr(node, "left")):
            #l_node = node.left
            count += self.count_nodes(node.left)

        return count


#DEPRECATED
def peticionEndPoint(nombreFunc, func):
    global URL
    endPoint = URL.replace('<fn>',nombreFunc)
    endPoint = endPoint.replace('<expr>', func)

    try:
        return requests.get(endPoint)

    except requests.exceptions.RequestException as e:  # This is the correct syntax
        print(e)
        sys.exit(1)

def tournament(poblation_param, ventana, fit_arr):
    global TAMPOBLACION
    pob_len_count = 0
    poblation_len = TAMPOBLACION - 1
    final_pobl = []

    while(pob_len_count < TAMPOBLACION - 1):
        arena = []
        for i in range(ventana):
            rand = random.randint(0, poblation_len)
            ind = fit_arr[rand]
            arena.append(
                {"fit":ind,
                "pos":rand})
        orden = sorted(arena, key=lambda k: k["fit"])
        final_pobl.append(orden[0]["pos"])
        pob_len_count += 1

    return final_pobl

#Crossover Normal
def crossover(nA, nB):

    tree = Tree()
    count_a =tree.count_nodes(nA)
    count_b = tree.count_nodes(nB)
    if (count_a >1 and count_b > 1):
        while(True):
            change_A = random.randint(1, count_a)
            change_B = random.randint(1, count_b)

            nodeA = tree.buscaNodo(nA, change_A)
            nodeB = tree.buscaNodo(nB, change_B)
            if(nodeA.parent is not None and nodeB.parent is not None):
                break
        parentB = nodeB.parent

        if(nodeA.parent.left is nodeA):
            nodeA.parent.left = nodeB
        else:
            nodeA.parent.right = nodeB
        nodeB.parent = nodeA.parent

        if (parentB.left is nodeB):
            parentB.left = nodeA
        else:
            parentB.right = nodeA
        nodeA.parent = parentB

def crossover_controlado(ind_nodoA, ind_nodoB, depths):
    global poblation
    depth_A = depths[ind_nodoA]
    depth_B = depths[ind_nodoB]

    if (depth_A  > 1 and depth_B > 1):
        while (True):
            ind_cambiar = random.randint(1, min(depth_A, depth_B))
            arrA = []
            arrB = []
            arrA = nodo_en_nivel(poblation[ind_nodoA], 0, ind_cambiar, arrA)
            arrB = nodo_en_nivel(poblation[ind_nodoB], 0, ind_cambiar, arrB)

            try:
                #Se obtiene un nodo aleatorio de entre los arrays de nodos en esa profundidad
                nodeA = arrA[random.randint(0, len(arrA) -1)]
                nodeB = arrA[random.randint(0, len(arrB) - 1)]
                if (nodeA.parent is not None and nodeB.parent is not None):
                    break
            except:
                pass

        parentB = nodeB.parent

        if (nodeA.parent.left is nodeA):
            nodeA.parent.left = nodeB
        else:
            nodeA.parent.right = nodeB
        nodeB.parent = nodeA.parent

        if (parentB.left is nodeB):
            parentB.left = nodeA
        else:
            parentB.right = nodeA
        nodeA.parent = parentB


def mutation(nodo, func):
    # Si viene de una funcion que solo tiene 2 hijos
    if (hasattr(nodo, "right")):

        orig = nodo.data
        new_data = nodo.data
        if func == 0:
            opcion = {
                0: '+',
                1: '-',
                2: '*',
                3: '/',
                4: '**',
                5: 'sqrt'
            }

            while (new_data == orig):
                rand = np.random.randint(0, 5)
                new_data = opcion[rand]
                #Si muta a algo que solo tiene un hijo eliminamos la parte derecha
                if rand > 4:
                    if hasattr(nodo, "right"):
                        del nodo.right
            nodo.data = new_data
        elif func == 1:
            opcion = {
                0: '+',
                1: '-',
                2: '*',
                3: '/',
                4: '**',
                5: 'sqrt'
            }

            while (new_data == orig):
                rand = np.random.randint(0, 5)
                new_data = opcion[rand]
                #Si muta a algo que solo tiene un hijo eliminamos la parte derecha
                if rand > 4:
                    if hasattr(nodo, "right"):
                        del nodo.right
            nodo.data = new_data

    #Si viene de una funcion que solo tiene 1 hijo
    elif (hasattr(nodo, "left")):

        #El nodo tiene 2 hijos
        if func == 0:
            new_node = Node(np.random.randint(5, 9), nodo.nivel, func)
        elif func == 1:
            new_node = Node(np.random.randint(6, 10), nodo.nivel, func)
        new_node.parent = nodo.parent
        new_node.left = nodo.left
        nodo.left.parent = new_node
        if(nodo.parent is not None):
            if(nodo.parent.left is nodo):
                nodo.parent.left = new_node
            else:
                nodo.parent.right = new_node
        #El nodo es un terminal --> solo cte y numeros
        if func == 0:
            new_right_node = Node(np.random.randint(0, 3), nodo.left.nivel, func)
        elif func == 1:
            new_right_node = Node(np.random.randint(0, 1), nodo.left.nivel, func)
        new_right_node.parent = new_node
        new_node.right = new_right_node
    #Si no tiene hijos --> si es un terminal
    else:

        orig = nodo.data
        new_data = nodo.data
        if func == 0:
            opcion = {
                0: float(np.random.randint(1, 3)),
                1: 'a',
                2: 'b',
                3: 'c',
            }
            while (new_data == orig):
                new_data = opcion[random.randint(0, 3)]
        elif func == 1:
            opcion = {
                0: float(np.random.randint(1, 3)),
                1: 'x',

            }
            while (new_data == orig):
                new_data = opcion[random.randint(0, 1)]

        nodo.data = new_data

def mutacionAgresiva(nodo, func):
    #Elige un nodo aleatoriamente
    #Genera un subarbol de tamaño aleatorio entre 1 y el maximo de profundidad
    tree = Tree()
    count_a = tree.count_nodes(nodo)
    change_A = random.randint(1, count_a)
    depth = random.randint(1, NIVELMAXIMO)
    nodeA = tree.buscaNodo(nodo, change_A)
    global TIPOFUNCION

    if TIPOFUNCION == 0:
        if nodeA.parent is None:
            nodeA = tree.recursiveGenerator(0, NIVELMAXIMO)
        else:
            sub_arbol = tree.recursiveGenerator(0, depth)
            if nodeA.parent.left is nodeA:
                nodeA.parent.left = sub_arbol
                sub_arbol.parent = nodeA.parent
            else:
                nodeA.parent.right = sub_arbol
                sub_arbol.parent = nodeA.parent
    elif TIPOFUNCION == 1:
        if nodeA.parent is None:
            nodeA = tree.recursiveGenerator(0, NIVELMAXIMO)
        else:
            sub_arbol = tree.recursiveGeneratorPI(0, depth)
            if nodeA.parent.left is nodeA:
                nodeA.parent.left = sub_arbol
                sub_arbol.parent = nodeA.parent
            else:
                nodeA.parent.right = sub_arbol
                sub_arbol.parent = nodeA.parent



def print_poblation(poblation):
    tree = Tree()
    for ind in poblation:
        aux = []

        final = tree.imprimeNodo(ind, aux)
        treeString = ''.join(str(e) for e in final)
        c = tree.count_nodes(ind)
        print(treeString, " - ", c)
    print("------")

def nivel_maximo(nodo, nivel):
    nivel += 1
    if hasattr(nodo, "right"):
        salida = nivel_maximo(nodo.left, nivel)
        salida2 = nivel_maximo(nodo.right, nivel)
        if salida > salida2:
            return salida
        else:
            return salida2
    elif hasattr(nodo, "left"):
        salida = nivel_maximo(nodo.left, nivel)
        return salida
    else:
        return nivel

def nodo_en_nivel(nodo, nivel, nivelBusq, arr_sol):
    nivel += 1
    #Si ha encontrado el nodo lo guarda
    if(nivel == nivelBusq):
        arr_sol.append(nodo)
        return
    #Busca entre los hijos
    if hasattr(nodo, "right"):
        nodo_en_nivel(nodo.left, nivel, nivelBusq, arr_sol)
        nodo_en_nivel(nodo.right, nivel, nivelBusq, arr_sol)

    elif hasattr(nodo, "left"):
        nodo_en_nivel(nodo.left, nivel, nivelBusq, arr_sol)
    #Si es el padre que devuelva la solucion
    if nivel == 1:
        return arr_sol

def main():
    global NUMEROCICLOS
    global poblation
    global NOMBREFUNCION
    global TIPOFUNCION
    global TAMPOBLACION
    global TASAMUTACION
    global p_next
    global BEST
    #Argumentos a pasar al programa
    # orden: NUMERO_CICLOS | TAM_POBLACION | TASA_MUTACION
    NUMEROCICLOS = int(sys.argv [1])
    TAMPOBLACION = int(sys.argv [2])
    TASAMUTACION = float(sys.argv [3])

    #La funcion de QESF es 0 y PI es 1
    funcion = int(sys.argv[4])
    if(funcion == 0):
        NOMBREFUNCION = QESF
        TIPOFUNCION = 0
    elif(funcion == 1):
        NOMBREFUNCION = PI
        TIPOFUNCION = 1
    print('num_ciclos ' + str(NUMEROCICLOS) + ' tam_poblacion ' + str(TAMPOBLACION) + ' tasa_mutacion ' + str(TASAMUTACION) +
          ' funcion ' + str(NOMBREFUNCION))

    needMut = NUMEROCICLOS * 0.3
    tree = Tree()
    p_next = [None]*TAMPOBLACION
    for i in range(TAMPOBLACION):
        raiz = tree.generateTree(funcion, NIVELMAXIMO)
        poblation.append(raiz)

    for ciclo in range(NUMEROCICLOS):
        print('----- ciclo ' + str(ciclo) + "--------")

        fit_arr = []
        depths = []

        t1 = time.time()
        for ind in poblation:
            aux = []
            final = tree.imprimeNodo(ind, aux)
            treeString = ''.join(str(e) for e in final)
            max_depth = nivel_maximo(ind, 0)
            '''
            try:
                fitness = qesf.fitness(treeString)
                fit_arr.append(float(fitness))
            except:
                fit_arr.append(float('Inf'))
            '''
            try:
                fitness = peticionEndPoint(NOMBREFUNCION, treeString)

                fit_arr.append(float(fitness.text))

            except:
                fit_arr.append(float('Inf'))
            depths.append(max_depth)


        if (ciclo!=0):

            max_fitness = max(fit_arr)
            max_value = fit_arr.index(max_fitness)
            if (BEST[1] < max_fitness):
                poblation[max_value] = deepcopy(BEST[0])
                fit_arr[max_value] = deepcopy(BEST[1])
                depths[max_value] = deepcopy(BEST[2])
        min_fitness = min(fit_arr)
        min_value = fit_arr.index(min_fitness)
        min_ind = deepcopy(poblation[min_value])
        min_ind_depth = depths[min_value]

        ########Guardamos el mejor individuo################
        if (min_fitness < BEST[1]):
            BEST[0] = deepcopy(min_ind)
            BEST[1] = deepcopy(min_fitness)
            BEST[2] = deepcopy(min_ind_depth)
####################################################

        #print_poblation(poblation)

        tour_pob = tournament(poblation, 3, fit_arr)

        for i in range(TAMPOBLACION - 1):
            p_next[i] = deepcopy(poblation[tour_pob[i]])

        for i in range(0, TAMPOBLACION -1 ,2):
            #Al cruce normal se le pasan los nodos a cruzar
#-----------------------------CROOSSS-------
            crossover(p_next[i], p_next[i+1])

            #crossover_controlado(i, i + 1, depths)
        for i in range((TAMPOBLACION - 1)):
            poblation[i] = deepcopy(p_next[i])

        #print_poblation(poblation)
        for it in range(TAMPOBLACION):

            if(random.uniform(0, 1) <= TASAMUTACION):
                #print('mut' + str(it))

                mut = tree.buscaNodo(poblation[it], random.randint(1, (tree.count_nodes(poblation[it]) - 1)))

                if ciclo <= needMut:
                    mutacionAgresiva(mut, funcion)
                else:
                    mutation(mut, funcion)


        #print_poblation(poblation)


        #min_fitness = min(fit_arr)
        #min_value = fit_arr.index(min_fitness)
        #min_ind = poblation[min_value]
        aux = []

        final= tree.imprimeNodo(min_ind, aux)
        treeString = ''.join(str(e) for e in final)
        
########Sustituimos el mejor individuo de la anterior poblacion por el peor de la siguiente##########
#        if (ciclo!=0):
#            print ("Change")
#            max_fitness = max(fit_arr)
#            max_value = fit_arr.index(max_fitness)
#            if (BEST[1] < max_fitness):
#                poblation[max_value] = deepcopy(BEST[0])
#####################################################################################################



        print(fit_arr[min_value], treeString)

        print("TIME: " + str(time.time() - t1))

    aux = deepcopy(poblation[0])




    '''
    nodo_en_pos = tree.buscaNodo(raiz, 6)
    print(nodo_en_pos.data)
    '''
if __name__ == "__main__":
    main()

def __del__(self):
    pass
