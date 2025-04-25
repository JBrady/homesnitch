import React from "react";
export default function Controls({ onRescan, onTest }) {
	return (
		<div className="flex space-x-2 mb-4">
			<button
				className="px-4 py-2 bg-blue-600 text-white rounded"
				onClick={onRescan}
			>
				Rescan
			</button>
			<button
				className="px-4 py-2 bg-green-600 text-white rounded"
				onClick={onTest}
			>
				Test Agent
			</button>
		</div>
	);
}