import React from "react";
import RiskBadge from "./RiskBadge";

// Added onSelect prop to handle sidebar open
export default function DeviceTable({ devices, onSelect }) {
	return (
		<table className="min-w-full border">
			<thead>
				<tr>
					<th>IP</th><th>Vendor</th><th>Type</th><th>Queries</th><th>Data Sent</th><th>Risk</th><th>Action</th>
				</tr>
			</thead>
			<tbody>
				{devices.map(d => (
					<tr key={d.ip} className="border-t">
						<td>{d.ip}</td>
						<td>{d.vendor || "Unknown"}</td>
						<td>{d.type || "Unknown"}</td>
						<td>{d.query_count}</td>
						<td>{(d.data_sent || []).join(", ")}</td>
						<td><RiskBadge level={d.risk_level} /></td>
						<td><button className="text-blue-600 underline" onClick={() => onSelect && onSelect(d)}>Fix</button></td>
					</tr>
				))}
			</tbody>
		</table>
	);
}