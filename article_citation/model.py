import math
from enum import Enum, EnumMeta
import networkx as nx
import numpy as np

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.datacollection import DataCollector
from mesa.space import NetworkGrid


class State(Enum):
    SUSCEPTIBLE = 0
    INFECTED = 1
    RESISTANT = 2

class Art_State(Enum):
    ESCRITO = 0
    PUBLICADO = 1
    NAO_PUBLICADO = 2


def number_state(model, state):
    return sum([1 for a in model.grid.get_all_cell_contents() if a.state is state])


def number_infected(model):
    return number_state(model, State.INFECTED)


def number_susceptible(model):
    return number_state(model, State.SUSCEPTIBLE)


def number_resistant(model):
    return number_state(model, State.RESISTANT)


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


def get_art_citation(model: Model):

    art_cite_freq = dict()

    for art in model.schedule.agents:
        art_cite_freq[art.unique_id] = 0

    for art in model.schedule.agents:
        for cite_article in art.reference_articles:
            art_cite_freq[cite_article.unique_id] += 1

    return art_cite_freq

class ArticlesProductModel(Model):
    """An article production model with a very simple functionality"""

    def __init__(
        self,
        num_max_authors=100,
        avg_node_degree=3,
        # initial_outbreak_size=1,
        # virus_spread_chance=0.4,
        # virus_check_frequency=0.4,
        # recovery_chance=0.3,
        # gain_resistance_chance=0.5,
        num_max_articles = 750
    ):

        self.num_max_articles = num_max_articles
        self.num_max_authors = num_max_authors
        # prob = avg_node_degree / self.num_max_articles
        self.G = nx.DiGraph()
        # self.G = nx.erdos_renyi_graph(n=self.num_max_articles, p=prob)
        
        self.grid = NetworkGrid(self.G)
        self.schedule = RandomActivation(self)
        self.art_idx = 0

        # self.initial_outbreak_size = (
        #     initial_outbreak_size if initial_outbreak_size <= num_nodes else num_nodes
        # )
        # self.virus_spread_chance = virus_spread_chance
        # self.virus_check_frequency = virus_check_frequency
        # self.recovery_chance = recovery_chance
        # self.gain_resistance_chance = gain_resistance_chance

        self.datacollector = DataCollector(
            {
                # "Infected": number_infected,
                # "Susceptible": number_susceptible,
                # "Resistant": number_resistant,

                "Media" : get_mean_citation,
                "Mediana" : get_median_citation,
                "Moda" : get_mode_citation,
                "Grau de citacoes por artigo": get_art_citation
            }
        )


        for i in range(15):
            # max_cite_num = self.random.randint(0, self.num_max_articles)
            new_article = Article(self.art_idx, self)
            self.art_idx += 1
            
            # temp = dict()
            # temp["agent"] = []

            # art.cite_arts()
            self.G.add_node(new_article.unique_id, agent = [])
            
            self.grid.place_agent(new_article, new_article.unique_id)
            self.schedule.add(new_article)
        
        # Create agents
        # for i, node in enumerate(self.G.nodes()):
        #     a = VirusAgent(
        #         i,
        #         self,
        #         State.SUSCEPTIBLE,
        #         self.virus_spread_chance,
        #         self.virus_check_frequency,
        #         self.recovery_chance,
        #         self.gain_resistance_chance,
        #     )
        #     self.schedule.add(a)
        #     # Add the agent to the node
        #     self.grid.place_agent(a, node)

        # Infect some nodes
        # infected_nodes = self.random.sample(self.G.nodes(), self.initial_outbreak_size)
        # for a in self.grid.get_cell_list_contents(infected_nodes):
        #     a.state = State.INFECTED

        self.running = True
        self.datacollector.collect(self)

    # def resistant_susceptible_ratio(self):
    #     try:
    #         return number_state(self, State.RESISTANT) / number_state(
    #             self, State.SUSCEPTIBLE
    #         )
    #     except ZeroDivisionError:
    #         return math.inf

    def step(self):
        self.schedule.step()

        # A cada passo, um artigo deve ser criado, e este novo artigo deve citar os artigos existentes,
        # baseado em alguma logica (pode ser de forma aleatoria, ou nao...).

        # Faca aqui a logica
        if(len(self.schedule.agents) < self.num_max_articles):
            new_article = Article(self.art_idx, self)
            self.art_idx += 1

            new_article.cite_arts()
            
            # for art in new_article.reference_articles:
            #     self.G.add_edge(new_article.unique_id, art.unique_id)

            # temp = dict()
            # temp["agent"] = []
            # self.G.add_node(new_article.unique_id, agent = new_article)
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

        self.reference_articles = []
        # self.references = []

        # mean_cite = get_mean_citation(self.model)
        self.max_cite_art = int(self.random.normalvariate(30, 6))
        # self.max_cite_art = self.random.randint(0, len(self.model.schedule.agents))

    def step(self):
        pass
    
    def cite_arts(self):
        
        # dg_dict = self.model.G.in_degree(self.model.G.nodes())

        if(len(self.model.schedule.agents) > 0):
            for i in range(self.max_cite_art):
                cited_art = self.random.choice(self.model.schedule.agents)
                self.reference_articles.append(cited_art)

        for art in self.reference_articles:
            self.model.G.add_edge(self.unique_id, art.unique_id)

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
