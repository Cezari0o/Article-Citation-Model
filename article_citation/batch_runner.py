from mesa.batchrunner import BatchRunner
from .model import *

def collect_data_simulations():

    # The parameters here still do not influence the execution of the simulations
    fixed_params = {
        "num_max_authors": 10 
        # "num_acceptable_articles": 20
    }

    variable_params = {
        "num_max_articles": range(100, 1000, 50),
        # "num_acceptable_articles": range(10, 20, 5),
    }

    # alo = []
    # for i in range(100, 451, 50):
    #     alo.append(i)
    # print(alo)
    experiments = 10
    maximum_steps = max(variable_params["num_max_articles"])

    model_reporters = {
        "Media" : get_mean_citation,
        "Mediana" : get_median_citation,
        "Moda" : get_mode_citation,
    }

    agent_reporters = {
        "numero_citacoes" : "num_citations",
        "numero_referencias" : "num_references",
        "artigos_referenciados" : "aux_reference_articles",
        "Citacoes": "aux_citations",
    }

    batch_runner = BatchRunner(
        ArticlesProductModel,
        variable_parameters = variable_params,
        fixed_parameters = fixed_params,
        iterations = experiments,
        max_steps = maximum_steps,
        model_reporters = model_reporters,
        agent_reporters = agent_reporters,
    )

    batch_runner.run_all()

    # Agents results
    agents_data = batch_runner.get_agent_vars_dataframe()

    # Model results
    model_data = batch_runner.get_model_vars_dataframe()

    agents_data.to_csv(path_or_buf = "ArticleProduction_Agents_" + 
    "_experiments_" + str(experiments) + 
    "_max_steps_" + str(maximum_steps) + "_.csv")

    model_data.to_csv(path_or_buf = "ArticleProduction_Model_" + 
    "_experiments_" + str(experiments) +
    "_max_steps_" + str(maximum_steps) + "_.csv")
