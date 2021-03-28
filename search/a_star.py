####################################################################################
#                                  A *  |   A * OPT                                #
####################################################################################


import sys
import os
sys.path.insert(1, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))
from input_parser import parse as parser
import stopit
import time
from math import sqrt

# informatii despre un nod din arborele de parcurgere (nu din graful initial)
class NodParcurgere:
    graph = None

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

    def __str__(self):
        return self.info


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


    def genereazaSuccesori(self, nodCurent, tip_euristica="euristica banala"):
        def conditie(indexCopil2):
            """

            Args:
                indexCopil2(integer): indexul copilului la care ar ajunge mesajul in self.copii
            
            Verificam ca mai exista cel putin 1 copil caruia nodul curent poate
            sa-i transmita biletul
            """
            return sum(self.adiacente[indexCopil2]) > 1 # Are cel putin muchia de intoarcere, deci mai trebuie macar una.
        
        listaSuccesori = []

        # Biletul se afla la nodul curent
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

    def euristica_euclidiana(self, index):
        """
        Euristica Euclidiana

        Args:
            index ([int]): Din index-ul in lista de copii putem creea "coordonatele" in clasa.

        Returns:
            [float]: Distanta euclidiana dintre punctul care se afla la ```index``` si punctul final. 
        """
        row = index // 6
        column = index % 6

        index_final = self.copii.index(self.final)
        final_row = index_final // 6
        final_column = index_final % 6

        return sqrt((final_row - row)**2 + (final_column - column)**2)

    # euristici
    def calculeaza_h(self, index, currentCost, tip_euristica="euristica banala"):
        if tip_euristica == "euristica banala":
            if self.copii[index] != self.final:
                return 1
            return 0
        elif tip_euristica == "euristica manhattan":
            return self.euristica_manhattan(index)
        elif tip_euristica == "euristica euclidiana":
            return self.euristica_euclidiana(index)
        else:
            # Euristica creste in functie de pozitia copilului in clasa, si e complet independenta
            # de orice distanta fata de copilul scop. Astfel, exista cazul in care un copil mai apropiat 
            # de scop va avea o euristica mai mare decat unul mai departat.
            #
            # Ridicarea la patrat doar exagereaza diferentele.
            return index ** 2

def a_star(graph, nrSolutiiCautate, tip_euristica):
    NodParcurgere.is_counting = True
    c = [NodParcurgere(graph.start, 0, graph.calculeaza_h(graph.copii.index(graph.start), 0, tip_euristica), None, None)]
    alg_time = []
    start_time = time.time() # Inceputul algoritmului
    results = []
    max_noduri = 0

    while len(c) > 0:
        max_noduri = max(NodParcurgere.total_instantiations - NodParcurgere.total_deletions, max_noduri)
        nodCurent = c.pop(0)

        if graph.testeaza_scop(nodCurent):
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
        lSuccesori = graph.genereazaSuccesori(nodCurent, tip_euristica=tip_euristica)
        for s in lSuccesori:
            i = 0
            gasit_loc = False
            for i in range(len(c)):
                if c[i].estimare >= s.estimare:
                    gasit_loc = True
                    break
            if gasit_loc:
                c.insert(i, s)
            else:
                c.append(s)
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

def a_star_opt(graph, tip_euristica):
    NodParcurgere.is_counting = True
    c = [NodParcurgere(graph.start, 0, graph.calculeaza_h(graph.copii.index(graph.start), 0, tip_euristica), None, None)]
    closed = []

    start_time = time.time()

    max_noduri = 0

    while len(c) > 0:
        max_noduri = max(NodParcurgere.total_instantiations - NodParcurgere.total_deletions, max_noduri)
        nodCurent = c.pop(0)
        closed.append(nodCurent)

        if graph.testeaza_scop(nodCurent):
            t = time.time() - start_time
            instantiations = NodParcurgere.total_instantiations
            deletions = NodParcurgere.total_deletions

            ## Resetting the object counter
            NodParcurgere.total_instantiations = 0
            NodParcurgere.total_deletions = 0
            NodParcurgere.is_counting = False

            return ([nodCurent.afisDrum()], max_noduri, instantiations, [t * 100])

        lSuccesori = graph.genereazaSuccesori(nodCurent, tip_euristica)
        lSuccesoriCopy = lSuccesori.copy()
        for s in lSuccesoriCopy:
            gasitOpen = False
            for elem in c:
                if s.info == elem.info:
                    gasitOpen = True
                    if s.estimare < elem.estimare:
                        c.remove(elem)
                    else:
                        lSuccesori.remove(s)
                    break
            if not gasitOpen:
                for elem in closed:
                    if s.info == elem.info:
                        if s.estimare < elem.estimare:
                            closed.remove(elem)
                        else:
                            lSuccesori.remove(s)
                        break

        for s in lSuccesori:
            i = 0
            while i < len(c):
                if c[i].estimare >= s.estimare:
                    break
                i += 1
            c.insert(i, s)
    instantiations = NodParcurgere.total_instantiations
    deletions = NodParcurgere.total_deletions

    ## Resetting the object counter
    NodParcurgere.total_instantiations = 0
    NodParcurgere.total_deletions = 0
    NodParcurgere.is_counting = False
    return (["Nu exista cale\n"], max_noduri, instantiations, [(time.time() - start_time) * 1000])


@stopit.threading_timeoutable(default='A* timed out')
def a_star_timeout(input_path, NSOL, euristica):
    graph = Graph(input_path)
    NodParcurgere.graph = graph
    return a_star(graph, NSOL, euristica)


@stopit.threading_timeoutable(default='A* OPT timed out')
def a_star_opt_timeout(input_path, euristica):
    graph = Graph(input_path)
    NodParcurgere.graph = graph
    return a_star_opt(graph, euristica)