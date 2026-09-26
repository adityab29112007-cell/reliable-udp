"""Raw UDP transport with optional network-condition simulation.

Integration contract:
	Sender -> packet encoding -> UDPSimulator.send(bytes) -> UDP
	UDP -> UDPSimulator.receive() -> packet decoding -> receiver/reliability

ACK datagrams use the same transport in the reverse direction. This module
does not inspect or alter packet contents and does not implement reliability.
Each endpoint creates its own simulator; configure the same conditions on both
endpoints if both data and ACK paths should be impaired.
"""

from __future__ import annotations

import random
import socket
import time
import math
from typing import TypeAlias

from config import BUFFER_SIZE, HOST, PORT

Address: TypeAlias = tuple[str, int]


class UDPSimulator:
	"""Send and receive UDP bytes while simulating basic network conditions.

	``delay`` is a fixed number of seconds applied to each send attempt.
	``send`` returns the payload length when accepted by the simulator, even if
	it is being held briefly for reordering; it returns 0 when simulated loss
	drops it. ``receive`` returns raw bytes and the sender address, and raises
	``socket.timeout`` when its optional timeout expires.

	Bind a receiver with ``local_address=(HOST, PORT)``. A sender can leave
	``local_address`` unset to use an ephemeral local port and set
	``remote_address`` to the receiver. Pass the received source address to
	``send(..., address=source)`` when replying with an ACK.
	"""

	def __init__(
		self,
		remote_address: Address | None = None,
		local_address: Address | None = None,
		*,
		loss_probability: float = 0.0,
		delay: float = 0.0,
		duplication_probability: float = 0.0,
		reordering_probability: float = 0.0,
		seed: int | None = None,
		buffer_size: int = BUFFER_SIZE,
	) -> None:
		self._validate_probability("loss_probability", loss_probability)
		self._validate_probability("duplication_probability", duplication_probability)
		self._validate_probability("reordering_probability", reordering_probability)
		if not math.isfinite(delay) or delay < 0:
			raise ValueError("delay must be non-negative")
		if buffer_size <= 0:
			raise ValueError("buffer_size must be positive")

		self.remote_address = remote_address or (HOST, PORT)
		self.loss_probability = loss_probability
		self.delay = delay
		self.duplication_probability = duplication_probability
		self.reordering_probability = reordering_probability
		self.buffer_size = buffer_size
		self._random = random.Random(seed)
		self._socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		if local_address is not None:
			self._socket.bind(local_address)

		self.packets_attempted = 0
		self.packets_lost = 0
		self.packets_duplicated = 0
		self.packets_reordered = 0
		self.datagrams_sent = 0
		self.total_delay_seconds = 0.0
		self._pending: tuple[bytes, Address, int] | None = None
		self._closed = False

	@staticmethod
	def _validate_probability(name: str, value: float) -> None:
		if not math.isfinite(value) or not 0.0 <= value <= 1.0:
			raise ValueError(f"{name} must be between 0.0 and 1.0")

	@property
	def local_address(self) -> Address:
		"""Return the bound address (including an assigned ephemeral port)."""
		address = self._socket.getsockname()
		return address[0], address[1]

	def send(self, data: bytes, address: Address | None = None) -> int:
		"""Submit one bytes payload for UDP delivery, applying configured effects."""
		if not isinstance(data, bytes):
			raise TypeError("data must be bytes")
		if self._closed:
			raise OSError("simulator is closed")

		destination = address or self.remote_address
		self.packets_attempted += 1
		if self.delay:
			time.sleep(self.delay)
			self.total_delay_seconds += self.delay

		if self._random.random() < self.loss_probability:
			self.packets_lost += 1
			return 0

		copies = 2 if self._random.random() < self.duplication_probability else 1
		if copies > 1:
			self.packets_duplicated += 1

		if self._pending is not None:
			pending_data, pending_address, pending_copies = self._pending
			self._send_copies(data, destination, copies)
			self._send_copies(pending_data, pending_address, pending_copies)
			self._pending = None
			self.packets_reordered += 1
		elif self._random.random() < self.reordering_probability:
			self._pending = (data, destination, copies)
		else:
			self._send_copies(data, destination, copies)

		return len(data)

	def _send_copies(self, data: bytes, address: Address, copies: int) -> None:
		for _ in range(copies):
			self._socket.sendto(data, address)
			self.datagrams_sent += 1

	def receive(self, timeout: float | None = None) -> tuple[bytes, Address]:
		"""Receive one raw UDP datagram and its source address."""
		if self._closed:
			raise OSError("simulator is closed")
		self._socket.settimeout(timeout)
		data, address = self._socket.recvfrom(self.buffer_size)
		return data, (address[0], address[1])

	def flush(self) -> None:
		"""Send any datagram held for reordering when no later packet arrived."""
		if self._closed:
			raise OSError("simulator is closed")
		if self._pending is not None:
			data, address, copies = self._pending
			self._send_copies(data, address, copies)
			self._pending = None

	def close(self) -> None:
		"""Flush a held datagram and close the underlying UDP socket."""
		if not self._closed:
			self.flush()
			self._socket.close()
			self._closed = True

	def __enter__(self) -> UDPSimulator:
		return self

	def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
		self.close()
