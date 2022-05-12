import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import geopandas as gpd

egrid = pd.read_csv("e_grid co2e nonbaseload subregion 2020.csv")
#subregions = gpd.read_file(r"C:\Users\thiag\Box\Thiago DOE Research\Delivery Robots\Paper\Emissions Map\egrid2020_subregions\eGRID2020_subregions.shp")
print(egrid)