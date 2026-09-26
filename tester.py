"""Demonstrate simulated UDP conditions, not a complete reliable transfer.

The sender/reliability/file-manager modules can later use this transport and
recorder. This standalone demo sends raw bytes from a temporary local UDP
sender to a receiver; it does not encode project packets, retransmit losses,
or verify reconstructed files.
"""

from __future__ import annotations

import socket
from dataclasses import dataclass

from config import HOST
from network import UDPSimulator
from statistics import NetworkStatistics

PACKET_COUNT = 100
BASE_SEED = 2026


@dataclass(frozen=True)
class Scenario:
	name: str
	loss_probability: float = 0.0
	delay: float = 0.0
	duplication_probability: float = 0.0
	reordering_probability: float = 0.0


SCENARIOS = (
	Scenario("TEST 1 - NO PACKET LOSS"),
	Scenario("TEST 2 - 10% PACKET LOSS", loss_probability=0.10),
	Scenario("TEST 3 - 20% PACKET LOSS", loss_probability=0.20),
	Scenario("TEST 4 - PACKET DELAY", delay=0.01),
	Scenario("TEST 5 - PACKET DUPLICATION", duplication_probability=0.10),
	Scenario("TEST 6 - PACKET REORDERING", reordering_probability=0.30),
	Scenario("TEST 7 - PACKET LOSS + DELAY", loss_probability=0.10, delay=0.005),
)


def run_scenario(scenario: Scenario, packet_count: int = PACKET_COUNT) -> dict[str, int | float | str]:
	"""Run one loopback UDP scenario and return its observed statistics."""
	if packet_count <= 0:
		raise ValueError("packet_count must be positive")

	stats = NetworkStatistics()
	receiver = UDPSimulator(local_address=(HOST, 0), seed=BASE_SEED)
	sender = UDPSimulator(
		remote_address=receiver.local_address,
		loss_probability=scenario.loss_probability,
		delay=scenario.delay,
		duplication_probability=scenario.duplication_probability,
		reordering_probability=scenario.reordering_probability,
		seed=BASE_SEED,
	)

	try:
		stats.record_transfer_start()
		expected_payloads = []
		for packet_number in range(packet_count):
			# Include NUL and non-UTF8 bytes to verify that transport is binary-safe.
			payload = bytes((packet_number % 256, 0, 255)) + packet_number.to_bytes(4, "big")
			expected_payloads.append(payload)
			stats.record_packet_sent()
			duplicates_before_send = sender.packets_duplicated
			if sender.send(payload) == 0:
				stats.record_packet_lost()
			for _ in range(sender.packets_duplicated - duplicates_before_send):
				stats.record_duplicate_packet()
			stats.record_packet_delay(scenario.delay)

		sender.flush()

		receive_timeout = max(0.05, scenario.delay * 2 + 0.02)
		received_payloads = []
		while True:
			try:
				payload, _ = receiver.receive(timeout=receive_timeout)
				received_payloads.append(payload)
				stats.record_packet_received()
			except socket.timeout:
				break

		expected_payload_set = set(expected_payloads)
		if any(payload not in expected_payload_set for payload in received_payloads):
			raise AssertionError("UDP transport changed a binary payload")
		received_numbers = [int.from_bytes(payload[3:], "big") for payload in received_payloads]
		reordered = any(
			earlier > later for earlier, later in zip(received_numbers, received_numbers[1:])
		)

		stats.record_transfer_completion()
		summary = stats.get_summary()
		summary["packets_reordered"] = sender.packets_reordered
		summary["reordering_observed"] = int(reordered)
		return summary
	finally:
		sender.close()
		receiver.close()


def print_scenario(scenario: Scenario, summary: dict[str, int | float | str]) -> None:
	print("=" * 40)
	print(scenario.name)
	print("=" * 40)
	print(f"Packet Loss          : {scenario.loss_probability:.0%}")
	print(f"Packet Delay         : {scenario.delay * 1000:.0f} ms")
	print(f"Duplicate Rate       : {scenario.duplication_probability:.0%}")
	print(f"Reordering Rate      : {scenario.reordering_probability:.0%}")
	print()
	print(f"Packets Sent         : {summary['packets_sent']}")
	print(f"Packets Received     : {summary['packets_received']}")
	print(f"Packets Lost         : {summary['packets_lost']}")
	print(f"Packets Retransmitted : {summary['packets_retransmitted']}")
	print(f"Duplicate Packets     : {summary['duplicate_packets']}")
	print(f"Reorder Events       : {summary['packets_reordered']}")
	print(f"Average Delay         : {summary['average_delay_ms']:.1f} ms")
	print(f"Transfer Time         : {summary['transfer_time_seconds']:.2f} seconds")
	print()
	print("Transfer Status      : SIMULATION COMPLETE")
	print("=" * 40)


def main() -> None:
	print("UDP NETWORK SIMULATION DEMO")
	print(f"Raw datagrams per scenario: {PACKET_COUNT}")
	print("This demonstrates network effects only; no reliable file transfer is run.\n")
	for scenario in SCENARIOS:
		print_scenario(scenario, run_scenario(scenario))
		print()


if __name__ == "__main__":
	main()
