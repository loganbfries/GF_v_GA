import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import functools as ft


def get_weeks():
    """Returns a list of weeks that we currently have data for."""

    import glob

    path_list = glob.glob("/Users/loganfries/iCloud/Hockey/Data/GF_v_GA/*.csv")

    return [path.split("_")[-1].split(".")[0] for path in path_list]


def merge_dataframes(path, merge_on="Team"):
    """Returns a dataframe that contains all of the dataframes in the path directory, merged by team name."""

    all_files = glob.glob("{path}/*.csv".format(path=path))

    list_of_dataframes = []

    for filename in all_files:
        df = pd.read_csv(filename, index_col=None, header=0)
        list_of_dataframes.append(df)

    return ft.reduce(
        lambda left, right: pd.merge(left, right, on=merge_on), list_of_dataframes
    )


weeks = get_weeks()

df_final = merge_dataframes("/Users/loganfries/iCloud/Hockey/Data/GF_v_GA/")

# Initialize a dictionary to store the x (average goals against) and y (average goals for) coordinate steps for each team.
coordinate_steps = {}

for team in df_final["Team"]:
    coordinate_steps[team] = {
        "Average Goals For Steps": [],
        "Average Goals Against Steps": [],
    }
