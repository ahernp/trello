"""
Script to extract summary of recent (last 8 days') card moves from a Trello board.

Usage:

Run `python extract_recent.py [TRELLO KEY] [TRELLO TOKEN] [BOARD ID]`.

Output is written to `recent_activity.csv` by default, pass `-o` or `--output-file` parameter to override.
"""

from datetime import datetime, timedelta, timezone
import argparse
import csv
import sys
import re
from trello import TrelloClient
from trello.exceptions import ResourceUnavailable

OLDEST_ACTIVITY_TO_EXTRACT = datetime.now(timezone.utc) - timedelta(days=8)

CARD_FIELDS = [
    "short_id",
    "name",
    "labels",
    "dateMovedToThisList",
    "movedFromList",
]
COLUMN_NAMES = "board_list_name,card_short_id,card_name,card_label1_name,card_label2_name,card_dateMovedToThisList,card_movedFromList"

REGEX_DUE_DATE_FORMAT = re.compile(r"(\d+)-(\d+)-(\d+)T(\d+):(\d+):(\d+).?\d*Z")
LABELS_TO_SEPARATE = 2


def get_cards_from_board(client, board_id, output_file):
    csv_rows = []

    print("Reading cards from board...")

    try:
        board = client.get_board(board_id)
    except ResourceUnavailable:
        return f"Error: could not find board with ID: {board_id}"

    board_lists = board.list_lists()

    for board_list in board_lists:
        for card in board_list.list_cards():
            if card.dateLastActivity < OLDEST_ACTIVITY_TO_EXTRACT:
                continue

            csv_row = {
                "board_list_name": board_list.name,
            }

            for field in CARD_FIELDS:
                value = getattr(card, field, None)
                if field == "labels":
                    if value and isinstance(value, list):
                        csv_row["card_label1_name"] = value[0].name
                        if len(value) > 1:
                            csv_row["card_label2_name"] = value[1].name
                else:
                    csv_row[f"card_{field}"] = value

            card_movements = card.list_movements()
            if card_movements:
                card_movements.sort(key=lambda x: x["datetime"], reverse=True)

                for card_movement in card_movements:
                    csv_row = csv_row.copy()
                    csv_row["card_dateMovedToThisList"] = card_movement["datetime"].date()
                    csv_row["card_movedFromList"] = card_movement["source"]["name"]
                    csv_row["board_list_name"] = card_movement["destination"]["name"]
                    csv_rows.append(csv_row)
            else:
                csv_row["card_dateMovedToThisList"] = card.created_date.date()
                csv_rows.append(csv_row)

    print(f"Writing CSV output to {output_file}...")
    with open(output_file, "w", newline="") as f:
        csvfile = csv.DictWriter(f, COLUMN_NAMES.split(","))
        csvfile.writeheader()
        csvfile.writerows(csv_rows)

    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Query Trello API for card information"
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
        help='File to receive results (default = "recent_activity.csv")',
        nargs="?",
        default="recent_activity.csv",
    )
    args = parser.parse_args()

    client = TrelloClient(
        api_key=args.key,
        token=args.token,
    )

    return_code = get_cards_from_board(client, args.board_id, args.output_file)
    sys.exit(return_code)
