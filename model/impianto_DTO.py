from dataclasses import dataclass
from database.consumo_DAO import ConsumoDAO

'''
    DTO (Data Transfer Object) dell'entità Impianto
'''

@dataclass()
class Impianto:
    id: int
    nome: str
    indirizzo: str

    # RELAZIONI
    lista_consumi: list = None

    def get_consumi(self):
        self.lista_consumi = [] # la inizializzo a lista
        consumi = ConsumoDAO().get_consumi(self.id) #mi prendo i consumi propri dell impianto con id dal database
        for consumo in consumi:
            self.lista_consumi.append(consumo) #popolo la lista con i consumi
        return self.lista_consumi

    def __eq__(self, other):
        return isinstance(other, Impianto) and self.id == other.id

    def __str__(self):
        return f"{self.id} | {self.nome} | Indirizzo: {self.indirizzo}"

    def __repr__(self):
        return f"{self.id} | {self.nome} | Indirizzo: {self.indirizzo}"

