from functools import reduce

class MalformedInputException(Exception):
    """Exceptie pentru fisier de input care nu respecta formatul.

    Args:
        Exception (string): Mesajul de eroare
    """
    pass

class EarlyNoSolution(Exception):
    """Exceptie pentru cazul in care e trivial de verificat ca 

    Args:
        Exception (string): Mesajul de eroare
    """
    pass

def parse(input_file):
    """
    Parseaza fisierul primit ca parametru si returneaza
    un vector cu numele copiilor si o matrice de adiacenta.

    Args:
        input_file (string): calea fisierului care trebuie citit

    Returns:
        start (string): copilul de la care pleaca mesajul
        final (string): copilul la care trebuie sa ajunga mesajul
        copii ([string]): lista de copii. Contine si locurile libere
        clasa ([[string]]): reprezentarea clasei in matrice
        adiacente ([[int]]): matricea de adiacente
    """
    clasa = []
    adiacente = []
    suparati = []
    start = None
    final = None
    _before_suparati = True             # inaintea liniei care separa clasa de copiii suparati
    with open(input_file) as f:
        lines = list(f.readlines())
        for line in lines:               # Procesam fiecare linie
            l = line.replace("\n", "").split()
            if _before_suparati:
                if l[0] == "suparati":
                    _before_suparati = False
                    continue
                clasa.append(l)
            else:
                if l[0] == "mesaj:":
                    start = l[1]
                    final = l[3]
                else:
                    suparati.append((l[0], l[1]))

    ## Construim adiacentele
    ##
    ## len(clasa) = numarul de randuri din clasa. 
    ## 6 copii pe fiecare rand => numarul de copii = 6 * len(clasa)
    adiacente = list([0] * (6 * len(clasa)) for _ in range(6 * len(clasa)))

    def _nesuparati(copil1, copil2):
        return (copil1, copil2) not in suparati and (copil2, copil1) not in suparati

    ## coloana de la stanga
    for i in range(len(clasa)):
        for j in range(6):

            if j % 2 == 0: ## drumuri orizontale pe cele 3 coloane
                
                if _nesuparati(clasa[i][j], clasa[i][j+1]) and\
                    clasa[i][j] != "liber" and clasa[i][j+1] != "liber":
                    adiacente[i * 6 + j][i * 6 + j + 1] = 1
                    adiacente[i * 6 + j + 1][i * 6 + j] = 1
            
            if i < len(clasa) - 1: # drumuri verticale de la primul rand pana la ultimul rand - 1

                if clasa[i][j] != "liber" and clasa[i+1][j] != "liber" and\
                    _nesuparati(clasa[i][j], clasa[i+1][j]):
                    adiacente[i * 6 + j][(i + 1) * 6 + j] = 1
                    adiacente[(i + 1) * 6 + j][i * 6 + j] = 1
            
            if (j == 1 or j == 3) and (i >= len(clasa) - 2): # transferul intre ultimele si penultimele banci

                if _nesuparati(clasa[i][j], clasa[i][j+1]) and\
                    clasa[i][j] != "liber" and clasa[i][j+1] != "liber":
                    adiacente[i * 6 + j][i * 6 + j + 1] = 1
                    adiacente[i * 6 + j + 1][i * 6 + j] = 1


    ## Vector de copii
    copii = reduce(lambda x, y: x + y, clasa, []) ## pastram locurile libere ca sa putem potrivi indicii

    if copii == [] or start is None or final is None: ## Fisierul e gol sau formatul gresit. Bail out
        raise MalformedInputException("Malformed input file. Bailing.")
    
    start_index = copii.index(start)
    final_index = copii.index(final)
    
    if sum(adiacente[start_index]) < 1 or sum(adiacente[final_index]) < 1:
        raise EarlyNoSolution("Nu poate exista o solutie.")

    return start, final, copii, adiacente
