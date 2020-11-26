import os
from enum import Enum

import tracking_client
from tracking_client import Event
from tracking_client.configuration import Configuration

NUM_API_CLIENT_THREADS = 10


class EventName(Enum):
    DECONTAMINATION = 'de-contamination'
    QC = 'QC'
    VARIANT_CALLING = 'variant-calling'
    PREDICTION = 'prediction'
    BIGSI_BUILDING = 'bigsi-building'
    DISTANCE_CALCULATION = 'distance-calculation'


configuration = Configuration()
configuration.host = os.environ.get("ATLAS_TRACKING_API", "http://tracking-api-service/api/v1")
api_client = tracking_client.ApiClient(configuration=configuration, pool_threads=NUM_API_CLIENT_THREADS)
qc_result_api_instance = tracking_client.QcResultApi(api_client)
event_api_instance = tracking_client.EventApi(api_client)


def send_qc_result(qc_result, sample_id):
    qc_result_api_instance.samples_id_qc_result_put(sample_id, qc_result)


def record_event(sample_id: str, event_name: EventName, software: str, software_version: str, start_timestamp: float, duration: float, command: str):
    """

    :param duration: in seconds
    """
    event = Event(
        name=event_name.value,
        software=software,
        software_version=software_version,
        start_time=start_timestamp,
        duration=duration,
        command=command
    )

    event_api_instance.samples_id_events_post(sample_id, event)
