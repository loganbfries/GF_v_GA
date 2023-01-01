import requests
import pickle
from datetime import date
import os


def delete_old_data(path):
    files = os.listdir(path)

    for file in files:
        if file.endswith(".pkl"):
            os.remove(os.path.join(path, file))
            print("Sucessfully deleted: {file}".format(file=file))
        else:
            continue


def get_season_data(year):

    save_path = "/Users/loganfries/iCloud/Hockey/Data/"
    delete_old_data(save_path)

    game_data = []
    year = year
    season_type = "02"
    max_game_ID = 1312

    today = date.today()

    for i in range(1, max_game_ID + 1):

        print(
            "Getting game data for game ID: {game_number}".format(
                game_number=str(i).zfill(4)
            )
        )

        r = requests.get(
            url="http://statsapi.web.nhl.com/api/v1/game/{year}{season_type}{game_number}/feed/live".format(
                year=year, season_type=season_type, game_number=str(i).zfill(4)
            )
        )

        data = r.json()
        game_data.append(data)

    with open(
        save_path
        + "{year}Dataset_on_{today_date}.pkl".format(year=year, today_date=str(today)),
        "wb",
    ) as f:
        pickle.dump(game_data, f, pickle.HIGHEST_PROTOCOL)


get_season_data("2022")
