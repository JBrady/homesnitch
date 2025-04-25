export async function fetchScanResults(endpoint) {
	const res = await fetch(endpoint);
	if (!res.ok) throw new Error("Network response not ok");
	return res.json();
}

export async function testAgent() {
	const res = await fetch("/agent/test");
	if (!res.ok) throw new Error("Network response not ok");
	return res.json();
}