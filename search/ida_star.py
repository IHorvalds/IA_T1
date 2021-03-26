##############################################################################################
#                                            IDA *                                           #
##############################################################################################

import sys
import os
sys.path.insert(1, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))
from input_parser import parse as parser
import stopit
import time
from math import sqrt

class NodParcurgere:
    graf = None  # static

    # Object counters
    total_instantiations = 0
    total_deletions = 0
    is_counting = False

    def __init__(self, info, cost, h=0, parinte=None, directie=None):
        self.info = info
        self.cost = cost
        self.euristica = h
        self.estimare = self.cost + self.euristica
        self.parinte = parinte      # parintele din arborele de parcurgere
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
        path += "\nlungime: {}\ncost: {}\n".format(len(l), self.cost)
        return path

    def contineInDrum(self, infoNodNou):
        nodDrum = self
        while nodDrum is not None:
            if infoNodNou == nodDrum.info:
                return True
            nodDrum = nodDrum.parinte

        return False

    def __repr__(self):
        return self.info


class Graph:  # graful problemei
    def __init__(self, nume_fisier):
        try:
            self.start, self.final, self.copii, self.clasa, self.adiacente = parser.parse(nume_fisier)
        except parser.MalformedInputException as e:
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

    def euristica_manhattan(self, index):
        """
        Euristica Manhattan

        Args:
            index (integer): Din index-ul in lista de copii putem creea "coordonatele" in clasa.

        Returns:
            [integer]: Distanta Manhattan dintre punctul care se afla la ```index``` si punctul final
        """
        row = index // 6
        column = index % 6

        index_final = self.copii.index(self.final)
        final_row = index_final // 6
        final_column = index_final % 6

        return abs(final_column - column) + abs(final_row - row)

    def euristica_euler(self, index):
        """
        Euristica Euleriana

        Args:
            index ([int]): Din index-ul in lista de copii putem creea "coordonatele" in clasa.

        Returns:
            [float]: Distanta euleriana dintre punctul care se afla la ```index``` si punctul final. 
        """
        row = index // 6
        column = index % 6

        index_final = self.copii.index(self.final)
        final_row = index_final // 6
        final_column = index_final % 6

        return sqrt((final_row - row)**2 + (final_column - column)**2)

    # euristici
    def calculeaza_h(self, index, currentCost, tip_euristica="banala"):
        if tip_euristica == "euristica banala":
            if self.copii[index] != self.final:
                return 1
            return 0
        elif tip_euristica == "euristica manhattan":
            return self.euristica_manhattan(index)
        elif tip_euristica == "euristica euler":
            return self.euristica_euler(index)
        else:
            # Euristica creste in functie de pozitia copilului in clasa, si e complet independenta
            # de orice distanta fata de copilul scop. Astfel, exista cazul in care un copil mai apropiat 
            # de scop va avea o euristica mai mare decat unul mai departat.
            #
            # Ridicarea la patrat doar exagereaza diferentele.
            return index ** 2

    # va genera succesorii sub forma de noduri in arborele de parcurgere
    def genereazaSuccesori(self, nodCurent, tip_euristica="banala"):
        def conditie(indexCopil2):
            """

            Args:
                indexCopil1(integer): indexul copilului de la care ar pleaca mesajul in self.copii
                indexCopil2(integer): indexul copilului la care ar ajunge mesajul in self.copii
            
            Verificam ca mai exista cel putin 1 copil caruia nodul curent poate
            sa-i transmita biletul
            """
            return sum(self.adiacente[indexCopil2]) > 1 # Are cel putin muchia de intoarcere, deci mai trebuie macar una.

        listaSuccesori = []
        indexCurent = self.copii.index(nodCurent.info)
        for index in range(len(self.adiacente)):
            if self.adiacente[indexCurent][index] == 1:
                if conditie(index) and not nodCurent.contineInDrum(self.copii[index]):

                    listaSuccesori.append(
                        NodParcurgere(
                            self.copii[index],
                            nodCurent.cost + 1,
                            self.calculeaza_h(index, nodCurent.cost + 1, tip_euristica),
                            nodCurent,
                            Graph.obtineDirectie(indexCurent, index)
                        )
                    )
        return listaSuccesori

    def __repr__(self):
        sir = ""
        for (k, v) in self.__dict__.items():
            sir += "{} = {}\n".format(k, v)
        return sir



def ida_star(gr, nrSolutiiCautate, euristica):
    NodParcurgere.is_counting = True
    start_time = time.time()
    results = []
    times = []

    start_index = gr.copii.index(gr.start)
    limita = gr.calculeaza_h(start_index, 0)
    nodStart = NodParcurgere(gr.start, 0, limita, None, None)

    while True:
        nrSolutiiCautate, rez = construieste_drum(gr, nodStart, limita, nrSolutiiCautate, euristica, times, start_time, results)
        if rez == "gata":
            break
        if rez == float("inf"):
            if results == []:
                results.append("Nu exista drum\n")
                times.append((time.time() - start_time) * 1000)
            break
        limita = rez

    instantiations = NodParcurgere.total_instantiations
    deletions = NodParcurgere.total_deletions

    ## Resetting the object counter
    NodParcurgere.total_instantiations = 0
    NodParcurgere.total_deletions = 0
    NodParcurgere.is_counting = False

    return (results, (instantiations - deletions), instantiations, times)


def construieste_drum(gr, nodCurent, limita, nrSolutiiCautate, euristica, times, start_time, results):

    if nodCurent.estimare > limita:
        return nrSolutiiCautate, nodCurent.estimare
    if gr.testeaza_scop(nodCurent) and nodCurent.estimare == limita:

        times.append((time.time() - start_time) * 1000)
        results.append(nodCurent.afisDrum())
        nrSolutiiCautate -= 1
        if nrSolutiiCautate == 0:
            return nrSolutiiCautate, "gata"
    lSuccesori = gr.genereazaSuccesori(nodCurent, euristica)
    minim = float("inf")
    for s in lSuccesori:
        nrSolutiiCautate, rez = construieste_drum(gr, s, limita, nrSolutiiCautate, euristica, times, start_time, results)
        if rez == "gata":
            return nrSolutiiCautate, "gata"
        if rez < minim:
            minim = rez
    return nrSolutiiCautate, minim

@stopit.threading_timeoutable(default='IDA* timed out')
def ida_star_timeout(input_path, nsol, euristica):
    graph = Graph(input_path)
    NodParcurgere.graph = graph
    return ida_star(graph, nsol, euristica)
