import math
from re import I

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule, BarChartModule
from mesa.visualization.modules import NetworkModule
from mesa.visualization.modules import TextElement
# from .model import VirusOnNetwork, State, number_infected
from .model import ArticlesProductModel
# from .model import get_art_citation


def network_portrayal(G):
    # The model ensures there is always 1 agent per node

    def node_size(agent):
        # total_refs = len(agent.reference_articles)

        refs_this_art = agent.model.G.in_degree(agent.unique_id)

        refs_this_art = int(math.log(refs_this_art + 1, 1000) * 5)

        # divisao = 30

        # refs_this_art = 2 * refs_this_art // divisao

        return refs_this_art + 3

    def node_color(agent):
        # return {State.INFECTED: "#FF0000", State.SUSCEPTIBLE: "#008000"}.get(
        #     agent.state, "#808080"
        # )
        total_refs = len(agent.reference_articles)

        if(total_refs > 0):
            return "#6666ff";

        return "#ff6600"

    def edge_color(agent1, agent2):
        # if State.RESISTANT in (agent1.state, agent2.state):
        #     return "#000000"
        return "#e8e8e8"

    def edge_width(agent1, agent2):
        # if State.RESISTANT in (agent1.state, agent2.state):
        #     return 3
        return 2

    def get_agents(source, target):
        src = []
        tgt = []
        if(len(G.nodes[source]["agent"]) > 0):
            src = G.nodes[source]["agent"][0]

        
        if(len(G.nodes[target]["agent"]) > 0):
            tgt = G.nodes[target]["agent"][0]

        return src, tgt
        return G.nodes[source]["agent"][0], G.nodes[target]["agent"][0]

    portrayal = dict()
    portrayal["nodes"] = [
        {
            "size": node_size(agents[0]),
            "color": node_color(agents[0]),
            "tooltip": "id: {}<br>Citações: {}<br>Vezes citado: {}".format(
                (agents[0].unique_id if len(agents) > 0 else "none"),
                len(agents[0].reference_articles),
                agents[0].model.G.in_degree(agents[0].unique_id),
                # agents[0].unique_id, agents[0].state.name
            ),
        }
        for (_, agents) in G.nodes.data("agent")
    ]

    portrayal["edges"] = [
        {
            "source": source,
            "target": target,
            "color": edge_color(*get_agents(source, target)),
            "width": edge_width(*get_agents(source, target)),
            "directed": True,
            "arrowhead_size": 3
        }
        for (source, target) in sorted(G.edges)
    ]

    return portrayal


network = NetworkModule(network_portrayal, 500, 500, library="d3")
chart = ChartModule(
    [
        {"Label": "Media", "Color": "#000000"},
        {"Label": "Mediana", "Color": "#008000"},
        {"Label": "Moda", "Color": "#808080"},
    
        # {"Label": "Infected", "Color": "#FF0000"},
        # {"Label": "Susceptible", "Color": "#008000"},
        # {"Label": "Resistant", "Color": "#808080"},
    ]
)

# Este grafico esta com problemas de exibicao, acreditamos que seja porque 
# ele nao foi feito para o nosso tipo de simulacao (adicionar novos artigos 
# com o passar do tempo).
chart2 = BarChartModule( canvas_height=400, canvas_width=800,
    fields = [
        {"Label": "Num citacoes Art", "Color": "0000FF"
        }
    ], 
    scope='agent',
    # sorting='ascending',
)

class ChartTitle(TextElement):
    def render(self, model):
        # ratio = model.resistant_susceptible_ratio()
        # ratio_text = "&infin;" if ratio is math.inf else "{0:.2f}".format(ratio)
        # infected_text = str(number_infected(model))

        # return "Resistant/Susceptible Ratio: {}<br>Infected Remaining: {}".format(
        #     ratio_text, infected_text
        # )

        return "Medidas de tendência sobre a quantidade de referências dos artigos:"


class ChartTitle2(TextElement):
    def render(self, model):

        return "Quantidade de citações que cada artigo faz:"

model_params = {
    "num_max_articles" : UserSettableParameter(
        param_type="slider",
        name="Número máximo de artigos",
        value=100,
        min_value=10,
        max_value=2000,
        step=1,
        description="Escolha o número de artigos máximos a serem produzidos"
    ),

    "num_acceptable_articles" :  UserSettableParameter(
        param_type="slider",
        name="Número de citações médias iniciais",
        value=50,
        min_value=10,
        max_value=80,
        step=1,
        description="Escolha a quantidade de artigos que terão uma citação média inicial um pouco mais baixa"
    ),
 
    # "avg_node_degree": UserSettableParameter(
    #     "slider", "Avg Node Degree", 3, 3, 8, 1, description="Avg Node Degree"
    # ),

    # "num_max_authors" : UserSettableParameter(
    #     param_type="slider",
    #     name="Número máximo de autores",
    #     value=100,
    #     min_value=10,
    #     max_value=400,
    #     step=1,
    #     description="Escolha o número de autores que podem produzir artigos"
    # ),
    # "num_nodes": UserSettableParameter(
    #     "slider",
    #     "Number of agents",
    #     10,
    #     10,
    #     100,
    #     1,
    #     description="Choose how many agents to include in the model",
    # ),
    # "avg_node_degree": UserSettableParameter(
    #     "slider", "Avg Node Degree", 3, 3, 8, 1, description="Avg Node Degree"
    # ),
    # "initial_outbreak_size": UserSettableParameter(
    #     "slider",
    #     "Initial Outbreak Size",
    #     1,
    #     1,
    #     10,
    #     1,
    #     description="Initial Outbreak Size",
    # ),
    # "virus_spread_chance": UserSettableParameter(
    #     "slider",
    #     "Virus Spread Chance",
    #     0.4,
    #     0.0,
    #     1.0,
    #     0.1,
    #     description="Probability that susceptible neighbor will be infected",
    # ),
    # "virus_check_frequency": UserSettableParameter(
    #     "slider",
    #     "Virus Check Frequency",
    #     0.4,
    #     0.0,
    #     1.0,
    #     0.1,
    #     description="Frequency the nodes check whether they are infected by " "a virus",
    # ),
    # "recovery_chance": UserSettableParameter(
    #     "slider",
    #     "Recovery Chance",
    #     0.3,
    #     0.0,
    #     1.0,
    #     0.1,
    #     description="Probability that the virus will be removed",
    # ),
    # "gain_resistance_chance": UserSettableParameter(
    #     "slider",
    #     "Gain Resistance Chance",
    #     0.5,
    #     0.0,
    #     1.0,
    #     0.1,
    #     description="Probability that a recovered agent will become "
    #     "resistant to this virus in the future",
    # ),
}

server = ModularServer(
    ArticlesProductModel, [network, ChartTitle(), chart, ChartTitle2(), chart2], "Modelo de Citações", model_params
)
server.port = 8521
