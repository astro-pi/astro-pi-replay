from datetime import timedelta
from unittest.mock import patch

from astro_pi_executor.executor import AstroPiExecutor
from astro_pi_executor.sense_hat.sense_hat_api import SenseHatAdapter

# TODO test that the SenseHat API works


def test_replay_should_replay_sequence_of_data():
    executor = AstroPiExecutor()

    # Make the test deterministic
    with patch("astro_pi_executor.executor.datetime") as mock_datetime:
        mock_datetime.now.return_value = executor._state._start_time + timedelta(days=2)
        sh = SenseHatAdapter(executor)
        assert sh.colour.colour == (17, 15, 13, 48)
        assert executor._state._last_row_index == (13723 - 1)  # should be the last row
