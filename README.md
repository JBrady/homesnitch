# HomeSnitch

**HomeSnitch** is a network scanning and privacy monitoring tool that discovers devices on your local network, captures their DNS queries, and displays risk scores and details in a web dashboard.

## Features

- Automatic local network discovery (Nmap ➔ Scapy ARP fallback)
- DNS query capture (Scapy sniff ➔ Tshark CLI fallback)
- Device risk scoring based on DNS activity
- User authentication (register, login, logout) via Flask-JWT-Extended with HTTP-only, secure cookies
- Real-time dashboard with rescan, agent test, device table, and details sidebar
- Rate limiting, CORS, CSRF protection, and development-friendly security via Flask-Talisman
- Interactive front end built with React, Vite, and Tailwind CSS
- Unit and integration tests using Vitest, React Testing Library, and MSW mocks

## Tech Stack

- **Frontend:**
  - React 18, Vite 5.x
  - React Router, Axios, js-cookie
  - Tailwind CSS
  - Vitest + React Testing Library + MSW for tests

- **Backend:**
  - Python 3.13, Flask 3.x
  - Flask-SQLAlchemy, Flask-Migrate
  - Flask-JWT-Extended, Flask-CORS, Flask-Limiter
  - Flask-Talisman for HTTP security headers
  - Scapy for packet sniffing, Tshark CLI fallback
  - Nmap for network discovery (with Scapy fallback)

## Prerequisites

- Node.js v16+ and npm
- Python 3.10+ and pip
- `tshark` (Wireshark CLI) for DNS capture fallback
- `nmap` for device discovery fallback

## Getting Started

1. **Clone the repository**
   ```bash
   git clone https://github.com/<your-username>/home_snitch.git
   cd home_snitch
   ```

2. **Backend setup**
   ```powershell
   cd backend
   python -m venv .venv
   .\.venv\Scripts\activate   # (Windows)
   # OR source .venv/bin/activate (macOS/Linux)
   pip install -r requirements.txt
   ```

   > **Environment variables:**
   > - `FLASK_APP=backend.api`
   > - `FRONTEND_ORIGIN=http://localhost:3000`

3. **Run backend**
   ```powershell
   flask run --host 127.0.0.1 --port 5000
   ```

4. **Frontend setup & run**
   ```bash
   cd ../frontend
   npm install
   npm run dev
   ```

   Open http://localhost:3000 in your browser.


## Testing

- **Frontend tests:**
  ```bash
  cd frontend
  npm run test
  ```

- **Backend tests:** (TBD)

## Project Structure

```
home_snitch/
├── backend/
│   ├── api.py            # Flask app & routes
│   ├── traffic_monitor.py  # DNS capture & network scan logic
│   ├── extensions.py     # Flask extensions initialization
│   └── config.py         # App configuration
│
├── frontend/
│   ├── src/              # React components, contexts, pages
│   ├── vite.config.js    # Vite dev server & proxy config
│   └── __tests__/        # Vitest + RTL test suites
│
└── README.md
```

## Contributing

Contributions, issues, and feature requests are welcome. Please open an issue or submit a pull request.

## License

This project is licensed under the MIT License.
