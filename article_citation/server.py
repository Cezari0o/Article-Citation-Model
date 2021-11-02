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

    def node_size(agent):
        """Da o tamanho de um nó no gráfico gerado, baseado na quantidade de citacoes que sao feitas a ele."""
        
        refs_this_art = agent.model.G.in_degree(agent.unique_id)
        refs_this_art = int(math.log(refs_this_art + 1, 1000) * 5)

        # divisao = 30

        # refs_this_art = 2 * refs_this_art // divisao

        return refs_this_art + 3

    def node_color(agent):
        """ Retorna a cor de um nó do gráfico. Se o artigo (nó) tiver alguma citação, sua cor ficara azul, caso contrário, ele será 
        laranja. """

        total_refs = len(agent.reference_articles)

        if(total_refs > 0):
            return "#6666ff";

        return "#ff6600"

    def edge_color(agent1, agent2):
        
        return "#e8e8e8"

    def edge_width(agent1, agent2):
        return 2

    def get_agents(source, target):
        """ Retorna os agentes que compõem a rede, assim como a forma que eles serão exibidos."""
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

# Secoes de texto a serem exibidas na página interativa
class ChartTitle(TextElement):
    def render(self, model):

        return "Medidas de tendência sobre a quantidade de referências dos artigos:"

class ChartTitle2(TextElement):
    def render(self, model):
        return "Quantidade de citações que cada artigo faz:"


# Os parametros utilizados na pagina interativa
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

    # "num_acceptable_articles" :  UserSettableParameter(
    #     param_type="slider",
    #     name="Número de citações médias iniciais",
    #     value=50,
    #     min_value=10,
    #     max_value=80,
    #     step=1,
    #     description="Escolha a quantidade de artigos que terão uma citação média inicial um pouco mais baixa"
    # ),

    "num_max_authors" : UserSettableParameter(
        param_type="slider",
        name="Número máximo de autores",
        value=100,
        min_value=10,
        max_value=400,
        step=1,
        description="Escolha o número de autores que podem produzir artigos"
    ),
}

server = ModularServer(
    ArticlesProductModel, [network, ChartTitle(), chart, ChartTitle2(), chart2], "Modelo de Citações", model_params
)
server.port = 8521
