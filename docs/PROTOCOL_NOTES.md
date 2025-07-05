# DMR Libertas Protocol Notes

## Overview

This document details the communication protocols used in the DMR Libertas system. It serves as a technical reference for developers working on the project and for those interested in understanding the underlying communication mechanisms.

## DMR Protocol Implementation

### ETSI Standards Compliance

DMR Libertas implements the Digital Mobile Radio (DMR) protocol as defined by the European Telecommunications Standards Institute (ETSI) standards:

- ETSI TS 102 361-1: DMR Air Interface Protocol
- ETSI TS 102 361-2: Voice and General Services and Facilities
- ETSI TS 102 361-3: Data Protocol
- ETSI TS 102 361-4: Trunking Protocol

### Tier Implementation

The system currently implements DMR Tier II with plans for Tier III support:

- **Tier I**: Direct mode (not implemented)
- **Tier II**: Conventional repeater mode (implemented)
- **Tier III**: Trunking mode (planned for future releases)

## Frame Structure

### Basic Frame Format

DMR uses a TDMA (Time Division Multiple Access) structure with 2 time slots per frame:

```
+----------------+----------------+
|    Timeslot 1   |   Timeslot 2   |
| (30 ms payload) | (30 ms payload)|
+----------------+----------------+
        |                |
        v                v
+----------------+  +----------------+
| Sync + Data    |  | Sync + Data    |
| Payload: 216   |  | Payload: 216   |
| bits (27 bytes)|  | bits (27 bytes)|
+----------------+  +----------------+
```

### Burst Types

- **Voice Burst A-E**: Carries encoded voice data
- **Data Burst**: Carries user data or control information
- **CSBK Burst**: Control Signaling Block
- **Idle Burst**: Transmitted when no voice or data is present

## Voice Codec

DMR Libertas uses the AMBE+2™ vocoder for voice encoding/decoding:

- Bit rate: 3600 bps (2450 bps vocoder + 1150 bps FEC)
- Frame size: 72 bits per 20 ms of audio
- Sampling rate: 8 kHz

## Data Services

### Short Message Service (SMS)

- Unified Data Transport (UDT) for messages up to 288 bits
- Defined Data Transport (DDT) for larger messages
- Store-and-forward capability for offline users

### Location Services

- GPS position reporting using NMEA format
- Configurable reporting intervals
- Emergency location reporting

## Network Protocol

### IP Connectivity

DMR Libertas implements the following network protocols:

- **DMR Standard**: DMR-MARC compatible networking
- **Homebrew**: Open protocol for DMR networking
- **MMDVM**: Multi-Mode Digital Voice Modem protocol

### Packet Structure

The basic network packet structure for Homebrew protocol:

```
+---------------+---------------+---------------+
|    Header     |  Packet Type  |    Payload    |
| (4 bytes)     | (1 byte)      | (Variable)    |
+---------------+---------------+---------------+
```

Packet types:

- 0x01: Voice data
- 0x02: Voice sync
- 0x03: Data sync
- 0x04: Control data
- 0x05: Configuration

## Authentication and Security

### Authentication Methods

- **Basic**: Callsign and password authentication
- **DMR ID**: Validation against centralized DMR database
- **API Key**: For programmatic access to the system

### Encryption

- AES-256 encryption for voice and data (optional)
- Key distribution via secure channel
- Key rotation policies configurable by system administrator

## Custom Extensions

DMR Libertas implements several custom extensions to the standard DMR protocol:

### Enhanced Group Calls

- Dynamic talk group assignment
- Hierarchical talk group structure
- Temporary group formation

### Advanced Emergency Protocol

- Multi-level emergency states
- Automatic location transmission
- Prioritized channel access

### Mesh Networking

- Peer-to-peer communication without central infrastructure
- Store-and-forward message routing
- Dynamic route discovery

## API Endpoints

The DMR Libertas system exposes the following API endpoints for integration:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/calls` | GET | List recent calls |
| `/api/calls` | POST | Initiate a call |
| `/api/messages` | GET | Retrieve messages |
| `/api/messages` | POST | Send a message |
| `/api/status` | GET | System status |
| `/api/config` | GET/POST | Configuration |

## WebSocket Interface

Real-time updates are available via WebSocket connection:

```
ws://[server]/ws
```

Event types:

- `call_start`: New call initiated
- `call_end`: Call terminated
- `message`: New message received
- `status_update`: System status changed
- `emergency`: Emergency alert

## Implementation Notes

### Rate Limiting

- Voice transmissions limited to 180 seconds
- SMS rate limited to 10 messages per minute per user
- API calls limited to 100 requests per minute per IP

### Interoperability

- Compatible with Motorola, Hytera, and other commercial DMR systems
- BrandMeister network connectivity supported
- DMR+ network connectivity supported

## Future Protocol Enhancements

- Implementation of DMR Tier III trunking
- Enhanced encryption options
- Integration with other digital voice modes (P25, D-STAR)
- Advanced telemetry and IoT support

---

*Last updated: July 2025*