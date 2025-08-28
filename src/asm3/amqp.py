"""
AMQP-backed asynchronous publisher for ASM3.

This module reads its configuration from ASM3's configuration store
(AMQPEnabled, AMQPBrokerUrl, AMQPExchangeName, AMQPRoutingKey),
starts a single background worker to own the AMQP connection, and
publishes JSON-serializable messages placed into an in-memory queue.

Public API:
    send_message(dbo, message) -> bool
    reinitialize(dbo) -> None
    close(drain: bool = False, drain_timeout: float = 5.0) -> None
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from queue import Empty, Queue as ThreadQueue
from threading import Event, Lock, Thread
from typing import Optional

from asm3 import configuration
from kombu import Connection, Exchange, Producer, Queue

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class _Config:
    """Immutable snapshot of effective AMQP settings."""
    enabled: bool
    broker_url: str
    exchange_name: str
    routing_key: str

    @property
    def valid(self) -> bool:
        return bool(self.broker_url and self.exchange_name and self.routing_key)


class AMQPClient:
    """
    Single-worker AMQP publisher.

    Thread-safety:
        - The public methods `ensure_config`, `send_message`, and `close` are safe to
          call from request threads.
        - The worker thread owns the AMQP connection/channel lifecycle.

    Reconfiguration:
        - On every `ensure_config`/`send_message` call, the latest settings are read
          and compared to the last applied snapshot. If they changed, the worker is
          restarted (or stopped if disabled).
    """

    def __init__(self) -> None:
        self._lock = Lock()
        self._outbox: ThreadQueue = ThreadQueue(maxsize=1000)
        self._stop = Event()
        self._worker: Optional[Thread] = None

        # Live connection state (worker thread only)
        self._connection: Optional[Connection] = None
        self._exchange: Optional[Exchange] = None
        self._connected: bool = False

        # Last applied configuration snapshot
        self._cfg: Optional[_Config] = None

    # --------------------------- public API ---------------------------

    def ensure_config(self, dbo) -> bool:
        """
        Sync the running worker with current ASM3 configuration.

        Returns:
            True if enabled and ready to accept messages, False otherwise.
        """
        cfg = _Config(
            enabled=configuration.amqp_enabled(dbo),
            broker_url=configuration.amqp_broker_url(dbo),
            exchange_name=configuration.amqp_exchange_name(dbo),
            routing_key=configuration.amqp_routing_key(dbo),
        )

        with self._lock:
            if self._cfg == cfg:
                return cfg.enabled and self._worker is not None and self._worker.is_alive()

            # Apply changes
            self._cfg = cfg
            worker = self._stop_worker_locked()  # stop old worker if any (non-blocking)
            # Join outside lock to avoid deadlocks
        if worker:
            worker.join(timeout=2.0)

        if not cfg.enabled:
            logger.info("AMQP disabled; worker stopped.")
            return False
        if not cfg.valid:
            logger.warning("AMQP misconfigured; missing broker/exchange/routing key.")
            return False

        with self._lock:
            self._start_worker_locked(cfg)
            return True

    def send_message(self, dbo, message: dict, *, block: bool = False, timeout: float = 0.0) -> bool:
        """
        Enqueue a message for asynchronous publish.

        Args:
            dbo: ASM3 database/session object used to read current configuration.
            message: JSON-serializable dict to publish.
            block: Whether to block if the internal queue is full.
            timeout: Seconds to wait if `block=True`.

        Returns:
            True if accepted into the outbox; False otherwise (disabled/misconfigured/full).
        """
        if not self.ensure_config(dbo):
            logger.debug("AMQP disabled or misconfigured; dropping message.")
            return False
        try:
            self._outbox.put(message, block=block, timeout=timeout)
            return True
        except Exception as e:  # queue.Full or other runtime issues
            logger.exception("Failed to enqueue AMQP message: %s", e)
            return False

    def close(self, drain: bool = False, drain_timeout: float = 5.0) -> None:
        """
        Stop the worker and release resources.

        Args:
            drain: If True, wait briefly for the outbox to drain before stopping.
            drain_timeout: Max seconds to wait for draining.
        """
        if drain:
            t0 = time.time()
            while not self._outbox.empty() and (time.time() - t0) < drain_timeout:
                time.sleep(0.05)

        with self._lock:
            worker = self._stop_worker_locked()
        if worker:
            worker.join(timeout=2.0)

    # ------------------------ worker lifecycle ------------------------

    def _start_worker_locked(self, cfg: _Config) -> None:
        """Start worker with the provided configuration (lock must be held)."""
        self._stop.clear()
        self._connected = False
        self._worker = Thread(target=self._run, name="kombu-worker", daemon=True)
        self._worker.start()
        logger.info("AMQP worker started (exchange=%s, routing_key=%s).", cfg.exchange_name, cfg.routing_key)

    def _stop_worker_locked(self) -> Optional[Thread]:
        """Signal worker to stop and return the thread to join outside the lock."""
        self._stop.set()
        worker, self._worker = self._worker, None
        # Let the worker loop notice _stop and exit; connection is released there.
        return worker

    # --------------------------- worker loop --------------------------

    def _run(self) -> None:
        """Worker thread: connect, declare, and publish outbox messages."""
        backoff = 1.0
        while not self._stop.is_set():
            if not self._connected:
                try:
                    self._connect_and_declare()
                    self._connected = True
                    backoff = 1.0
                except Exception as e:
                    self._connected = False
                    logger.warning("AMQP connect/declare failed: %s; retry in %.1fs", e, backoff)
                    time.sleep(backoff)
                    backoff = min(backoff * 2.0, 30.0)
                    continue

            try:
                msg = self._outbox.get(timeout=0.5)
            except Empty:
                continue

            try:
                ch = self._connection.channel()  # type: ignore[union-attr]
                try:
                    Producer(ch, exchange=self._exchange, routing_key=self._cfg.routing_key).publish(  # type: ignore[arg-type]
                        msg,
                        retry=True,
                        retry_policy={"max_retries": 3, "interval_start": 0, "interval_step": 1, "interval_max": 2},
                    )
                finally:
                    ch.close()
            except Exception as e:
                logger.warning("AMQP publish failed: %s; will reconnect", e)
                self._connected = False
                # Best-effort: requeue the message; if the queue is momentarily full, drop with a log.
                try:
                    self._outbox.put_nowait(msg)
                except Exception:
                    logger.error("AMQP outbox full; dropping message after publish failure.")
                self._safe_release()

        # Shutdown path
        self._safe_release()
        self._connected = False

    # ------------------------- connection setup -----------------------

    def _connect_and_declare(self) -> None:
        """Establish connection and declare exchange/queue (worker thread)."""
        cfg = self._cfg  # capture snapshot
        if not cfg or not cfg.valid:
            raise RuntimeError("AMQP configuration not set")

        self._connection = Connection(cfg.broker_url, heartbeat=10, connect_timeout=5)
        self._connection.ensure_connection(max_retries=3)

        self._exchange = Exchange(cfg.exchange_name, type="direct", durable=True)

        ch = self._connection.channel()
        try:
            # Declare exchange first, then queue bound to routing key.
            self._exchange(ch).declare()
            Queue(
                name=cfg.routing_key,
                exchange=self._exchange,
                routing_key=cfg.routing_key,
                durable=True,
            ).bind(ch).declare()
        finally:
            ch.close()

    def _safe_release(self) -> None:
        """Release AMQP connection safely."""
        try:
            if self._connection:
                self._connection.release()
        except Exception:
            pass
        self._connection = None
        self._exchange = None


# ------------------------- module-level facade -------------------------

_client = AMQPClient()


def reinitialize(dbo) -> None:
    """Force a configuration refresh and (re)start/stop the worker as needed."""
    _client.ensure_config(dbo)


def send_message(dbo, message: dict) -> bool:
    """
    Enqueue a message to be published by the background worker.

    Returns:
        True if accepted into the outbox; False if disabled/misconfigured or full.
    """
    return _client.send_message(dbo, message)


def close(drain: bool = False, drain_timeout: float = 5.0) -> None:
    """Stop the background worker and release all resources."""
    _client.close(drain=drain, drain_timeout=drain_timeout)

