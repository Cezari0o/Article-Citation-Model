from article_citation.server import server
from article_citation.batch_runner import collect_data_simulations

# Mostrando na tela as opcoes disponiveis para execucao do modelo
print("\n------ Article Production Simulation ------")
print("1 - Run interactive page.")
print("2 - Run several simulations. Save the generated data do csv files.\n")

print("Choose one option from above:", sep= ' ')

opt = 0
# O programa nao avanca enquanto uma das opcoes possiveis nao for selecionada
while(opt != 1 and opt != 2):
    opt = int(input())

if opt == 1:
    server.launch()

else:
    collect_data_simulations()