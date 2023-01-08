import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import glob
import os
import functools as ft
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

# Gets the images for plotting the teams logos.
def images(dict, xcol, ycol, graph_name):
    for team in dict.keys():
        arr_img = plt.imread(
            "/Users/loganfries/iCloud/Hockey/Data/Logos/{team}_logo.png".format(
                team=team
            )
        )
        imagebox = OffsetImage(arr_img, zoom=0.04)
        ab = AnnotationBbox(
            imagebox, (dict[team][xcol], dict[team][ycol]), frameon=False
        )
        graph_name.add_artist(ab)


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
step_size = 20

weeks = get_weeks()
weeks = sorted(weeks)

df_final = merge_dataframes("/Users/loganfries/iCloud/Hockey/Data/GF_v_GA/")

# Dictionary that will contain lists of the max and min values for each week.
max_min_each_week = {"Average Goals For": [], "Average Goals Against": []}

for week in weeks:
    max_min_each_week["Average Goals For"].append(
        np.max(df_final["Avg Goals For Week {week}".format(week=week)])
    )

    max_min_each_week["Average Goals For"].append(
        np.min(df_final["Avg Goals For Week {week}".format(week=week)]),
    )
    max_min_each_week["Average Goals Against"].append(
        np.max(df_final["Avg Goals Against Week {week}".format(week=week)])
    )

    max_min_each_week["Average Goals Against"].append(
        np.min(df_final["Avg Goals Against Week {week}".format(week=week)]),
    )

x_axis_bounds = (
    np.min(max_min_each_week["Average Goals For"]),
    np.max(max_min_each_week["Average Goals For"]),
)

y_axis_bounds = (
    np.min(max_min_each_week["Average Goals Against"]),
    np.max(max_min_each_week["Average Goals Against"]),
)

# Initialize a dictionary to store the league median for each week.
league_medians = {}

for week in weeks:
    league_medians["Week {week}".format(week=week)] = {
        "League Median Goals For": np.median(
            df_final["Avg Goals For Week {week}".format(week=week)]
        ),
        "League Median Goals Against": np.median(
            df_final["Avg Goals Against Week {week}".format(week=week)]
        ),
    }

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


coordinate_step_name_list = sorted(
    list(coordinate_steps["Anaheim Ducks"]["Average Goals For Steps"].keys())
)

dimensions = (7, 7)
fig, ax = plt.subplots(figsize=dimensions)

counter = 1

for coordinate_step_name in coordinate_step_name_list:

    week = coordinate_step_name.split(" ")[1]

    for step in range(0, step_size):

        dict_for_images = {}

        for team in coordinate_steps.keys():

            avg_goals_for = coordinate_steps[team]["Average Goals For Steps"][
                coordinate_step_name
            ][step]
            avg_goals_against = coordinate_steps[team]["Average Goals Against Steps"][
                coordinate_step_name
            ][step]

            dict_for_images[team] = {}
            dict_for_images[team]["avg_goals_for"] = avg_goals_for
            dict_for_images[team]["avg_goals_against"] = avg_goals_against

            ax.scatter(
                avg_goals_for,
                avg_goals_against,
                s=10,
                color="black",
                alpha=0.5,
            )

        if "Still" in coordinate_step_name:

            week = coordinate_step_name.split(" ")[1]

            ax.axvline(
                x=league_medians["Week {week}".format(week=week)][
                    "League Median Goals For"
                ],
                ls="--",
                color="gray",
                alpha=0.3,
            )
            ax.axhline(
                y=league_medians["Week {week}".format(week=week)][
                    "League Median Goals Against"
                ],
                ls="--",
                color="gray",
                alpha=0.3,
            )

            ax.text(
                league_medians["Week {week}".format(week=week)][
                    "League Median Goals Against"
                ]
                + 0.05,
                league_medians["Week {week}".format(week=week)][
                    "League Median Goals For"
                ]
                + 0.1,
                "League" "\n" "Median",
                horizontalalignment="left",
                size=6,
                color="gray",
                weight="bold",
            )

        plt.suptitle("Avg Goals Against vs. Avg Goals For", size=14, y=0.95)

        plt.title(
            "Through Week: {nhl_week}".format(nhl_week=week),
            size=12,
        )
        ax.invert_yaxis()

        ax.set_xbound(lower=x_axis_bounds[0] - 0.25, upper=x_axis_bounds[1] + 0.25)
        ax.set_ybound(lower=y_axis_bounds[0] - 0.25, upper=y_axis_bounds[1] + 0.25)

        # Text for top right quadrant.
        plt.text(
            0.98,
            0.98,
            "Good Offense",
            horizontalalignment="right",
            verticalalignment="top",
            size=8,
            color="green",
            weight="semibold",
            transform=ax.transAxes,
        )
        plt.text(
            0.98,
            0.96,
            "Good Defense",
            horizontalalignment="right",
            verticalalignment="top",
            size=8,
            color="green",
            weight="semibold",
            transform=ax.transAxes,
        )

        # Text for bottom right quadrant.
        plt.text(
            0.98,
            0.06,
            "Good Offense",
            horizontalalignment="right",
            verticalalignment="top",
            size=8,
            color="green",
            weight="semibold",
            transform=ax.transAxes,
        )
        plt.text(
            0.98,
            0.04,
            "Bad Defense",
            horizontalalignment="right",
            verticalalignment="top",
            size=8,
            color="red",
            weight="semibold",
            transform=ax.transAxes,
        )

        # Text for bottom left quadrant.
        plt.text(
            0.02,
            0.06,
            "Bad Offense",
            horizontalalignment="left",
            verticalalignment="top",
            size=8,
            color="red",
            weight="semibold",
            transform=ax.transAxes,
        )
        plt.text(
            0.02,
            0.04,
            "Bad Defense",
            horizontalalignment="left",
            verticalalignment="top",
            size=8,
            color="red",
            weight="semibold",
            transform=ax.transAxes,
        )

        # Text for top left quadrant.
        plt.text(
            0.02,
            0.98,
            "Bad Offense",
            horizontalalignment="left",
            verticalalignment="top",
            size=8,
            color="red",
            weight="semibold",
            transform=ax.transAxes,
        )
        plt.text(
            0.02,
            0.96,
            "Good Defense",
            horizontalalignment="left",
            verticalalignment="top",
            size=8,
            color="green",
            weight="semibold",
            transform=ax.transAxes,
        )

        images(dict_for_images, "avg_goals_for", "avg_goals_against", ax)

        plt.savefig(
            "/Users/loganfries/iCloud/Hockey/GIF_Images/GF_v_GA/{number}.png".format(
                number=counter
            ),
            dpi=300,
            bbox_inches="tight",
        )
        plt.cla()
        counter += 1
