import axios from 'axios';
import Cookies from 'js-cookie';

axios.defaults.withCredentials = true;

export async function fetchScanResults(endpoint) {
  const res = await axios.get(endpoint, { headers: { 'X-CSRF-TOKEN': Cookies.get('csrf_access_token') } });
  if (res.status !== 200) throw new Error('Network response not ok');
  return res.data;
}

export async function testAgent() {
  const res = await axios.get('/agent/test');
  if (res.status !== 200) throw new Error('Network response not ok');
  return res.data;
}

export async function register(email, password) {
  const res = await axios.post('/auth/register', { email, password }, { headers: { 'X-CSRF-TOKEN': Cookies.get('csrf_access_token') } });
  return res.data;
}

export async function login(email, password) {
  const res = await axios.post('/auth/login', { email, password }, { headers: { 'X-CSRF-TOKEN': Cookies.get('csrf_access_token') } });
  return res.data;
}

export async function logout() {
  const res = await axios.post('/auth/logout', {}, { headers: { 'X-CSRF-TOKEN': Cookies.get('csrf_access_token') } });
  return res.data;
}

export async function refreshToken() {
  const res = await axios.post('/auth/refresh', {}, { headers: { 'X-CSRF-TOKEN': Cookies.get('csrf_refresh_token') } });
  return res.data;
}