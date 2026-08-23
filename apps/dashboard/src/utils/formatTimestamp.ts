export function formatTimestamp(value: string, now = new Date()) {
	const date = new Date(value);
	const sameYear = date.getFullYear() === now.getFullYear();
	const dateStart = new Date(now.getFullYear(), now.getMonth(), now.getDate());
	const eventStart = new Date(
		date.getFullYear(),
		date.getMonth(),
		date.getDate(),
	);
	const daysAgo = Math.round(
		(dateStart.getTime() - eventStart.getTime()) / (24 * 60 * 60 * 1000),
	);
	const time = new Intl.DateTimeFormat(undefined, {
		hour: '2-digit',
		minute: '2-digit',
	}).format(date);

	if (daysAgo === 0) return `Today · ${time}`;

	const datePart = new Intl.DateTimeFormat(undefined, {
		day: '2-digit',
		month: 'short',
		year: sameYear ? undefined : 'numeric',
	}).format(date);
	return `${datePart} · ${time}`;
}
