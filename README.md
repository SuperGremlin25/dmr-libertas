# DMR Libertas

**Open Source DMR Radio Driver & AI Integration Platform**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Build Status](https://github.com/SuperGremlin25/dmr-libertas/actions/workflows/ci.yml/badge.svg)](https://github.com/SuperGremlin25/dmr-libertas/actions)
[![Docker Pulls](https://img.shields.io/docker/pulls/dmrlibertas/backend)](https://hub.docker.com/r/dmrlibertas/backend)

## 🚀 Overview

DMR Libertas is an open-source platform that liberates your DMR radio from vendor lock-in, adding AI-powered features while maintaining compatibility with existing DMR networks.

### Key Features

- **Universal DMR Radio Interface** - Works with multiple DMR radio models
- **AI-Powered Features** - Voice transcription, translation, and alerting
- **Cross-Platform** - Runs on x86_64 and ARM64 (Raspberry Pi)
- **Modern Web Interface** - Real-time monitoring and control
- **Extensible Architecture** - Plugin system for custom features

## 🛠 Hardware Support

### Tested Radios
- Anytone AT-D578UVIII Plus
- BTECH DMR-6X2
- TYT MD-UV380
- Radioddity GD-77

### Recommended AI Hardware
- Raspberry Pi 5 with Hailo-8L AI accelerator
- NVIDIA Jetson Nano/Orin NX (for advanced AI workloads)
- Seeed Studio reComputer (Jetson-based alternative)

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.10+
- Node.js 18+

### Running with Docker (Recommended)

1. Clone the repository:
   ```bash
   git clone https://github.com/SuperGremlin25/dmr-libertas.git
   cd dmr-libertas
   ```

2. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

3. Start the services:
   ```bash
   docker-compose up -d
   ```

4. Access the web interface at http://localhost:3000

### Development Setup

1. Set up Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   pip install -r backend/requirements-dev.txt
   ```

2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   cd ..
   ```

3. Start the development servers:
   ```bash
   # Terminal 1: Backend
   cd backend
   uvicorn main:app --reload
   
   # Terminal 2: Frontend
   cd frontend
   npm run dev
   ```

## 🤖 AI Features

- **Real-time Voice Transcription** - Convert DMR audio to text
- **Keyword Spotting** - Get alerts for important transmissions
- **Language Translation** - Break language barriers in real-time
- **Sentiment Analysis** - Gauge the emotional tone of communications

## 📡 Protocol Support

- DMR Tier I/II
- P25 Phase 1/2 (Planned)
- NXDN (Future)
- M17 (Future)

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- Email: your.email@example.com
- Twitter: [@dmrlibertas](https://twitter.com/dmrlibertas)
- GitHub Issues: [Issues](https://github.com/SuperGremlin25/dmr-libertas/issues)

## 🙏 Acknowledgments

- All the amazing open-source projects that make this possible
- The DMR community for their support and feedback
- Early testers and contributors

---

*"Libertas per Technologia" - Freedom through Technology*