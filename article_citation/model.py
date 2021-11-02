import math
from enum import Enum, EnumMeta
import networkx as nx
import numpy as np

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid

# Alguns estados possiveis para artigos,
# mas que nao foram utilizados no modelo
class Art_State(Enum):
    ESCRITO = 0
    PUBLICADO = 1
    NAO_PUBLICADO = 2

def get_mean_citation(model: Model):
    """ Retorna a media da quantidade de referencias dos artigos do modelo. """
    total_cite = sum([len(art.reference_articles) for art in model.schedule.agents])

    num_art = len(model.schedule.agents)
    if(num_art == 0):
        return 0.0

    return total_cite / num_art

def get_median_citation(model: Model):
    """ Retorna a mediana da quantidade de referencias dos artigos do modelo. """
    num_of_citations = [len(art.reference_articles) for art in model.schedule.agents]

    num_of_citations.sort()
    
    median = 0
    len_cite_list = len(num_of_citations)

    if(len_cite_list > 0):
        if(len_cite_list % 2 == 0):
            median = (num_of_citations[len_cite_list // 2 - 1] + num_of_citations[len_cite_list // 2]) / 2
        else:
            median = num_of_citations[len_cite_list // 2]

    return median


def get_mode_citation(model: Model):
    """ Retorna a moda da quantidade de referencias dos artigos do modelo. """
    num_of_citations = [len(art.reference_articles) for art in model.schedule.agents]

    max_mode_num = 0
    mode = 0
    map_citations = dict()

    for cn in num_of_citations:
        map_citations[cn] = 0

    for cn in num_of_citations:
        map_citations[cn] += 1

    # print(map_citations)
    for k, value in map_citations.items():

        if(max_mode_num <= value):
            mode = k
            max_mode_num = value

    return mode


def get_art_citation(artigo: Agent):
    """ Retorna a quantidade total de referencias feitas por um artigo """
    # print(len(artigo.reference_articles), sep = ' ')
    return len(artigo.reference_articles)


class ArticlesProductModel(Model):
    """Um modelo de produção de artigos com uma funcionalidade bem simples, que tenta simular
    a citação de artigos ao longo do tempo. Os detalhes sobre a produção e outros aspectos 
    dos artigos foram abstraídos, e o foco foi dado à citação feita pelos artigos """

    def __init__(
        self,
        num_max_authors=100,
        avg_node_degree=3,
        num_acceptable_articles = 50,
        num_max_articles = 750
    ):

        self.num_max_articles = num_max_articles

        # Controla o numero inicial de artigos que terao uma quantidade de citacoes abaixo do normal
        self.num_acceptable_articles = num_acceptable_articles
        self.num_max_authors = num_max_authors
        self.G = nx.DiGraph()
        
        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)
        
        # Controla o indice dos artigos
        self.art_idx = 0

        
        # Coletor de dados utilizado pelo mesa, para apresentar na simulacao interativa alguns 
        # dados interessantes
        self.datacollector = DataCollector(
            model_reporters = {
                "Media" : get_mean_citation,
                "Mediana" : get_median_citation,
                "Moda" : get_mode_citation,
                
            },
            agent_reporters = {
                "Num citacoes Art": "num_citations",
                "Num referencias Art" : "num_references",
            },
        )

        # Criando uma quantidade inicial de artigos, sem nenhuma citacao
        for i in range(10):
            new_article = Article(self.art_idx, self)
            self.art_idx += 1
            
            self.G.add_node(new_article.unique_id, agent = [])
            
            self.grid.place_agent(new_article, new_article.unique_id)
            self.schedule.add(new_article)
        

        self.running = len(self.schedule.agents) <= self.num_max_articles
        self.datacollector.collect(self)

    
    def step(self):
        self.schedule.step()

        # A cada passo, um artigo deve ser criado, e este novo artigo deve citar os artigos existentes,

        if(len(self.schedule.agents) < self.num_max_articles):
            new_article = Article(self.art_idx, self)
            self.art_idx += 1

            new_article.cite_arts()
            
            self.G.add_node(new_article.unique_id, agent = [])

            self.grid.place_agent(new_article, new_article.unique_id)
            self.schedule.add(new_article)
        # Coletando dados
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()

class Article(Agent):
    """ Agente que faz o papel do artigo no modelo. Nao possui steps, sendo que sua função principal 
    é citar os artigos que ja estao presentes na rede."""

    def __init__(self, unique_id: int, model: Model) -> None:
        super().__init__(unique_id, model)

        self.reference_articles = [] # Contem referencias para outros artigos, que sao unicas
        self.citations = [] # Contem as citacoes (semelhante as referencias, mas podem repetir artigos ja citados)
        self.num_citations = 0
        self.num_references = 0

        # Listas auxiliares para guardar os "nomes" (ids) dos artigos referenciados
        self.aux_reference_articles = []
        self.aux_citations = []


        # Verificando se o artigo é um dos iniciais que terao uma quantidade menor de citações 
        if(len(self.model.schedule.agents) < self.model.num_acceptable_articles):
            mu = len(self.model.schedule.agents) // 2
            sigma = 5
        
        else:
            mu = 40
            sigma = 20

        # Escolhendo um valor aleatorio de citacoes, usando uma variacao normal
        self.max_cite_art = int(self.random.normalvariate(mu, sigma))

    def step(self):
        pass
    
    def cite_arts(self):
        """ Escolhe os artigos que serao citados do modelo. Busca no modelo os artigos ja existentes, e os cita de forma 
        'aleatoria', dando preferencia a artigos com um fator de qualidade maior (aqueles que possuem uma quantidade grande de 
        citacoes, e que fazem muitas citacoes) """

        # Obtendo o grau de cada artigo, para calcular os seus pesos
        dg_dict = self.model.G.degree(self.model.G.nodes())
        dg_list = list(dg_dict)
        dg_list = [value + 1 for key, value in dg_list]


        if(len(self.model.schedule.agents) > 0):
            for i in range(self.max_cite_art):
                
                # Escolha do artigo a ser citado, usando os pesos calculados
                cited_art = self.random.choices(self.model.schedule.agents, weights = dg_list, k = 1, cum_weights = None)[0]
                
                self.citations.append(cited_art)

                self.aux_citations.append(str(cited_art.unique_id))

        # Obtendo as ocorrencias unicas de citacoes, para fazer as referencias
        self.reference_articles = list(set(self.citations))

        self.num_citations = len(self.citations)
        self.num_references = len(self.reference_articles)
        
        for art in self.reference_articles:
            self.model.G.add_edge(self.unique_id, art.unique_id)
            self.aux_reference_articles.append(str(art.unique_id))