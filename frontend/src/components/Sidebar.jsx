import React from "react";

export default function Sidebar({ device, onClose }) {
    if (!device) return null;
    return (
        <div className="fixed right-0 top-0 h-full w-1/3 bg-white shadow-lg p-4 overflow-auto">
            <button onClick={onClose} className="float-right text-gray-500 hover:text-gray-800 text-2xl leading-none">&times;</button>
            <h2 className="text-xl font-bold mb-2">Device Details</h2>
            <p><strong>IP:</strong> {device.ip}</p>
            <p><strong>Vendor:</strong> {device.vendor}</p>
            <p><strong>Type:</strong> {device.type}</p>
            <p><strong>Risk Level:</strong> {device.risk_level}</p>
            <p><strong>Query Count:</strong> {device.query_count}</p>
            <p><strong>Data Sent:</strong></p>
            <ul className="list-disc list-inside mb-2">
                {device.data_sent.map((dom, i) => <li key={i}>{dom}</li>)}
            </ul>
            <p><strong>Suggestions:</strong></p>
            <ul className="list-decimal list-inside">
                {device.suggestions.map((s, i) => <li key={i}>{s}</li>)}
            </ul>
        </div>
    );
}
