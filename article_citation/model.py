import math
from enum import Enum, EnumMeta
import networkx as nx
import numpy as np

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid

class Art_State(Enum):
    ESCRITO = 0
    PUBLICADO = 1
    NAO_PUBLICADO = 2

def get_mean_citation(model: Model):

    total_cite = sum([len(art.reference_articles) for art in model.schedule.agents])

    num_art = len(model.schedule.agents)
    if(num_art == 0):
        return 0.0

    return total_cite / num_art

def get_median_citation(model: Model):

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

    # print(len(artigo.reference_articles), sep = ' ')
    return len(artigo.reference_articles)


class ArticlesProductModel(Model):
    """An article production model with a very simple functionality"""

    def __init__(
        self,
        num_max_authors=100,
        avg_node_degree=3,
        num_acceptable_articles = 50,
        # initial_outbreak_size=1,
        # virus_spread_chance=0.4,
        # virus_check_frequency=0.4,
        # recovery_chance=0.3,
        # gain_resistance_chance=0.5,
        num_max_articles = 750
    ):

        self.num_max_articles = num_max_articles
        self.num_acceptable_articles = num_acceptable_articles
        self.num_max_authors = num_max_authors
        self.G = nx.DiGraph()
        
        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)
        self.art_idx = 0

        
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
        # baseado em alguma logica (pode ser de forma aleatoria, ou nao...).

        # Faca aqui a logica
        if(len(self.schedule.agents) < self.num_max_articles):
            new_article = Article(self.art_idx, self)
            self.art_idx += 1

            new_article.cite_arts()
            
            
            self.G.add_node(new_article.unique_id, agent = [])

            self.grid.place_agent(new_article, new_article.unique_id)
            self.schedule.add(new_article)
        # collect data
        self.datacollector.collect(self)

    def run_model(self, n):
        for i in range(n):
            self.step()

class Article(Agent):
    def __init__(self, unique_id: int, model: Model) -> None:
        super().__init__(unique_id, model)

        # Listas que contem as referencias para os artigos
        self.reference_articles = [] # Contem referencias para outros artigos, que sao unicas
        self.citations = [] # Contem as citacoes, que podem ser repetir
        self.num_citations = 0
        self.num_references = 0

        self.aux_reference_articles = []
        self.aux_citations = []

        if(len(self.model.schedule.agents) < self.model.num_acceptable_articles):
            mu = len(self.model.schedule.agents) // 2
            sigma = 5
        
        else:
            mu = 40
            sigma = 20

        self.max_cite_art = int(self.random.normalvariate(mu, sigma))
        
        # self.max_cite_art = self.random.randint(0, len(self.model.schedule.agents))


    def step(self):
        pass
    
    def cite_arts(self):
        
        dg_dict = self.model.G.degree(self.model.G.nodes())

        # print(dg_dict)
        dg_list = list(dg_dict)
        # print(len(dg_list))
        # dg_list.sort(key = lambda x:x[1], reverse = True)

        dg_list = [value + 1 for key, value in dg_list]
        # total = sum([peso for key, peso in dg_list])
        # total += (len(dg_list))
        
        # print("sua lista")
        # dg_list = [(key, (value / total)) for key, value in dg_list]
        # print(dg_list)
        # weight_dict = {}
        # curr_tot_weight = 0
        # for key, weight in dg_list:
        #     weight_dict[(curr_tot_weight, (curr_tot_weight+weight))] = key
        #     curr_tot_weight+=weight
        # print(weight_dict)
        # random_weight = self.random.random()

        if(len(self.model.schedule.agents) > 0):
            for i in range(self.max_cite_art):
                
                cited_art = self.random.choices(self.model.schedule.agents, weights = dg_list, k = 1, cum_weights = None)[0]
                # cited_art = self.random.choice(self.model.schedule.agents)
                self.citations.append(cited_art)
                self.aux_citations.append(str(cited_art.unique_id))

        self.reference_articles = list(set(self.citations))

        self.num_citations = len(self.citations)
        self.num_references = len(self.reference_articles)
        
        
        for art in self.reference_articles:
            self.model.G.add_edge(self.unique_id, art.unique_id)

            self.aux_reference_articles.append(str(art.unique_id))

# class VirusAgent(Agent):
#     def __init__(
#         self,
#         unique_id,
#         model,
#         initial_state,
#         virus_spread_chance,
#         virus_check_frequency,
#         recovery_chance,
#         gain_resistance_chance,
#     ):
#         super().__init__(unique_id, model)

#         self.state = initial_state

#         self.virus_spread_chance = virus_spread_chance
#         self.virus_check_frequency = virus_check_frequency
#         self.recovery_chance = recovery_chance
#         self.gain_resistance_chance = gain_resistance_chance

#     def try_to_infect_neighbors(self):
#         neighbors_nodes = self.model.grid.get_neighbors(self.pos, include_center=False)
#         susceptible_neighbors = [
#             agent
#             for agent in self.model.grid.get_cell_list_contents(neighbors_nodes)
#             if agent.state is State.SUSCEPTIBLE
#         ]
#         for a in susceptible_neighbors:
#             if self.random.random() < self.virus_spread_chance:
#                 a.state = State.INFECTED

#     def try_gain_resistance(self):
#         if self.random.random() < self.gain_resistance_chance:
#             self.state = State.RESISTANT

#     def try_remove_infection(self):
#         # Try to remove
#         if self.random.random() < self.recovery_chance:
#             # Success
#             self.state = State.SUSCEPTIBLE
#             self.try_gain_resistance()
#         else:
#             # Failed
#             self.state = State.INFECTED

#     def try_check_situation(self):
#         if self.random.random() < self.virus_check_frequency:
#             # Checking...
#             if self.state is State.INFECTED:
#                 self.try_remove_infection()

#     def step(self):
#         if self.state is State.INFECTED:
#             self.try_to_infect_neighbors()
#         self.try_check_situation()
