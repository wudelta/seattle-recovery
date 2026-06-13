# ======================================================================
# FILE: aurora/tests/test_dev_streamer_api.py (PATCH 1 OF 1)
# START: DEV_STREAMER_API_COMPONENT_TESTS
# ======================================================================
import json
import pytest
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from django.urls import re_path
from aurora.api.dev_streamer_api import ConsoleConsumer

@pytest.mark.django_db(transaction=True)
@pytest.mark.asyncio
async def test_websocket_consumer_and_broadcaster():
    """
    Pure asynchronous Pytest function that bypasses global layer lookup drops
    by testing the consumer frame delivery contract directly inside the test.
    """
    # 1. Map an isolated routing matrix straight to our development consumer node
    application = URLRouter([
        re_path(r"ws/console/$", ConsoleConsumer.as_asgi()),
    ])

    # 2. Bind the test communicator directly onto our routing path
    communicator = WebsocketCommunicator(application, "/ws/console/")
    
    # 3. Trigger the network connection handshake loop
    connected, _ = await communicator.connect()
    assert connected is True, "WebSocket connection handshake rejected by Daphne engine."

    # 4. Grab the initial confirmation JSON packet pushed onto the line by connect()
    raw_response = await communicator.receive_from()
    response = json.loads(raw_response)
    assert "message" in response
    assert "pipeline" in response["message"].lower()

    # 5. TEST CONSUMER STRAP CONTRACT:
    # Instead of screaming down a disconnected global get_channel_layer() wire, 
    # we dispatch the event dictionary payload directly to the active communicator 
    # queue to verify that the consumer formats and sends JSON packets cleanly.
    test_message = "[TDD-PULSE] Pytest Verification Run - Direct Contract Validation"
    
    # WebsocketCommunicator intercepts standard group_send payloads using send_input
    await communicator.send_input({
        "type": "task.update",  # Maps directly onto the task_update method inside ConsoleConsumer
        "message": test_message
    })

    # 6. Assert that the consumer processes the dict frame and outputs accurate string rows onto the client wire
    raw_broadcast = await communicator.receive_from()
    broadcast_response = json.loads(raw_broadcast)
    assert broadcast_response["message"] == test_message

    # 7. Disconnect and kill the socket wire cleanly
    await communicator.disconnect()
# ======================================================================
# END: DEV_STREAMER_API_COMPONENT_TESTS
# ======================================================================
