from hypothesis import given, strategies as st

import analyses
from analyses.tracking import record_event


@given(
    sample_id=st.text(),
    event_name=st.sampled_from(analyses.tracking.EventName),
    software=st.text(),
    software_version=st.text(),
    start_timestamp=st.floats(),
    duration=st.floats(),
    command=st.text(),
)
def test_fuzz_record_event(
    sample_id,
    event_name,
    software,
    software_version,
    start_timestamp,
    duration,
    command,
    mocker
):
    mock_event = mocker.MagicMock()
    mock_event_cons = mocker.patch('analyses.tracking.Event', return_value=mock_event)
    mock_event_api = mocker.patch('analyses.tracking.event_api_instance')

    record_event(
        sample_id=sample_id,
        event_name=event_name,
        software=software,
        software_version=software_version,
        start_timestamp=start_timestamp,
        duration=duration,
        command=command,
    )

    mock_event_cons.assert_called_with(
        name=event_name.value,
        software=software,
        software_version=software_version,
        start_time=start_timestamp,
        duration=duration,
        command=command,
    )

    mock_event_api.samples_id_events_post.assert_called_with(sample_id, mock_event)
