from collections.abc import Mapping, Sequence
from typing import cast

from redis.asyncio import Redis
from redis.exceptions import ResponseError
from redis.typing import EncodableT, KeyT, StreamIdT

from event_broker.config import EventBrokerSettings
from event_broker.interfaces import StreamFields, StreamReadResult


class EventBrokerManager:
	def __init__(self, settings: EventBrokerSettings) -> None:
		"""Initialize the event broker manager.

		Args:
			settings: The event broker settings used to build the Redis client.
		"""
		self._settings = settings
		self._client: Redis | None = None

	async def initialize(self) -> None:
		"""Initialize the async Redis client."""
		if self._client is not None:
			return

		self._client = Redis.from_url(
			self._settings.EVENT_BROKER_URL,
			decode_responses=True,
		)

	async def check_connection(self) -> None:
		"""Verify that the event broker backend is reachable.

		Raises:
			RuntimeError: If the event broker manager has not been initialized.
		"""
		client = self.get_client()
		await client.ping()

	def get_client(self) -> Redis:
		"""Return the initialized Redis client.

		Returns:
			The initialized async Redis client.

		Raises:
			RuntimeError: If the event broker manager has not been initialized.
		"""
		if self._client is None:
			raise RuntimeError('Event broker manager has not been initialized.')

		return self._client

	async def publish(
		self,
		stream_name: str,
		fields: StreamFields,
		*,
		maxlen: int | None = None,
		approximate: bool = True,
	) -> str:
		"""Publish a message to the given Redis Stream.

		Args:
			stream_name: The target Redis Stream name.
			fields: The stream entry fields to publish.
			maxlen: Optional stream max length cap for ``XADD`` trimming.
			approximate: Whether ``MAXLEN`` trimming should be approximate.

		Returns:
			The Redis Stream entry identifier created by ``XADD``.
		"""
		client = self.get_client()
		stream_fields = cast(dict[EncodableT, EncodableT], dict(fields))
		message_id = await client.xadd(
			name=stream_name,
			fields=stream_fields,
			maxlen=maxlen
			if maxlen is not None
			else self._settings.EVENT_BROKER_DEFAULT_STREAM_MAXLEN,
			approximate=approximate,
		)
		return cast(str, message_id)

	async def create_consumer_group(
		self,
		stream_name: str,
		group_name: str,
		*,
		start_id: str = '$',
		mkstream: bool = False,
	) -> None:
		"""Create a consumer group for the given Redis Stream.

		Args:
			stream_name: The target Redis Stream name.
			group_name: The consumer group name to create.
			start_id: The starting stream identifier for the group cursor.
			mkstream: Whether to create the stream if it does not already exist.
		"""
		client = self.get_client()
		try:
			await client.xgroup_create(
				name=stream_name,
				groupname=group_name,
				id=start_id,
				mkstream=mkstream,
			)
		except ResponseError as error:
			if 'BUSYGROUP' in str(error):
				return
			raise

	async def read_group(
		self,
		group_name: str,
		consumer_name: str,
		streams: Mapping[str, str],
		*,
		count: int | None = None,
		block_ms: int | None = None,
	) -> StreamReadResult:
		"""Read messages for a consumer group from one or more streams.

		Args:
			group_name: The consumer group to read from.
			consumer_name: The consumer identity within the group.
			streams: Stream names mapped to the last-delivered IDs to request.
			count: Optional maximum number of entries to return.
			block_ms: Optional blocking wait time in milliseconds.

		Returns:
			The stream entries returned by ``XREADGROUP``.
		"""
		client = self.get_client()
		stream_map = cast(dict[KeyT, StreamIdT], dict(streams))
		entries = await client.xreadgroup(
			groupname=group_name,
			consumername=consumer_name,
			streams=stream_map,
			count=count,
			block=block_ms,
		)
		return cast(StreamReadResult, entries)

	async def acknowledge(
		self,
		stream_name: str,
		group_name: str,
		message_ids: Sequence[str],
	) -> int:
		"""Acknowledge one or more messages for the given consumer group.

		Args:
			stream_name: The target Redis Stream name.
			group_name: The consumer group that processed the messages.
			message_ids: The stream entry identifiers to acknowledge.

		Returns:
			The number of acknowledged messages.
		"""
		client = self.get_client()
		return cast(int, await client.xack(stream_name, group_name, *message_ids))

	async def delete_messages(
		self,
		stream_name: str,
		message_ids: Sequence[str],
	) -> int:
		"""Delete one or more messages from the given stream.

		Args:
			stream_name: The target Redis Stream name.
			message_ids: The stream entry identifiers to delete.

		Returns:
			The number of deleted messages.
		"""
		client = self.get_client()
		return cast(int, await client.xdel(stream_name, *message_ids))

	async def dispose(self) -> None:
		"""Dispose the async Redis client."""
		if self._client is None:
			return

		await self._client.aclose()
		self._client = None
