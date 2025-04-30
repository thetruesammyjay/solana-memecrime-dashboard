# Solana Memecrime Investigation (MCSI)

> On-chain forensic toolkit for detecting rug pulls and scam tokens on Solana

## Features

- 🕵️‍♂️ Real-time token launch monitoring
- 📉 Liquidity pool anomaly detection
- 🚨 Automated alert system
- 🔗 Wallet clustering and entity resolution
- 📊 Interactive dashboard visualization

## Dune Dashboard Link
- [MCSI SOLANA MEMECRIME MONITOR](https://dune.com/thetruesammyjay/mcsi-solana-memecrime-monitor)

## Tech Stack

**Blockchain Layer:**
- Solana RPC/WebSocket
- Dune Analytics SQL
- Custom indexers

**Backend:**
- Python 3.10+
- FastAPI
- PostgreSQL/TimescaleDB
- Redis (caching)

**Frontend:**
- Vue.js 3
- D3.js
- Tailwind CSS

## Getting Started

### Prerequisites

- Python 3.10+
- PostgreSQL 14+
- Node.js 18+
- Solana CLI tools

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/thetruesammyjay/solana-memecrime-dashboard.git
   cd solana-memecrime
   ```
2. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```
3. Install backend dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Setup database:
   ```bash
   alembic upgrade head
   ```
5. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```

### Running Locally
**Start backend**:
```bash
uvicorn backend.main:app --reload
```

**Start frontend**:
```bash
cd frontend
npm run dev
```
The dashboard will be available at `http://localhost:3000` and API at `http://localhost:8000`

## Project Structure
```markdown
solana-memecrime/
├── blockchain/      # On-chain analysis
├── backend/         # API and services  
├── frontend/        # Dashboard UI
├── docs/            # Documentation
└── scripts/         # Utility scripts
```

## Contributing
1. Fork the project

2. Create your feature branch (`git checkout -b feature/AmazingFeature`)

3. Commit your changes (`git commit -m 'Add some amazing feature'`)

4. Push to the branch (`git push origin feature/AmazingFeature`)

5. Open a Pull Request

## License
Distributed under the MIT License. See `LICENSE` for more information.

## Contact Me
- **Projet Lead**: [@thatbwoysammyj](x.com/thatbwoysammyj)
- **Email**: [thetruesammyjay@gmail.com](mailto:thetruesammyjay@gmail.com)

Thanks for going through this repository, more updates would be made to this project before the end of Q2 2025
