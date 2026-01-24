"""ELIMS Common Package - MQTT Module - Connection Pool."""

import threading
from collections.abc import Generator
from contextlib import contextmanager
from queue import Empty, Queue

from elims_common.logger.logger import logger
from elims_common.mqtt.config import MQTTConfig
from elims_common.mqtt.exceptions import MQTTConnectionError
from elims_common.mqtt.publisher import MQTTPublisher
from elims_common.mqtt.subscriber import MQTTSubscriber


class MQTTConnectionPool:
    """Connection pool for managing multiple MQTT client connections.

    This pool manages a set of reusable MQTT connections (Publishers or Subscribers)
    to improve performance for applications that need multiple concurrent connections
    or frequent connect/disconnect cycles.

    Features:
    - Lazy connection initialization
    - Thread-safe connection checkout/checkin
    - Automatic connection health monitoring
    - Configurable pool size and timeout
    - Support for both Publisher and Subscriber clients

    Example:
        >>> config = MQTTConfig(broker_host="localhost")
        >>> pool = MQTTConnectionPool(config, pool_size=5, client_type="publisher")
        >>>
        >>> # Get a connection from pool
        >>> with pool.get_connection() as publisher:
        ...     publisher.publish("sensor/temperature", {"value": 22.5})
        >>>
        >>> # Connection is automatically returned to pool after use
        >>> pool.close_all()  # Cleanup when done

    """

    def __init__(
        self,
        config: MQTTConfig,
        pool_size: int = 5,
        client_type: str = "publisher",
        connection_timeout: float = 5.0,
        checkout_timeout: float = 30.0,
    ) -> None:
        """Initialize MQTT connection pool.

        Args:
            config: MQTT configuration for all connections in pool
            pool_size: Maximum number of connections in pool (must be >= 1)
            client_type: Type of client to pool ("publisher" or "subscriber")
            connection_timeout: Timeout for individual MQTT connections
            checkout_timeout: Timeout when waiting for available connection from pool

        Raises:
            ValueError: If pool_size < 1 or client_type is invalid

        """
        if pool_size < 1:
            msg = f"pool_size must be >= 1, got {pool_size}"
            raise ValueError(msg)

        if client_type not in ("publisher", "subscriber"):
            msg = f"client_type must be 'publisher' or 'subscriber', got '{client_type}'"
            raise ValueError(msg)

        self.config = config
        self.pool_size = pool_size
        self.client_type = client_type
        self.connection_timeout = connection_timeout
        self.checkout_timeout = checkout_timeout

        # Thread-safe queue for available connections
        self._pool: Queue[MQTTPublisher | MQTTSubscriber] = Queue(maxsize=pool_size)

        # Lock for pool operations
        self._lock = threading.Lock()

        # Track all created connections (for cleanup)
        self._all_connections: list[MQTTPublisher | MQTTSubscriber] = []

        # Pool state
        self._closed = False

        logger.info(f"Initialized MQTT {client_type} connection pool " f"(size: {pool_size}, timeout: {connection_timeout}s)")

    def _create_connection(self) -> MQTTPublisher | MQTTSubscriber:
        """Create a new MQTT connection.

        Returns:
            New MQTT Publisher or Subscriber instance

        Raises:
            MQTTConnectionError: If connection fails

        """
        client = MQTTPublisher(self.config) if self.client_type == "publisher" else MQTTSubscriber(self.config)

        # Connect to broker
        client.connect(timeout=self.connection_timeout)

        logger.debug(f"Created new {self.client_type} connection in pool")
        return client

    def _validate_connection(self, connection: MQTTPublisher | MQTTSubscriber) -> bool:
        """Validate that a connection is still healthy.

        Args:
            connection: Connection to validate

        Returns:
            True if connection is healthy, False otherwise

        """
        return connection.is_connected

    def get_connection(self, *, block: bool = True) -> MQTTPublisher | MQTTSubscriber:
        """Get a connection from the pool.

        If no connection is available and pool is not full, creates a new connection.
        If pool is full and no connection is available, waits for one to be returned.

        Args:
            block: Whether to block waiting for a connection if none available

        Returns:
            MQTT Publisher or Subscriber connection

        Raises:
            MQTTConnectionError: If pool is closed, connection creation fails,
                or timeout waiting for available connection

        """
        if self._closed:
            msg = "Connection pool is closed"
            raise MQTTConnectionError(msg)

        # Try to get existing connection from pool
        try:
            timeout = self.checkout_timeout if block else None
            connection = self._pool.get(block=block, timeout=timeout)

            # Validate connection health
            if self._validate_connection(connection):
                logger.debug(f"Reusing {self.client_type} connection from pool")
                return connection

            # Connection is unhealthy, try to reconnect
            logger.warning(f"Unhealthy {self.client_type} connection, reconnecting...")
            try:
                connection.disconnect()
                connection.connect(timeout=self.connection_timeout)
            except (MQTTConnectionError, OSError, TimeoutError) as e:
                logger.error(f"Failed to reconnect unhealthy connection: {e}")
                # Connection is dead, create a new one below
            else:
                return connection

        except Empty:
            # No connection available in pool
            pass

        # Create new connection if pool not full
        with self._lock:
            if len(self._all_connections) < self.pool_size:
                try:
                    connection = self._create_connection()
                    self._all_connections.append(connection)
                except Exception as e:
                    logger.error(f"Failed to create new connection: {e}")
                    raise
                else:
                    return connection

        # Pool is full and no connection available
        if not block:
            msg = f"No connection available and pool is full ({self.pool_size})"
            raise MQTTConnectionError(msg)

        # This shouldn't happen if block=True, but handle it
        msg = f"Timeout waiting for connection from pool ({self.checkout_timeout}s)"
        raise MQTTConnectionError(msg)

    def return_connection(self, connection: MQTTPublisher | MQTTSubscriber) -> None:
        """Return a connection to the pool.

        Args:
            connection: Connection to return to pool

        Raises:
            ValueError: If connection does not belong to this pool

        """
        if self._closed:
            logger.warning("Attempted to return connection to closed pool")
            return

        if connection not in self._all_connections:
            msg = "Connection does not belong to this pool"
            raise ValueError(msg)

        # Only return healthy connections to pool
        if self._validate_connection(connection):
            try:
                self._pool.put(connection, block=False)
                logger.debug(f"Returned {self.client_type} connection to pool")
            except (ValueError, TypeError):
                # Queue is full, this shouldn't happen
                logger.warning("Pool queue full, connection not returned")
        else:
            logger.warning("Unhealthy connection not returned to pool")

    @contextmanager
    def get_connection_context(self) -> Generator[MQTTPublisher | MQTTSubscriber]:
        """Context manager for automatic connection checkout and return.

        Yields:
            MQTT connection from pool

        Example:
            >>> with pool.get_connection_context() as publisher:
            ...     publisher.publish("topic", "message")

        """
        connection = self.get_connection()
        try:
            yield connection
        finally:
            self.return_connection(connection)

    def close_all(self) -> None:
        """Close all connections in the pool and mark pool as closed.

        This method should be called when the pool is no longer needed
        to ensure all MQTT connections are properly closed.

        """
        if self._closed:
            logger.warning("Pool already closed")
            return

        self._closed = True

        with self._lock:
            # Close all connections
            for connection in self._all_connections:
                try:
                    connection.disconnect()
                except (OSError, RuntimeError) as e:
                    logger.error(f"Error disconnecting {self.client_type}: {e}")

            # Clear tracking structures
            self._all_connections.clear()

            # Empty the queue
            while not self._pool.empty():
                try:
                    self._pool.get(block=False)
                except Empty:
                    break

        logger.info(f"Closed MQTT {self.client_type} connection pool")

    @property
    def size(self) -> int:
        """Get current number of connections in pool."""
        with self._lock:
            return len(self._all_connections)

    @property
    def available(self) -> int:
        """Get number of available connections in pool queue."""
        return self._pool.qsize()

    @property
    def is_closed(self) -> bool:
        """Check if pool is closed."""
        return self._closed

    def __enter__(self) -> "MQTTConnectionPool":
        """Context manager entry."""
        return self

    def __exit__(self, *_args: object) -> None:
        """Context manager exit - closes all connections."""
        self.close_all()


class MQTTPublisherPool(MQTTConnectionPool):
    """Specialized connection pool for MQTT Publishers.

    This is a convenience class that ensures the pool only contains
    Publisher clients. Provides type hints for better IDE support.

    Example:
        >>> config = MQTTConfig(broker_host="localhost")
        >>> with MQTTPublisherPool(config, pool_size=3) as pool:
        ...     with pool.get_connection_context() as publisher:
        ...         publisher.publish("topic", "message")

    """

    def __init__(
        self,
        config: MQTTConfig,
        pool_size: int = 5,
        connection_timeout: float = 5.0,
        checkout_timeout: float = 30.0,
    ) -> None:
        """Initialize MQTT Publisher pool.

        Args:
            config: MQTT configuration for all connections
            pool_size: Maximum number of publisher connections
            connection_timeout: Timeout for individual connections
            checkout_timeout: Timeout when waiting for available connection

        """
        super().__init__(
            config=config,
            pool_size=pool_size,
            client_type="publisher",
            connection_timeout=connection_timeout,
            checkout_timeout=checkout_timeout,
        )

    def get_connection(self, *, block: bool = True) -> MQTTPublisher:
        """Get a Publisher connection from pool.

        Args:
            block: Whether to block waiting for connection

        Returns:
            MQTTPublisher instance

        """
        return super().get_connection(block)  # type: ignore[return-value]

    @contextmanager
    def get_connection_context(self) -> Generator[MQTTPublisher]:
        """Context manager for automatic Publisher checkout and return.

        Yields:
            MQTTPublisher from pool

        """
        connection = self.get_connection()
        try:
            yield connection
        finally:
            self.return_connection(connection)


class MQTTSubscriberPool(MQTTConnectionPool):
    """Specialized connection pool for MQTT Subscribers.

    This is a convenience class that ensures the pool only contains
    Subscriber clients. Provides type hints for better IDE support.

    Note:
        When using subscriber pools, each subscriber maintains its own
        subscription state. Consider using a single subscriber with multiple
        topic subscriptions unless you specifically need multiple subscriber
        clients.

    Example:
        >>> config = MQTTConfig(broker_host="localhost")
        >>> with MQTTSubscriberPool(config, pool_size=2) as pool:
        ...     with pool.get_connection_context() as subscriber:
        ...         subscriber.subscribe("sensor/#", lambda topic, payload: print(payload))

    """

    def __init__(
        self,
        config: MQTTConfig,
        pool_size: int = 5,
        connection_timeout: float = 5.0,
        checkout_timeout: float = 30.0,
    ) -> None:
        """Initialize MQTT Subscriber pool.

        Args:
            config: MQTT configuration for all connections
            pool_size: Maximum number of subscriber connections
            connection_timeout: Timeout for individual connections
            checkout_timeout: Timeout when waiting for available connection

        """
        super().__init__(
            config=config,
            pool_size=pool_size,
            client_type="subscriber",
            connection_timeout=connection_timeout,
            checkout_timeout=checkout_timeout,
        )

    def get_connection(self, *, block: bool = True) -> MQTTSubscriber:
        """Get a Subscriber connection from pool.

        Args:
            block: Whether to block waiting for connection

        Returns:
            MQTTSubscriber instance

        """
        return super().get_connection(block)  # type: ignore[return-value]

    @contextmanager
    def get_connection_context(self) -> Generator[MQTTSubscriber]:
        """Context manager for automatic Subscriber checkout and return.

        Yields:
            MQTTSubscriber from pool

        """
        connection = self.get_connection()
        try:
            yield connection
        finally:
            self.return_connection(connection)
