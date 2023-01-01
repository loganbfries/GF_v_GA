import numpy as np
import pickle
import matplotlib.pyplot as plt
import requests
from datetime import date
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import datetime
import pandas as pd

# Creates a dictionary storing goals for and goals against data per team.
def create_team_goals_dict():

    r = requests.get(url="https://statsapi.web.nhl.com/api/v1/teams")

    data = r.json()

    team_goals_dict = {}

    for team in data["teams"]:
        team_goals_dict[team["name"]] = {}
        team_goals_dict[team["name"]]["goals_for"] = []
        team_goals_dict[team["name"]]["goals_against"] = []
        team_goals_dict[team["name"]]["avg_goals_for"] = []
        team_goals_dict[team["name"]]["avg_goals_against"] = []

    return team_goals_dict


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


# Formats the game dates for comparison with todays date.
def format_game_date(game_date):
    game_date_month = int(game_date.split("T")[0].split("-")[1])
    game_date_year = int(game_date.split("T")[0].split("-")[0])
    game_date_day = int(game_date.split("T")[0].split("-")[2])

    return datetime.date(game_date_year, game_date_month, game_date_day)


def get_nhl_week():
    nhl_start_date = datetime.date(2022, 10, 11)  # Constant.
    today = date.today()
    week = today.isocalendar()[1]
    year = today.isocalendar()[0]

    if year == 2022:
        current_nhl_week = week - nhl_start_date.isocalendar()[1] + 1
        return current_nhl_week
    elif year == 2023:
        current_nhl_week = (week + 52) - nhl_start_date.isocalendar()[1] + 1
        return current_nhl_week


team_goals_dict = create_team_goals_dict()

today = date.today()

nhl_week = get_nhl_week()

league_goals_for = []
league_goals_against = []

individual_data = []

with open(
    "/Users/loganfries/iCloud/Hockey/Data/2022Dataset_on_{todays_date}.pkl".format(
        todays_date=today
    ),
    "rb",
) as f:
    game_data = pickle.load(f)

for game in game_data:
    if "liveData" not in game:
        continue
    if today <= format_game_date(game["gameData"]["datetime"]["dateTime"]):
        continue

    away_team = game["gameData"]["teams"]["away"]["name"]
    home_team = game["gameData"]["teams"]["home"]["name"]

    away_goals = game["liveData"]["boxscore"]["teams"]["away"]["teamStats"][
        "teamSkaterStats"
    ]["goals"]
    home_goals = game["liveData"]["boxscore"]["teams"]["home"]["teamStats"][
        "teamSkaterStats"
    ]["goals"]

    # Append goals for and goals against data to the team_goals_dict for the away team.
    team_goals_dict[away_team]["goals_for"].append(away_goals)
    team_goals_dict[away_team]["goals_against"].append(home_goals)

    # Append goals for and goals against data to the team_goals_dict for the home team.
    team_goals_dict[home_team]["goals_for"].append(home_goals)
    team_goals_dict[home_team]["goals_against"].append(away_goals)

for team in team_goals_dict:
    team_goals_dict[team]["avg_goals_for"] = np.mean(team_goals_dict[team]["goals_for"])
    team_goals_dict[team]["avg_goals_against"] = np.mean(
        team_goals_dict[team]["goals_against"]
    )

    league_goals_for.append(team_goals_dict[team]["avg_goals_for"])
    league_goals_against.append(team_goals_dict[team]["avg_goals_against"])

    individual_data.append(
        [
            team,
            team_goals_dict[team]["avg_goals_for"],
            team_goals_dict[team]["avg_goals_against"],
        ]
    )


pd.DataFrame(
    individual_data,
    columns=[
        "Team",
        "Avg Goals For Week {week}".format(week=nhl_week),
        "Avg Goals Against Week {week}".format(week=nhl_week),
    ],
).to_csv(
    "/Users/loganfries/iCloud/Hockey/Data/GF_v_GA/2022TeamData_Week_{week}.csv".format(
        week=nhl_week
    ),
    index=False,
)

league_median_goals_for = np.median(league_goals_for)
league_median_goals_against = np.median(league_goals_against)

dimensions = (7, 7)
fig, ax = plt.subplots(figsize=dimensions)


for team in team_goals_dict.keys():

    ax.scatter(
        team_goals_dict[team]["avg_goals_for"],
        team_goals_dict[team]["avg_goals_against"],
        s=10,
        color="black",
        alpha=0.5,
    )


ax.axvline(x=league_median_goals_for, ls="--", color="gray", alpha=0.3)
ax.axhline(y=league_median_goals_against, ls="--", color="gray", alpha=0.3)

ax.text(
    league_median_goals_for + 0.05,
    league_median_goals_against + 0.1,
    "League" "\n" "Median",
    horizontalalignment="left",
    size=6,
    color="gray",
    weight="bold",
)

plt.suptitle("Avg Goals Against vs. Avg Goals For", size=14, y=0.95)

plt.title(
    "Through Week: {nhl_week}".format(nhl_week=nhl_week),
    size=12,
)

ax.invert_yaxis()

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

ax.set_xbound(lower=min(league_goals_for) - 0.25, upper=max(league_goals_for) + 0.25)
ax.set_ybound(
    upper=max(league_goals_against) + 0.25, lower=min(league_goals_against) - 0.25
)

ax.set_ylabel("Avg Goals Against", size=12)
ax.set_xlabel("Avg Goals For", size=12)

images(team_goals_dict, "avg_goals_for", "avg_goals_against", ax)

plt.savefig(
    "/Users/loganfries/iCloud/Hockey/Plots/goals_for_goals_against_week_{week}.png".format(
        week=nhl_week
    ),
    dpi=300,
    bbox_inches="tight",
)
