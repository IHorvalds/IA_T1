####################################################################################
#                               Uniform Cost Search                                #
####################################################################################

import sys
import os
sys.path.insert(1, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))
from input_parser import parse as parser
import stopit
import time


class NodParcurgere:

    # Object counters
    total_instantiations = 0
    total_deletions = 0
    is_counting = False

    def __init__(self, info, cost, parinte, directie=None):
        self.info = info
        self.g = cost
        self.parinte = parinte  # parintele din arborele de parcurgere
        self.directie = directie    # parinte -> copil

        if NodParcurgere.is_counting:
            NodParcurgere.total_instantiations += 1
    
    def __del__(self):
        if NodParcurgere.is_counting:
            NodParcurgere.total_deletions += 1

    def obtineDrum(self):
        l = [self]
        nod = self
        while nod.parinte is not None:
            l.insert(0, nod.parinte)
            nod = nod.parinte
        return l

    def afisDrum(self): # returneaza drumul formatat
        l = self.obtineDrum()
        path = ""
        for nod in l:
            if nod.directie is not None:
                path += " {} {}".format(nod.directie, nod)
            else:
                path += str(nod)
        path += "\nlungime: {}\ncost: {}\n".format(len(l), self.g)
        return path

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if infoNodNou == nodDrum.info:
                return True
            nodDrum = nodDrum.parinte
        return False

    def __repr__(self):
        sir = ""
        sir += str(self.info)
        return sir

    def __str__(self):
        return str(self.info)


class Graph:  # graful problemei
    def __init__(self, nume_fisier):
        try:
            self.start, self.final, self.copii, self.adiacente = parser.parse(nume_fisier)
        except Exception as e:
            raise e

    def testeaza_scop(self, nodCurent):
        return nodCurent.info == self.final

    @staticmethod
    def obtineDirectie(index1, index2): # obtine directia biletului
        directie = None
        row = index1 // 6
        column = index1 % 6
        to_row = index2 // 6
        to_column = index2 % 6

        if row < to_row:
            directie = "v"
        elif row > to_row:
            directie = "^"
        
        # daca row == to_row
        if column > to_column:
            directie = "<"
            if to_column % 2 != 0: # dinspre o coloana la interval spre stanga
                directie = "<<"
        elif column < to_column:
            directie = ">"
            if to_column % 2 == 0: # dinspre o coloana la interval spre dreapta
                directie = ">>"
        return directie

    def genereazaSuccesori(self, nodCurent):
        listaSuccesori = []

        index = self.copii.index(nodCurent.info)

        for i in range(len(self.adiacente)):
            if self.adiacente[index][i] == 1 and not nodCurent.contineInDrum(self.copii[i]):

                listaSuccesori.append(NodParcurgere(self.copii[i], nodCurent.g + 1, nodCurent, Graph.obtineDirectie(index, i)))

        return listaSuccesori


def uniform_cost(gr, nrSolutiiCautate):
    NodParcurgere.is_counting = True
    alg_time = []
    start_time = time.time() # Inceputul algoritmului
    c = [NodParcurgere(gr.start, 0, None)]

    max_noduri = 0

    results = []

    while len(c) > 0:
        max_noduri = max(NodParcurgere.total_instantiations - NodParcurgere.total_deletions, max_noduri)
        nodCurent = c.pop(0)

        if gr.testeaza_scop(nodCurent):
            results.append(nodCurent.afisDrum())
            
            alg_time.append((time.time() - start_time) * 100)

            nrSolutiiCautate -= 1
            if nrSolutiiCautate == 0:
                instantiations = NodParcurgere.total_instantiations
                deletions = NodParcurgere.total_deletions

                ## Resetting the object counter
                NodParcurgere.total_instantiations = 0
                NodParcurgere.total_deletions = 0
                NodParcurgere.is_counting = False

                return (results, max_noduri, instantiations, alg_time)
        lSuccesori = gr.genereazaSuccesori(nodCurent)
        for s in lSuccesori:
            i = 0
            while i < len(c):
                if c[i].g > s.g:
                    break
                i += 1
            c.insert(i, s)
    
    instantiations = NodParcurgere.total_instantiations
    deletions = NodParcurgere.total_deletions

    ## Resetting the object counter
    NodParcurgere.total_instantiations = 0
    NodParcurgere.total_deletions = 0
    NodParcurgere.is_counting = False
    if results == []:
        return (["Nu exista cale\n"], max_noduri, instantiations, [(time.time() - start_time) * 1000])
    else:
        return (results, max_noduri, instantiations, alg_time)

@stopit.threading_timeoutable(default='UCS timed out')
def ucs_timeout(input_path, NSOL):
    gr = Graph(input_path)
    return uniform_cost(gr, nrSolutiiCautate=NSOL)
