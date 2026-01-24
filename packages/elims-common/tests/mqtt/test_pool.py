"""Test ELIMS Common Package - MQTT Module - Connection Pool."""

from typing import Any
from unittest.mock import patch

import pytest
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.exceptions import MQTTConnectionError
from elims_common.mqtt.pool import (
    MQTTConnectionPool,
    MQTTPublisherPool,
    MQTTSubscriberPool,
)
from elims_common.mqtt.publisher import MQTTPublisher
from elims_common.mqtt.subscriber import MQTTSubscriber


@pytest.fixture
def mqtt_config() -> MQTTConfig:
    """Create a test MQTT configuration."""
    return MQTTConfig(
        broker_host="localhost",
        broker_port=1883,
        client_id="test_pool",
    )


def test_connection_pool_initialization(mqtt_config: MQTTConfig) -> None:
    """Test connection pool initialization."""
    pool = MQTTConnectionPool(mqtt_config, pool_size=3, client_type="publisher")

    assert pool.config == mqtt_config
    assert pool.pool_size == 3  # noqa: PLR2004
    assert pool.client_type == "publisher"
    assert pool.size == 0  # No connections created yet
    assert not pool.is_closed


def test_connection_pool_invalid_size(mqtt_config: MQTTConfig) -> None:
    """Test connection pool with invalid pool size."""
    with pytest.raises(ValueError, match="pool_size must be >= 1"):
        MQTTConnectionPool(mqtt_config, pool_size=0, client_type="publisher")

    with pytest.raises(ValueError, match="pool_size must be >= 1"):
        MQTTConnectionPool(mqtt_config, pool_size=-1, client_type="publisher")


def test_connection_pool_invalid_client_type(mqtt_config: MQTTConfig) -> None:
    """Test connection pool with invalid client type."""
    with pytest.raises(ValueError, match="client_type must be"):
        MQTTConnectionPool(mqtt_config, pool_size=5, client_type="invalid")


@patch("elims_common.mqtt.publisher.MQTTPublisher.connect")
@patch("paho.mqtt.client.Client")
def test_connection_pool_get_connection(_mock_client: Any, mock_connect: Any, mqtt_config: MQTTConfig) -> None:
    """Test getting connection from pool."""
    pool = MQTTConnectionPool(mqtt_config, pool_size=3, client_type="publisher")

    # Mock successful connection
    def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
        _self._connected = True  # noqa: SLF001

    mock_connect.side_effect = mock_conn_success

    # Get first connection (should create new one)
    conn1 = pool.get_connection()
    assert isinstance(conn1, MQTTPublisher)
    assert pool.size == 1

    # Return connection to pool
    pool.return_connection(conn1)
    assert pool.available == 1


@patch("elims_common.mqtt.publisher.MQTTPublisher.connect")
@patch("paho.mqtt.client.Client")
def test_connection_pool_reuses_connections(_mock_client: Any, mock_connect: Any, mqtt_config: MQTTConfig) -> None:
    """Test that pool reuses returned connections."""
    pool = MQTTConnectionPool(mqtt_config, pool_size=3, client_type="publisher")

    # Mock successful connection
    def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
        _self._connected = True  # noqa: SLF001

    mock_connect.side_effect = mock_conn_success

    # Get and return connection
    conn1 = pool.get_connection()
    pool.return_connection(conn1)

    # Get again should reuse same connection
    conn2 = pool.get_connection()
    assert conn1 is conn2
    assert pool.size == 1  # Only one connection created


@patch("elims_common.mqtt.publisher.MQTTPublisher.connect")
@patch("elims_common.mqtt.publisher.MQTTPublisher.disconnect")
@patch("paho.mqtt.client.Client")
def test_connection_pool_validates_health(_mock_client: Any, mock_disconnect: Any, mock_connect: Any, mqtt_config: MQTTConfig) -> None:
    """Test that pool validates connection health before reuse."""
    pool = MQTTConnectionPool(mqtt_config, pool_size=3, client_type="publisher")

    # Mock connection
    def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
        _self._connected = True  # noqa: SLF001

    mock_connect.side_effect = mock_conn_success

    # Get connection
    conn1 = pool.get_connection()

    # Mark as disconnected (unhealthy)
    conn1._connected = False  # noqa: SLF001

    # Return to pool
    pool.return_connection(conn1)

    # Get connection again - should reconnect the unhealthy connection
    conn2 = pool.get_connection()
    assert conn1 is conn2
    assert mock_disconnect.called  # Should have attempted to disconnect
    assert mock_connect.call_count >= 2  # noqa: PLR2004


@patch("elims_common.mqtt.publisher.MQTTPublisher.connect")
@patch("paho.mqtt.client.Client")
def test_connection_pool_context_manager(_mock_client: Any, mock_connect: Any, mqtt_config: MQTTConfig) -> None:
    """Test connection pool context manager for auto checkout/return."""
    pool = MQTTConnectionPool(mqtt_config, pool_size=3, client_type="publisher")

    # Mock successful connection
    def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
        _self._connected = True  # noqa: SLF001

    mock_connect.side_effect = mock_conn_success

    # Use context manager
    with pool.get_connection_context() as conn:
        assert isinstance(conn, MQTTPublisher)
        assert pool.available == 0  # Connection checked out

    # Connection should be returned automatically
    assert pool.available == 1


@patch("paho.mqtt.client.Client")
def test_connection_pool_close_all(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test closing all connections in pool."""
    pool = MQTTConnectionPool(mqtt_config, pool_size=3, client_type="publisher")

    # Close empty pool
    pool.close_all()
    assert pool.is_closed

    # Closing again should not error
    pool.close_all()


@patch("elims_common.mqtt.publisher.MQTTPublisher.connect")
@patch("elims_common.mqtt.publisher.MQTTPublisher.disconnect")
@patch("paho.mqtt.client.Client")
def test_connection_pool_close_with_connections(_mock_client: Any, _mock_disconnect: Any, mock_connect: Any, mqtt_config: MQTTConfig) -> None:
    """Test closing pool with active connections."""
    pool = MQTTConnectionPool(mqtt_config, pool_size=3, client_type="publisher")

    # Mock successful connection
    def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
        _self._connected = True  # noqa: SLF001

    mock_connect.side_effect = mock_conn_success

    # Create some connections
    conn1 = pool.get_connection()
    pool.return_connection(conn1)

    # Close pool
    pool.close_all()

    assert pool.is_closed
    assert pool.size == 0
    assert _mock_disconnect.called


@patch("paho.mqtt.client.Client")
def test_connection_pool_get_after_close(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test that getting connection from closed pool raises error."""
    pool = MQTTConnectionPool(mqtt_config, pool_size=3, client_type="publisher")
    pool.close_all()

    with pytest.raises(MQTTConnectionError, match="closed"):
        pool.get_connection()


def test_connection_pool_return_foreign_connection(mqtt_config: MQTTConfig) -> None:
    """Test returning connection that doesn't belong to pool."""
    pool = MQTTConnectionPool(mqtt_config, pool_size=3, client_type="publisher")

    # Create a foreign connection
    with patch("paho.mqtt.client.Client"):
        foreign_conn = MQTTPublisher(mqtt_config)

    with pytest.raises(ValueError, match="does not belong"):
        pool.return_connection(foreign_conn)


@patch("elims_common.mqtt.publisher.MQTTPublisher.connect")
@patch("paho.mqtt.client.Client")
def test_connection_pool_max_size(_mock_client: Any, mock_connect: Any, mqtt_config: MQTTConfig) -> None:
    """Test that pool respects max size."""
    pool = MQTTConnectionPool(mqtt_config, pool_size=2, client_type="publisher")

    # Mock successful connection
    def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
        _self._connected = True  # noqa: SLF001

    mock_connect.side_effect = mock_conn_success

    # Get connections up to max
    pool.get_connection()
    pool.get_connection()
    assert pool.size == 2  # noqa: PLR2004

    # Getting third without returning should timeout (non-blocking should fail)
    with pytest.raises(MQTTConnectionError, match="pool is full"):
        pool.get_connection(block=False)


@patch("elims_common.mqtt.publisher.MQTTPublisher.connect")
@patch("elims_common.mqtt.publisher.MQTTPublisher.disconnect")
@patch("paho.mqtt.client.Client")
def test_publisher_pool(_mock_client: Any, _mock_disconnect: Any, mock_connect: Any) -> None:
    """Test MQTTPublisherPool specialized class."""
    config = MQTTConfig(broker_host="localhost")

    # Mock successful connection
    def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
        _self._connected = True  # noqa: SLF001

    mock_connect.side_effect = mock_conn_success

    pool = MQTTPublisherPool(config, pool_size=2)

    # Should only create publisher clients
    conn = pool.get_connection()
    assert isinstance(conn, MQTTPublisher)

    pool.return_connection(conn)
    pool.close_all()


@patch("elims_common.mqtt.subscriber.MQTTSubscriber.connect")
@patch("elims_common.mqtt.subscriber.MQTTSubscriber.disconnect")
@patch("paho.mqtt.client.Client")
def test_subscriber_pool(_mock_client: Any, _mock_disconnect: Any, mock_connect: Any) -> None:
    """Test MQTTSubscriberPool specialized class."""
    config = MQTTConfig(broker_host="localhost")

    # Mock successful connection
    def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
        _self._connected = True  # noqa: SLF001

    mock_connect.side_effect = mock_conn_success

    pool = MQTTSubscriberPool(config, pool_size=2)

    # Should only create subscriber clients
    conn = pool.get_connection()
    assert isinstance(conn, MQTTSubscriber)

    pool.return_connection(conn)
    pool.close_all()


@patch("elims_common.mqtt.publisher.MQTTPublisher.connect")
@patch("elims_common.mqtt.publisher.MQTTPublisher.disconnect")
@patch("paho.mqtt.client.Client")
def test_pool_context_manager_cleanup(_mock_client: Any, _mock_disconnect: Any, mock_connect: Any) -> None:
    """Test that pool context manager closes all connections."""
    config = MQTTConfig(broker_host="localhost")

    # Mock successful connection
    def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
        _self._connected = True  # noqa: SLF001

    mock_connect.side_effect = mock_conn_success

    with MQTTPublisherPool(config, pool_size=2) as pool:
        conn = pool.get_connection()
        pool.return_connection(conn)
        assert not pool.is_closed

    # After exiting context, pool should be closed
    assert pool.is_closed


@patch("elims_common.mqtt.publisher.MQTTPublisher.connect")
@patch("paho.mqtt.client.Client")
def test_pool_connection_context_manager(_mock_client: Any, mock_connect: Any) -> None:
    """Test pool's get_connection_context manager."""
    config = MQTTConfig(broker_host="localhost")

    # Mock successful connection
    def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
        _self._connected = True  # noqa: SLF001

    mock_connect.side_effect = mock_conn_success

    pool = MQTTPublisherPool(config, pool_size=2)

    with pool.get_connection_context() as publisher:
        assert isinstance(publisher, MQTTPublisher)
        assert pool.available == 0  # Checked out

    # After context exits, connection should be returned
    assert pool.available == 1

    pool.close_all()


@patch("elims_common.mqtt.publisher.MQTTPublisher.connect")
@patch("paho.mqtt.client.Client")
def test_pool_properties(_mock_client: Any, mock_connect: Any, mqtt_config: MQTTConfig) -> None:
    """Test pool property accessors."""
    pool = MQTTConnectionPool(mqtt_config, pool_size=5, client_type="publisher")

    # Mock successful connection
    def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
        _self._connected = True  # noqa: SLF001

    mock_connect.side_effect = mock_conn_success

    assert pool.size == 0
    assert pool.available == 0
    assert not pool.is_closed

    # Create connections
    conn1 = pool.get_connection()
    assert pool.size == 1
    assert pool.available == 0

    pool.return_connection(conn1)
    assert pool.size == 1
    assert pool.available == 1

    pool.close_all()
    assert pool.is_closed
    assert pool.size == 0


@patch("elims_common.mqtt.publisher.MQTTPublisher.connect")
@patch("paho.mqtt.client.Client")
def test_pool_lazy_initialization(_mock_client: Any, mock_connect: Any, mqtt_config: MQTTConfig) -> None:
    """Test that pool creates connections lazily."""
    pool = MQTTConnectionPool(mqtt_config, pool_size=5, client_type="publisher")

    # No connections should be created initially
    assert pool.size == 0
    assert mock_connect.call_count == 0

    # Mock successful connection
    def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
        _self._connected = True  # noqa: SLF001

    mock_connect.side_effect = mock_conn_success

    # Only create when needed
    conn1 = pool.get_connection()
    assert pool.size == 1
    assert mock_connect.call_count == 1

    pool.return_connection(conn1)
    pool.close_all()


@patch("elims_common.mqtt.publisher.MQTTPublisher.connect")
@patch("paho.mqtt.client.Client")
def test_pool_concurrent_usage(_mock_client: Any, mock_connect: Any, mqtt_config: MQTTConfig) -> None:
    """Test pool with concurrent connection usage."""
    pool = MQTTConnectionPool(mqtt_config, pool_size=3, client_type="publisher")

    # Mock successful connection
    def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
        _self._connected = True  # noqa: SLF001

    mock_connect.side_effect = mock_conn_success

    # Get multiple connections
    conn1 = pool.get_connection()
    conn2 = pool.get_connection()
    conn3 = pool.get_connection()

    assert pool.size == 3  # noqa: PLR2004
    assert conn1 is not conn2
    assert conn2 is not conn3
    assert conn1 is not conn3

    # Return all
    pool.return_connection(conn1)
    pool.return_connection(conn2)
    pool.return_connection(conn3)

    assert pool.available == 3  # noqa: PLR2004

    pool.close_all()


@patch("elims_common.mqtt.subscriber.MQTTSubscriber.connect")
@patch("paho.mqtt.client.Client")
def test_subscriber_pool_type_safety(_mock_client: Any, mock_connect: Any) -> None:
    """Test that subscriber pool returns subscriber instances."""
    config = MQTTConfig(broker_host="localhost")

    # Mock successful connection
    def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
        _self._connected = True  # noqa: SLF001

    mock_connect.side_effect = mock_conn_success

    pool = MQTTSubscriberPool(config, pool_size=2)

    conn = pool.get_connection()
    assert isinstance(conn, MQTTSubscriber)
    assert not isinstance(conn, MQTTPublisher)

    pool.return_connection(conn)
    pool.close_all()


@patch("paho.mqtt.client.Client")
def test_pool_return_to_closed_pool(_mock_client: Any, mqtt_config: MQTTConfig) -> None:
    """Test returning connection to closed pool."""
    pool = MQTTConnectionPool(mqtt_config, pool_size=2, client_type="publisher")

    with patch("elims_common.mqtt.publisher.MQTTPublisher.connect") as mock_connect:

        def mock_conn_success(_self: Any, _timeout: float = 5.0) -> None:
            _self._connected = True  # noqa: SLF001

        mock_connect.side_effect = mock_conn_success

        conn = pool.get_connection()
        pool.close_all()

        # Should not raise, but log warning
        pool.return_connection(conn)
