"""
Script to extract summary of recent (last 8 days') card moves from a Trello board.

Usage:

Run `python extract_recent_moves.py [TRELLO KEY] [TRELLO TOKEN] [BOARD ID]`.

Output is written to `recent_moves.csv` by default,
pass `-o` or `--output-file` parameter to override.
"""

from collections import namedtuple
from datetime import datetime, timedelta, timezone
import argparse
import csv
import sys
import re
from trello import TrelloClient
from trello.exceptions import ResourceUnavailable

OLDEST_MOVES_TO_EXTRACT = datetime.now(timezone.utc) - timedelta(days=8)

BOARD_LIST_NAME = "board_list_name"
CARD_LABEL1_NAME = "card_label1_name"
CARD_LABEL2_NAME = "card_label2_name"

Column = namedtuple("Column", ["column_name", "field_name"])
COLUMNS = [
    Column(column_name=BOARD_LIST_NAME, field_name=""),
    Column(column_name="card_short_id", field_name="short_id"),
    Column(column_name="card_name", field_name="name"),
    Column(column_name=CARD_LABEL1_NAME, field_name=""),
    Column(column_name=CARD_LABEL2_NAME, field_name=""),
    Column(column_name="card_dateMovedToThisList", field_name="dateMovedToThisList"),
    Column(column_name="card_movedFromList", field_name="movedFromList"),
]

REGEX_DUE_DATE_FORMAT = re.compile(r"(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+).?\d*Z")


def get_cards_from_board(client, board_id, output_file):
    rows = []

    try:
        print("Reading cards from board...")
        board = client.get_board(board_id)
    except ResourceUnavailable:
        return f"Error: could not find board with ID: {board_id}"

    board_lists = board.list_lists()

    for board_list in board_lists:
        for card in board_list.list_cards():
            if card.dateLastmoves < OLDEST_MOVES_TO_EXTRACT:
                continue

            row = {}
            labels = getattr(card, "labels", None)

            for column in COLUMNS:
                if column.field_name:
                    row[column.column_name] = getattr(card, column.field_name, "")
                else:
                    if column.column_name == BOARD_LIST_NAME:
                        row[column.column_name] = board_list.name
                    elif column.column_name == CARD_LABEL1_NAME:
                        if len(labels) > 0:
                            row[column.column_name] = labels[0].name
                    elif column.column_name == CARD_LABEL2_NAME:
                        if len(labels) > 1:
                            row[column.column_name] = labels[1].name
                    else:
                        row[column.column_name] = f"No value found for {column}"

            card_movements = card.list_movements()
            if card_movements:
                card_movements.sort(
                    key=lambda card_movement: card_movement["datetime"],
                    reverse=True,
                )

                for card_movement in card_movements:
                    row = row.copy()
                    row["card_dateMovedToThisList"] = card_movement["datetime"].date()
                    row["card_movedFromList"] = card_movement["source"]["name"]
                    row["board_list_name"] = card_movement["destination"]["name"]
                    rows.append(row)
            else:
                row["card_dateMovedToThisList"] = card.created_date.date()
                rows.append(row)

    print(f"Writing CSV output to {output_file}...")
    with open(output_file, "w", newline="", encoding="utf-8") as file:
        csvfile = csv.DictWriter(file, [column.column_name for column in COLUMNS])
        csvfile.writeheader()
        csvfile.writerows(rows)
    print("Fin")


def get_arguments():
    parser = argparse.ArgumentParser(
        description="Query Trello API for recent card moves in a board"
    )
    parser.add_argument("key", help="Your Trello API key")
    parser.add_argument("token", help="Your Trello service token")
    parser.add_argument(
        "board_id",
        help="ID of board to query (if not supplied, will list all available boards and exit)",
        nargs="?",
    )
    parser.add_argument(
        "-o",
        "--output_file",
        help='File to receive results (default = "recent_moves.csv")',
        nargs="?",
        default="recent_moves.csv",
    )
    return parser.parse_args()


def main():
    args = get_arguments()

    client = TrelloClient(api_key=args.key, token=args.token)

    return get_cards_from_board(client, args.board_id, args.output_file)


if __name__ == "__main__":
    return_code = main()
    sys.exit(return_code)
