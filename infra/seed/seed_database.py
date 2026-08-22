import argparse
import asyncio
import json
from datetime import datetime, timedelta
from pathlib import Path
from uuid import NAMESPACE_URL, UUID, uuid5

from database.config import get_database_settings
from database.models import (
	AlertModel,
	AuthEventModel,
	EnforcementActionModel,
	EventProcessingRunModel,
	EventSourceModel,
	FeatureSnapshotModel,
	HostInteractionSnapshotModel,
	IngestionCredentialModel,
	PolicyDecisionModel,
	RiskScoreModel,
	TenantModel,
	TenantOperatingModeModel,
	TenantThresholdProfileModel,
)
from database.session import (
	AsyncDatabaseConfig,
	create_database_engine,
	create_session_factory,
)
from domain.alert import AlertSeverity, AlertStatus
from domain.enforcement import EnforcementActionStatus, EnforcementActionType
from domain.event import AuthEventOutcome
from domain.policy import PolicyAction, ScoreBand
from domain.scoring import ProcessingJobType, ProcessingRunStatus
from sqlalchemy import select

SEED_DIR = Path(__file__).resolve().parent


def load_json(path: Path) -> dict:
	return json.loads(path.read_text(encoding='utf-8'))


def parse_datetime(value: str) -> datetime:
	return datetime.fromisoformat(value)


def stable_id(tenant_id: UUID, kind: str, key: str) -> UUID:
	return uuid5(NAMESPACE_URL, f'continuous-auth-seed:{tenant_id}:{kind}:{key}')


async def get_or_create_event(
	session,
	*,
	tenant_id: UUID,
	source_id: UUID,
	credential_id: UUID | None,
	key: str,
	data: dict,
) -> AuthEventModel:
	result = await session.execute(
		select(AuthEventModel).where(
			AuthEventModel.tenant_id == tenant_id,
			AuthEventModel.source_event_id == data['source_event_id'],
		)
	)
	event = result.scalar_one_or_none()
	if event is not None:
		return event

	occurred_at = parse_datetime(data['occurred_at'])
	event = AuthEventModel(
		id=stable_id(tenant_id, 'auth-event', key),
		tenant_id=tenant_id,
		event_source_id=source_id,
		ingestion_credential_id=credential_id,
		source_event_id=data['source_event_id'],
		idempotency_key=f'seed:{key}',
		occurred_at=occurred_at,
		ingested_at=occurred_at + timedelta(seconds=1),
		event_type=data['event_type'],
		outcome=AuthEventOutcome(data['outcome']),
		user_hash=data['user_hash'],
		account_hash=data.get('account_hash'),
		session_hash=data.get('session_hash'),
		source_ip_hash=data.get('source_ip_hash'),
		source_ip_prefix=data.get('source_ip_prefix'),
		device_hash=data.get('device_hash'),
		host_hash=data.get('host_hash'),
		auth_method=data.get('auth_method'),
		failure_reason=data.get('failure_reason'),
		location_country=data.get('location_country'),
		location_region=data.get('location_region'),
		occurred_hour=data['occurred_hour'],
		occurred_day_of_week=data['occurred_day_of_week'],
		hash_key_version=data['hash_key_version'],
		payload_schema_version=data['payload_schema_version'],
		raw_payload_redacted={'seed_key': key},
		normalization_metadata={'seeded': True},
	)
	session.add(event)
	await session.flush()
	return event


async def seed_database(seed: dict, state: dict) -> None:
	if not state.get('tenant_id'):
		raise RuntimeError(
			'Run seed_api.py first so seed-state.json contains a tenant_id.'
		)

	tenant_id = UUID(state['tenant_id'])
	settings = get_database_settings()
	engine = create_database_engine(AsyncDatabaseConfig.from_settings(settings))
	session_factory = create_session_factory(engine)

	try:
		async with session_factory() as session:
			tenant = await session.get(TenantModel, tenant_id)
			if tenant is None:
				raise RuntimeError(f'Tenant {tenant_id} was not found.')

			source = await session.get(EventSourceModel, UUID(state['event_source_id']))
			credential = await session.get(
				IngestionCredentialModel, UUID(state['ingestion_credential_id'])
			)
			if source is None or credential is None:
				raise RuntimeError(
					'Seed event source or ingestion credential was not found.'
				)

			mode_result = await session.execute(
				select(TenantOperatingModeModel).where(
					TenantOperatingModeModel.tenant_id == tenant_id,
					TenantOperatingModeModel.is_active.is_(True),
				)
			)
			operating_mode = mode_result.scalar_one()
			profile_result = await session.execute(
				select(TenantThresholdProfileModel).where(
					TenantThresholdProfileModel.tenant_id == tenant_id,
					TenantThresholdProfileModel.is_active.is_(True),
				)
			)
			threshold_profile = profile_result.scalar_one()

			events: dict[str, AuthEventModel] = {}
			for item in seed['database']['auth_events']:
				events[item['key']] = await get_or_create_event(
					session,
					tenant_id=tenant_id,
					source_id=source.id,
					credential_id=credential.id,
					key=item['key'],
					data=item,
				)

			runs: dict[str, EventProcessingRunModel] = {}
			for item in seed['database']['processing_runs']:
				run_id = stable_id(tenant_id, 'processing-run', item['key'])
				run = await session.get(EventProcessingRunModel, run_id)
				if run is None:
					run = EventProcessingRunModel(
						id=run_id,
						tenant_id=tenant_id,
						auth_event_id=events[item['event_key']].id,
						job_type=ProcessingJobType(item['job_type']),
						status=ProcessingRunStatus(item['status']),
						attempt_count=item['attempt_count'],
						correlation_id=item['correlation_id'],
						queued_at=parse_datetime(item['queued_at']),
						started_at=parse_datetime(item['started_at']),
						finished_at=parse_datetime(item['finished_at']),
					)
					session.add(run)
				runs[item['key']] = run

			features: dict[str, FeatureSnapshotModel] = {}
			for item in seed['database']['feature_snapshots']:
				feature_id = stable_id(tenant_id, 'feature-snapshot', item['key'])
				feature = await session.get(FeatureSnapshotModel, feature_id)
				if feature is None:
					event = events[item['event_key']]
					feature = FeatureSnapshotModel(
						id=feature_id,
						tenant_id=tenant_id,
						auth_event_id=event.id,
						processing_run_id=runs[item['run_key']].id,
						window_start=event.occurred_at - timedelta(days=7),
						window_end=event.occurred_at,
						computed_at=event.occurred_at + timedelta(seconds=3),
						**{
							field: item[field]
							for field in (
								'login_frequency',
								'avg_inter_event_time',
								'time_since_last_login',
								'unique_hosts',
								'host_entropy',
								'top_host_ratio',
								'degree_centrality',
								'hour_of_day',
								'day_of_week',
								'feature_version',
							)
						},
					)
					session.add(feature)
				features[item['key']] = feature

			for item in seed['database']['host_interaction_snapshots']:
				host_id = stable_id(tenant_id, 'host-snapshot', item['key'])
				host = await session.get(HostInteractionSnapshotModel, host_id)
				if host is None:
					event = events[item['event_key']]
					host = HostInteractionSnapshotModel(
						id=host_id,
						tenant_id=tenant_id,
						auth_event_id=event.id,
						processing_run_id=runs[item['run_key']].id,
						window_start=event.occurred_at - timedelta(days=7),
						window_end=event.occurred_at,
						user_hash=item['user_hash'],
						host_hash=item['host_hash'],
						interaction_count=item['interaction_count'],
						last_interaction_at=event.occurred_at,
						snapshot_version=1,
						computed_at=event.occurred_at + timedelta(seconds=3),
					)
					session.add(host)

			scores: dict[str, RiskScoreModel] = {}
			for item in seed['database']['risk_scores']:
				score_id = stable_id(tenant_id, 'risk-score', item['key'])
				score = await session.get(RiskScoreModel, score_id)
				if score is None:
					event = events[item['event_key']]
					score = RiskScoreModel(
						id=score_id,
						tenant_id=tenant_id,
						auth_event_id=event.id,
						feature_snapshot_id=features[item['feature_key']].id,
						processing_run_id=runs[item['run_key']].id,
						model_version=item['model_version'],
						threshold_profile_id=threshold_profile.id,
						caution_threshold_applied=threshold_profile.caution_threshold,
						lockout_threshold_applied=threshold_profile.lockout_threshold,
						scored_at=event.occurred_at + timedelta(seconds=4),
						**{
							field: item[field]
							for field in (
								'global_anomaly_score',
								'local_anomaly_score_raw',
								'local_anomaly_score_normalized',
								'fusion_alpha',
								'fused_anomaly_score',
							)
						},
					)
					score.score_band = ScoreBand(item['score_band'])
					session.add(score)
				scores[item['key']] = score

			decisions: dict[str, PolicyDecisionModel] = {}
			for item in seed['database']['policy_decisions']:
				decision_id = stable_id(tenant_id, 'policy-decision', item['key'])
				decision = await session.get(PolicyDecisionModel, decision_id)
				if decision is None:
					event = events[item['event_key']]
					decision = PolicyDecisionModel(
						id=decision_id,
						tenant_id=tenant_id,
						auth_event_id=event.id,
						risk_score_id=scores[item['score_key']].id,
						operating_mode_id=operating_mode.id,
						decision_band=ScoreBand(item['decision_band']),
						recommended_action=PolicyAction(item['recommended_action']),
						final_action=PolicyAction(item['final_action']),
						decision_reason=item['decision_reason'],
						decision_metadata={'seeded': True},
						decided_at=event.occurred_at + timedelta(seconds=5),
					)
					session.add(decision)
				decisions[item['key']] = decision

			for item in seed['database']['alerts']:
				alert_id = stable_id(tenant_id, 'alert', item['key'])
				if await session.get(AlertModel, alert_id) is None:
					session.add(
						AlertModel(
							id=alert_id,
							tenant_id=tenant_id,
							policy_decision_id=decisions[item['decision_key']].id,
							risk_score_id=scores[item['score_key']].id,
							severity=AlertSeverity(item['severity']),
							status=AlertStatus(item['status']),
							title=item['title'],
							summary=item['summary'],
							alert_metadata={'seeded': True},
							acknowledged_at=parse_datetime(item['acknowledged_at'])
							if item.get('acknowledged_at')
							else None,
						)
					)

			for item in seed['database']['enforcement_actions']:
				action_id = stable_id(tenant_id, 'enforcement-action', item['key'])
				if await session.get(EnforcementActionModel, action_id) is None:
					session.add(
						EnforcementActionModel(
							id=action_id,
							tenant_id=tenant_id,
							policy_decision_id=decisions[item['decision_key']].id,
							event_source_id=source.id
							if item.get('event_source_required')
							else None,
							action_type=EnforcementActionType(item['action_type']),
							target_user_hash=item['target_user_hash'],
							integration_name=item['integration_name'],
							request_payload_redacted={'seeded': True},
							status=EnforcementActionStatus(item['status']),
							attempt_count=item['attempt_count'],
							external_action_id=item.get('external_action_id'),
							requested_at=parse_datetime(item['requested_at']),
							completed_at=parse_datetime(item['completed_at'])
							if item.get('completed_at')
							else None,
						)
					)

			await session.commit()
			print(f'Seeded dashboard records for tenant {tenant_id}.')
	finally:
		await engine.dispose()


def main() -> None:
	parser = argparse.ArgumentParser(description=__doc__)
	parser.add_argument('--seed-file', type=Path, default=SEED_DIR / 'seed-data.json')
	parser.add_argument('--state-file', type=Path, default=SEED_DIR / 'seed-state.json')
	args = parser.parse_args()
	asyncio.run(seed_database(load_json(args.seed_file), load_json(args.state_file)))


if __name__ == '__main__':
	main()
