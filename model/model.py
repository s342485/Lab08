from database.impianto_DAO import ImpiantoDAO

'''
    MODELLO:
    - Rappresenta la struttura dati
    - Si occupa di gestire lo stato dell'applicazione
    - Interagisce con il database
'''

class Model:
    def __init__(self):
        self._impianti = None #prima di chiamare load_impianti è vuota
        self.load_impianti()

        self.__sequenza_ottima = []
        self.__costo_ottimo = -1
        self._lista_per_mese = []

    def load_impianti(self):
        """ Carica tutti gli impianti e li setta nella variabile self._impianti """
        self._impianti = ImpiantoDAO.get_impianti()

    def get_consumo_medio(self, mese:int):
        """
        Calcola, per ogni impianto, il consumo medio giornaliero per il mese selezionato.
        :param mese: Mese selezionato (un intero da 1 a 12)
        :return: lista di tuple --> (nome dell'impianto, media), es. (Impianto A, 123)
        """
        somma_mensile = 0
        contatore = 0
        for impianto in self._impianti:
            consumi = impianto.get_consumi()
            impianto_corrente = impianto.nome
            for consumo in consumi:
                consumo_mensile = consumo.data.month
                if mese == consumo_mensile:
                    somma_mensile = somma_mensile + consumo.kwh
                    contatore += 1

            media = round((somma_mensile / contatore) , 2)
            self._lista_per_mese.append((impianto_corrente,media))


        return self._lista_per_mese

    def get_sequenza_ottima(self, mese:int):
        """
        Calcola la sequenza ottimale di interventi nei primi 7 giorni
        :return: sequenza di nomi impianto ottimale
        :return: costo ottimale (cioè quello minimizzato dalla sequenza scelta)
        """
        #resetto i risultati cosi ogni volta che premo il pulsante il model riparte da zero
        self.__sequenza_ottima = []
        self.__costo_ottimo = -1

        consumi_settimana = self.__get_consumi_prima_settimana_mese(mese)

        id_impianti = [impianto.id for impianto in self._impianti]
        consumi_tuple = []


        for giorno in range(7):
            consumi_giorno = []
            for id in id_impianti:
                consumi_giorno.append(consumi_settimana[id][giorno])
            consumi_tuple.append(consumi_giorno)

        # avvio da giorno 0
        self.__ricorsione([], 0, None, 0, consumi_tuple)

        # Traduzione in nomi
        id_to_nome = {impianto.id: impianto.nome for impianto in self._impianti}
        sequenza_nomi = [
            f"Giorno {giorno}: {id_to_nome[i]}"
            for giorno, i in enumerate(self.__sequenza_ottima, start=1)
        ]
        return sequenza_nomi, self.__costo_ottimo

    def __ricorsione(self, sequenza_parziale, giorno, ultimo_impianto,
                     costo_corrente, consumi_settimana):

        # Ricavo gli ID degli impianti
        id_impianti = [imp.id for imp in self._impianti]

        #  CONDIZIONE TERMINALE
        if len(sequenza_parziale) == 7:
            if self.__costo_ottimo == -1 or costo_corrente < self.__costo_ottimo:
                self.__costo_ottimo = costo_corrente
                self.__sequenza_ottima = sequenza_parziale.copy()
            return
        else:
        #  CONDIZIONE RICORSIVA
            #se non ho ancora 7 giorni vado avanti
            consumi_giorno = consumi_settimana[giorno]  # lista consumi del giorno

            # Per ogni impianto disponibile
            for indice, id_impianto in enumerate(id_impianti):

                consumo_del_giorno = consumi_giorno[indice]
                nuovo_costo = costo_corrente + consumo_del_giorno

                # costo di spostamento
                if ultimo_impianto is not None and ultimo_impianto != id_impianto:
                    nuovo_costo += 5

                # aggiungo impianto alla sequenza temporanea
                sequenza_parziale.append(id_impianto)

                # ricorsione sul giorno successivo
                self.__ricorsione(
                    sequenza_parziale,
                    giorno + 1,
                    id_impianto,
                    nuovo_costo,
                    consumi_settimana
                )

                # backtracking
                sequenza_parziale.pop()

    def __get_consumi_prima_settimana_mese(self, mese: int):
        """
        Restituisce i consumi dei primi 7 giorni del mese selezionato per ciascun impianto.
        :return: un dizionario: {id_impianto: [kwh_giorno1, ..., kwh_giorno7]}
        """
        consumi_settimana = {}

        for impianto in self._impianti:
            consumi = impianto.get_consumi()
            consumi_mese = []

            # prendo solo quelli del mese selezionato
            for consumo in consumi:
                if consumo.data.month == mese:
                    consumi_mese.append((consumo.data.day, consumo.kwh))

            # ordino la lista (giorno, kwh)
            consumi_mese.sort(key=lambda x: x[0])

            # prendo i primi 7 valori di kwh
            lista_kwh = []
            for giorno, kwh in consumi_mese[:7]:
                lista_kwh.append(kwh)

            # aggiungo al dizionario usando l’ID dell’impianto come chiave
            consumi_settimana[impianto.id] = lista_kwh

        return consumi_settimana
