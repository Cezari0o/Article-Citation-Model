from article_citation.server import server
from article_citation.batch_runner import collect_data_simulations

print("\n------ Article Production Simulation ------")
print("1 - Run interactive page.")
print("2 - Run various simulations. Save the generated data do csv files.\n")

print("Choose one option from above:", sep= ' ')

opt = 0
while(opt != 1 and opt != 2):
    opt = int(input())

if opt == 1:
    server.launch()

else:
    collect_data_simulations()