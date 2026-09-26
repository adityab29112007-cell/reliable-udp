"""Passive per-transfer event counters and reporting.

Create one ``NetworkStatistics`` instance per transfer. Sender, receiver, and
future reliability code should call its ``record_*`` methods when events
occur, then use ``get_summary`` or ``print_report`` to inspect the results.
This module only records events; it never acts on packets or transfer state.
"""

from __future__ import annotations

import time


class NetworkStatistics:
	"""Record transfer events without performing networking or reliability."""

	def __init__(self) -> None:
		self.total_packets_sent = 0
		self.total_packets_received = 0
		self.packets_lost = 0
		self.packets_retransmitted = 0
		self.duplicate_packets = 0
		self.successful_transfers = 0
		self.failed_transfers = 0
		self._total_delay_seconds = 0.0
		self._delay_samples = 0
		self._started_at: float | None = None
		self._completed_at: float | None = None
		self._status = "NOT STARTED"

	def record_packet_sent(self) -> None:
		self.total_packets_sent += 1

	def record_packet_received(self) -> None:
		self.total_packets_received += 1

	def record_packet_lost(self) -> None:
		self.packets_lost += 1

	def record_retransmission(self) -> None:
		self.packets_retransmitted += 1

	def record_duplicate_packet(self) -> None:
		self.duplicate_packets += 1

	def record_packet_delay(self, delay_seconds: float) -> None:
		if delay_seconds < 0:
			raise ValueError("delay_seconds must be non-negative")
		self._total_delay_seconds += delay_seconds
		self._delay_samples += 1

	def record_transfer_start(self) -> None:
		if self._started_at is None:
			self._started_at = time.monotonic()
			self._status = "IN PROGRESS"

	def record_transfer_completion(self) -> None:
		if self._completed_at is None:
			self._completed_at = time.monotonic()
		if self._status in ("NOT STARTED", "IN PROGRESS"):
			self._status = "COMPLETED"

	def record_transfer_success(self) -> None:
		if self._status not in ("SUCCESS", "FAILED"):
			self.record_transfer_completion()
			self._status = "SUCCESS"
			self.successful_transfers += 1

	def record_transfer_failure(self) -> None:
		if self._status not in ("SUCCESS", "FAILED"):
			self.record_transfer_completion()
			self._status = "FAILED"
			self.failed_transfers += 1

	@property
	def average_delay_ms(self) -> float:
		if self._delay_samples == 0:
			return 0.0
		return (self._total_delay_seconds / self._delay_samples) * 1000.0

	@property
	def transfer_time_seconds(self) -> float:
		if self._started_at is None:
			return 0.0
		end_time = self._completed_at or time.monotonic()
		return end_time - self._started_at

	def get_summary(self) -> dict[str, int | float | str]:
		"""Return a snapshot suitable for a CLI, test, or later integration."""
		return {
			"packets_sent": self.total_packets_sent,
			"packets_received": self.total_packets_received,
			"packets_lost": self.packets_lost,
			"packets_retransmitted": self.packets_retransmitted,
			"duplicate_packets": self.duplicate_packets,
			"average_delay_ms": self.average_delay_ms,
			"transfer_time_seconds": self.transfer_time_seconds,
			"successful_transfers": self.successful_transfers,
			"failed_transfers": self.failed_transfers,
			"status": self._status,
		}

	def format_report(self, status: str | None = None) -> str:
		"""Format a readable report; ``status`` may describe a simulation run."""
		summary = self.get_summary()
		report_status = status or str(summary["status"])
		return "\n".join(
			(
				"========================================",
				"        NETWORK STATISTICS",
				"========================================",
				f"Packets Sent          : {summary['packets_sent']}",
				f"Packets Received      : {summary['packets_received']}",
				f"Packets Lost          : {summary['packets_lost']}",
				f"Packets Retransmitted : {summary['packets_retransmitted']}",
				f"Duplicate Packets     : {summary['duplicate_packets']}",
				f"Average Delay         : {summary['average_delay_ms']:.1f} ms",
				f"Transfer Time         : {summary['transfer_time_seconds']:.2f} seconds",
				f"Transfer Status       : {report_status}",
				"========================================",
			)
		)

	def print_report(self, status: str | None = None) -> None:
		print(self.format_report(status))
