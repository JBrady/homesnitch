import React, { useState, useEffect } from "react";
import DeviceTable from "./components/DeviceTable";
import Sidebar from "./components/Sidebar";
import Controls from "./components/Controls";
import { fetchScanResults } from "./utils/api";

export default function App() {
	const [devices, setDevices] = useState([]);
	const [selectedDevice, setSelectedDevice] = useState(null);
	const loadDevices = async () => setDevices(await fetchScanResults("/scan_with_score"));
	useEffect(() => { loadDevices(); }, []);
	return (
		<div className="p-4">
			<h1 className="text-2xl font-bold mb-4">HomeSnitch Dashboard</h1>
			<Controls onRescan={loadDevices} />
			<DeviceTable devices={devices} onSelect={setSelectedDevice} />
			<Sidebar device={selectedDevice} onClose={() => setSelectedDevice(null)} />
		</div>
	);
}