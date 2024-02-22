from pathlib import Path
import requests
from typing import List
import yaml

import numpy as np


def normal(x, mu=0.5, sigma=0.15):
    return (1 / (sigma * np.sqrt(2 * np.pi))) * np.exp(-0.5 * ((x - mu) / sigma) ** 2)


def parse_config_file(file_path: str, require_big_map=False):
    def process_name(name: str):
        name = [w.lower() for w in name.replace("_", " ").split()]
        name = " ".join(
            [w.capitalize() if w not in ["and", "of", "to"] else w for w in name]
        )
        return name

    def normalize_sample(sample: List[tuple]):
        sum_sample = sum([item[1] for item in sample])
        return [(item[0], item[1] / sum_sample) for item in sample]

    with open(file_path, "r") as file:
        sets = yaml.safe_load(file)

    heroes = []
    maps = []

    for set_name in sets:
        content = sets[set_name]
        set_name = process_name(set_name)
        set_weight = content["SET_WEIGHT"]

        for hero_name in content["HEROES"]:
            hero_weight = content["HEROES"][hero_name]
            hero_name = process_name(hero_name)
            hero_name = f"{hero_name}"
            # hero_name = f"{hero_name} ({set_name})"
            if set_weight * hero_weight > 0:
                heroes.append((hero_name, set_weight * hero_weight))

        if content["MAPS"] is not None:
            for map_name in content["MAPS"]:
                map_weight = content["MAPS"][map_name]["WEIGHT"]
                is_map_big = content["MAPS"][map_name]["IS_BIG"]
                map_name = process_name(map_name)
                map_name = f"{map_name} ({set_name})"
                if set_weight * map_weight > 0:
                    if require_big_map and is_map_big or not require_big_map:
                        maps.append((map_name, set_weight * map_weight))

    heroes = normalize_sample(heroes)
    maps = normalize_sample(maps)

    return heroes, maps


def get_umdb_sample(num_items, total_threshold=10):
    grid = requests.get("https://unmatched.cards/api/games/grid").json()["grid"]
    totals = {item["id"]: item["total"] for item in grid}
    names = {item["id"]: item["name"] for item in grid}

    def get_winrates(item: dict):
        stats = {
            int(key): (value["victories"] / value["total_games"], value["total_games"])
            for key, value in item.items()
            if key.isnumeric()
            and value["total_games"] > 0
            and value["victories"] is not None
        }
        return stats

    def normalize_weights(weights):
        norm_weights = [normal(x) for x in weights]
        norm_sum = sum(norm_weights)
        return tuple([x / norm_sum for x in norm_weights])

    def get_combinations():
        result = []
        for j in range(2):
            for i in range(num_items // 2):
                result.append((i, j))
        return result

    start_sample = np.random.choice(grid, size=num_items // 2, replace=False)
    start_weights = []
    selected_ids = []

    for item in start_sample:
        item_id = int(item["id"])
        selected_ids.append(item_id)
        item_stats = get_winrates(item)

        undefined_values = set(totals.keys()).difference(set(item_stats.keys()))
        for idx in undefined_values:
            item_stats[idx] = (0, 0)

        for idx in item_stats:
            if item_stats[idx][1] >= total_threshold:
                item_stats[idx] = item_stats[idx][0]
            else:
                alpha = item_stats[idx][1] / total_threshold
                beta = (1 - alpha) / 2
                item_av = totals[item_id]["victories"] / totals[item_id]["total_games"]
                idx_av = totals[idx]["victories"] / totals[idx]["total_games"]
                rate = alpha * item_stats[idx][0] + beta * (item_av + 1 - idx_av)
                item_stats[idx] = rate

        start_weights.append(item_stats)

    for idx in selected_ids:
        for sw in start_weights:
            del sw[idx]

    final_pairs = []
    for i in range(len(start_weights)):
        ids, weights = zip(*[(key, value) for key, value in start_weights[i].items()])
        weights = normalize_weights(weights)
        new_item = np.random.choice(ids, size=1, replace=False, p=weights)[0]

        for sw in start_weights[i:]:
            del sw[new_item]

        final_pairs.append((names[selected_ids[i]], names[new_item]))

    final_pairs = [final_pairs[i][j] for i, j in get_combinations()]
    return final_pairs


def get_sample(items: List[tuple], num_items, policy="w"):
    if policy == "w":
        names, weights = zip(*items)
        sample = np.random.choice(names, size=num_items, replace=False, p=weights)

    if policy == "s":
        sample = get_umdb_sample(num_items)

    return sample
