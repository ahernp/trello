from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from unittest.mock import call, MagicMock, Mock, mock_open, patch

from trello import TrelloClient

from extract_recent_moves import main

TODAY = datetime.now(timezone.utc)
SEVEN_DAYS_AGO = TODAY - timedelta(days=7)
EIGHT_DAYS_AGO = TODAY - timedelta(days=8)
NINE_DAYS_AGO = TODAY - timedelta(days=9)

today = TODAY.strftime("%Y-%m-%d")
seven_days_ago = SEVEN_DAYS_AGO.strftime("%Y-%m-%d")
eight_days_ago = EIGHT_DAYS_AGO.strftime("%Y-%m-%d")
nine_days_ago = NINE_DAYS_AGO.strftime("%Y-%m-%d")

card_label_1 = MagicMock()
card_label_1.name = "Card label 1"
card_label_2 = MagicMock()
card_label_2.name = "Card label 2"
card_label_3 = MagicMock()
card_label_3.name = "Card label 3"


@dataclass()
class MockArgs:
    key: str = "key"
    token: str = "token"
    board_id: str = "board_id"
    output_file: str = "output_file"


card_movement_1 = {
    "datetime": NINE_DAYS_AGO,
    "source": {"name": "Movement source name 1"},
    "destination": {"name": "Movement destination name 2"},
}
card_movement_2 = {
    "datetime": EIGHT_DAYS_AGO,
    "source": {"name": "Movement source name 3"},
    "destination": {"name": "Movement destination name 4"},
}
card_movement_3 = {
    "datetime": SEVEN_DAYS_AGO,
    "source": {"name": "Movement source name 5"},
    "destination": {"name": "Movement destination name 6"},
}

mock_card_moved_today = MagicMock()
mock_card_moved_today.short_id = 1
mock_card_moved_today.name = "Card name 1"
mock_card_moved_today.created_date = NINE_DAYS_AGO
mock_card_moved_today.dateLastActivity = TODAY
mock_card_moved_today.dateMovedToThisList = TODAY
mock_card_moved_today.movedFromList = "From list 1"
mock_card_moved_today.labels = []
mock_card_moved_today.list_movements.return_value = [card_movement_1]

mock_card_moved_7_days_ago = MagicMock()
mock_card_moved_7_days_ago.short_id = 2
mock_card_moved_7_days_ago.name = "Card name 2"
mock_card_moved_7_days_ago.created_date = NINE_DAYS_AGO
mock_card_moved_7_days_ago.dateLastActivity = SEVEN_DAYS_AGO
mock_card_moved_7_days_ago.dateMovedToThisList = SEVEN_DAYS_AGO
mock_card_moved_7_days_ago.movedFromList = "From list 2"
mock_card_moved_7_days_ago.labels = [card_label_1]
mock_card_moved_7_days_ago.list_movements.return_value = []

mock_card_moved_8_days_ago = MagicMock()
mock_card_moved_8_days_ago.short_id = 3
mock_card_moved_8_days_ago.name = "Card name 3"
mock_card_moved_7_days_ago.created_date = NINE_DAYS_AGO
mock_card_moved_8_days_ago.dateLastActivity = EIGHT_DAYS_AGO
mock_card_moved_8_days_ago.dateMovedToThisList = EIGHT_DAYS_AGO
mock_card_moved_8_days_ago.movedFromList = "From list 3"
mock_card_moved_8_days_ago.labels = [card_label_1, card_label_2]
mock_card_moved_8_days_ago.list_movements.return_value = [
    card_movement_2,
    card_movement_3,
]

mock_card_moved_9_days_ago = MagicMock()
mock_card_moved_9_days_ago.short_id = 4
mock_card_moved_9_days_ago.name = "Card name 4"
mock_card_moved_7_days_ago.created_date = NINE_DAYS_AGO
mock_card_moved_9_days_ago.dateLastActivity = NINE_DAYS_AGO
mock_card_moved_9_days_ago.dateMovedToThisList = NINE_DAYS_AGO
mock_card_moved_9_days_ago.movedFromList = "From list 4"
mock_card_moved_9_days_ago.labels = [card_label_1, card_label_2, card_label_3]
mock_card_moved_9_days_ago.list_movements.return_value = [
    card_movement_1,
    card_movement_2,
    card_movement_3,
]

mock_card_list_1 = [mock_card_moved_today, mock_card_moved_7_days_ago]
mock_card_list_2 = [mock_card_moved_8_days_ago, mock_card_moved_9_days_ago]

mock_board_list_1 = MagicMock()
mock_board_list_1.name = "List name 1"
mock_board_list_1.list_cards.return_value = mock_card_list_1
mock_board_list_2 = MagicMock()
mock_board_list_2.name = "List name 2"
mock_board_list_2.list_cards.return_value = mock_card_list_2
mock_board_lists = [mock_board_list_1, mock_board_list_2]

mock_board = MagicMock()
mock_board.list_lists.return_value = mock_board_lists

mock_client = MagicMock()
mock_client.get_board.return_value = mock_board
mock_trello_client = Mock(spec_set=TrelloClient, return_value=mock_client)

expected_output_calls = [
    call(
        "board_list_name,card_short_id,card_name,card_label1_name,card_label2_name,card_dateMovedToThisList,card_movedFromList\r\n"
    ),
    call(
        f"Movement destination name 2,1,Card name 1,,,{nine_days_ago},Movement source name 1\r\n"
    ),
    call(f"List name 1,2,Card name 2,Card label 1,,{nine_days_ago},From list 2\r\n"),
    call(
        f"Movement destination name 6,3,Card name 3,Card label 1,Card label 2,{seven_days_ago},Movement source name 5\r\n"
    ),
    call(
        f"Movement destination name 4,3,Card name 3,Card label 1,Card label 2,{eight_days_ago},Movement source name 3\r\n"
    ),
]


def test_extract_recent_moves():
    with patch(
        "extract_recent_moves.get_arguments", Mock(return_value=MockArgs())
    ), patch("extract_recent_moves.open", mock_open()) as mock_file, patch(
        "extract_recent_moves.TrelloClient", mock_trello_client
    ):
        main()
        mock_file().write.assert_has_calls(expected_output_calls)


test_extract_recent_moves()
