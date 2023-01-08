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


def get_coordinate_data(dataframe, coordinate, team, week):
    """Returns the coordinate data for the team in the dataframe."""

    if coordinate == "goals_for":
        coordinate = "Avg Goals For Week {week}"
    elif coordinate == "goals_against":
        coordinate = "Avg Goals Against Week {week}"

    return dataframe.loc[
        dataframe["Team"] == team, coordinate.format(week=week)
    ].values[0]


# Set the number of steps for the point to move through for each week.
step_size = 10

weeks = get_weeks()
weeks = sorted(weeks)

df_final = merge_dataframes("/Users/loganfries/iCloud/Hockey/Data/GF_v_GA/")

# Initialize a dictionary to store the x (average goals against) and y (average goals for) coordinate steps for each team.
coordinate_steps = {}

for team in df_final["Team"]:
    coordinate_steps[team] = {
        "Average Goals For Steps": {},
        "Average Goals Against Steps": {},
    }

for team in df_final["Team"]:

    ga_coordinate_steps = []
    gf_coordinate_steps = []

    for week in weeks:
        # Skip the first week since we are starting from that point.
        if week == weeks[0]:

            coordinate_steps[team]["Average Goals Against Steps"][
                "Week {week} Still".format(week=week)
            ] = np.ones(step_size) * get_coordinate_data(
                df_final, "goals_against", team, week
            )

            coordinate_steps[team]["Average Goals For Steps"][
                "Week {week} Still".format(week=week)
            ] = np.ones(step_size) * get_coordinate_data(
                df_final, "goals_for", team, week
            )
            continue

        current_week_index = weeks.index(week)
        prev_week = weeks[current_week_index - 1]

        avg_gf_prev_week = get_coordinate_data(df_final, "goals_for", team, prev_week)

        avg_ga_prev_week = get_coordinate_data(
            df_final, "goals_against", team, prev_week
        )

        avg_gf_current_week = get_coordinate_data(df_final, "goals_for", team, week)

        avg_ga_current_week = get_coordinate_data(df_final, "goals_against", team, week)

        ga_weekly_coordinate_steps = np.linspace(
            avg_ga_prev_week, avg_ga_current_week, step_size
        )

        gf_weekly_coordinate_steps = np.linspace(
            avg_gf_prev_week, avg_gf_current_week, step_size
        )

        # This is creating an array of size (step_size) that contains the last value of the array of coordinate steps, so it pauses on the last coordinate step for each week.
        ga_stand_still_frames = np.ones(step_size) * ga_weekly_coordinate_steps[-1]
        gf_stand_still_frames = np.ones(step_size) * gf_weekly_coordinate_steps[-1]

        coordinate_steps[team]["Average Goals Against Steps"][
            "Week {week} Still".format(week=week)
        ] = ga_stand_still_frames
        coordinate_steps[team]["Average Goals For Steps"][
            "Week {week} Still".format(week=week)
        ] = gf_stand_still_frames
        coordinate_steps[team]["Average Goals Against Steps"][
            "Week {previous_week} to Week {week}".format(
                previous_week=prev_week, week=week
            )
        ] = ga_weekly_coordinate_steps
        coordinate_steps[team]["Average Goals For Steps"][
            "Week {previous_week} to Week {week}".format(
                previous_week=prev_week, week=week
            )
        ] = gf_weekly_coordinate_steps

    print(coordinate_steps[team]["Average Goals Against Steps"].keys())
    print(coordinate_steps[team]["Average Goals For Steps"].keys())

    exit()
