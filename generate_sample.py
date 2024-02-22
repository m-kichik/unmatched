from argparse import ArgumentParser
import random

from utils import parse_config_file, get_sample


def parse_args():
    parser = ArgumentParser()
    parser.add_argument("file", type=str, help=".yaml file with sets info")
    parser.add_argument("num_players", type=int, default=2)
    parser.add_argument(
        "policy", type=str, default="w", help="w for weighted, s for statistical"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.policy not in ["w", "s"]:
        raise ValueError("Undefined sampling policy")

    heroes, maps = parse_config_file(args.file, bool(args.num_players - 4))
    selected_heroes = get_sample(heroes, args.num_players, args.policy)
    selected_map = get_sample(maps, 1, "w")

    for idx, hero in enumerate(selected_heroes):
        print(f"Player {idx + 1}: {hero}")

    print(f"\nMap: {selected_map[0]}")


if __name__ == "__main__":
    main()
