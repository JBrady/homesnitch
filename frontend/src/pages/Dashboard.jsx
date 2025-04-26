import React, { useState, useEffect } from 'react';
import DeviceTable from '../components/DeviceTable';
import Sidebar from '../components/Sidebar';
import Controls from '../components/Controls';
import { fetchScanResults, testAgent } from '../utils/api';

export default function Dashboard() {
  const [devices, setDevices] = useState([]);
  const [selectedDevice, setSelectedDevice] = useState(null);
  const [testStatus, setTestStatus] = useState(null);
  const [testError, setTestError] = useState('');
  const [scanStatus, setScanStatus] = useState('idle');
  const [scanError, setScanError] = useState('');

  const loadDevices = async () => {
    setScanStatus('loading');
    setScanError('');
    console.log('Rescan clicked: loading devices...');
    try {
      const data = await fetchScanResults('/scan_with_score');
      console.log('Scan data:', data);
      setDevices(data);
      setScanStatus('success');
    } catch (e) {
      console.error('Error scanning devices:', e);
      setScanError(e.message);
      setScanStatus('error');
    }
  };
  useEffect(() => { loadDevices(); }, []);

  const runAgentTest = async () => {
    setTestStatus('loading');
    setTestError('');
    try {
      await testAgent();
      setTestStatus('success');
    } catch(e) {
      setTestStatus('error');
      setTestError(e.message);
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-2xl font-bold mb-4">HomeSnitch Dashboard</h1>
      <Controls onRescan={loadDevices} onTest={runAgentTest} />
      {testStatus === 'loading' && <div>Testing agent...</div>}
      {testStatus === 'success' && <div className="text-green-600">Agent test successful!</div>}
      {testStatus === 'error' && <div className="text-red-600">Agent test failed: {testError}</div>}
      {scanStatus === 'loading' && <div>Scanning devices...</div>}
      {scanStatus === 'success' && <div className="text-green-600">Scan successful!</div>}
      {scanStatus === 'error' && <div className="text-red-600">Scan failed: {scanError}</div>}
      <DeviceTable devices={devices} onSelect={setSelectedDevice} />
      <Sidebar device={selectedDevice} onClose={() => setSelectedDevice(null)} />
    </div>
  );
}
