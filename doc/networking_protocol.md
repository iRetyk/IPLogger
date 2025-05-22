# Networking Protocol Documentation

## Overview
The networking protocol implements a client-server communication system using TCP sockets. The protocol uses a size-prefixed message format to ensure reliable message delivery and includes support for various operations like user authentication, URL management, and statistics retrieval.

## Base Network Architecture
The protocol is built on three main classes:
- `NetworkWrapper`: Base class providing core networking functionality
- `Client`: Extends NetworkWrapper with specific client-side operations
- `Server`: Extends NetworkWrapper to handle client requests and URL management

### Server Architecture
The server implements several key features:
1. **URL Management**
   - Uses a JSON file to persistently store URL mappings
   - Manages fake/real URL pairs
   - Provides URL statistics tracking
   - Generates unique fake URLs

2. **Request Handling**
   - Processes client commands
   - Manages user authentication
   - Tracks URL access statistics
   - Handles concurrent connections (up to 100 clients)

3. **URL Generation**
   The server generates fake URLs using:
   - Random combinations of tech-related words
   - Common TLDs (com, net, org, etc.)
   - Random path components
   Example: `https://techxyzcom/cloudab/defg`

### Message Format
All messages follow this format:
```
[message_size]~[actual_message]
```
Where:
- `message_size` is the length of the actual message in bytes
- `~` is the delimiter
- `actual_message` is the payload

## Commands and Message Types

### Authentication Commands
1. **Sign Up**
   ```
   SIGN_UP~<username>~<password>~<confirm_password>
   ```

2. **Login**
   ```
   SIGN_IN~<username>~<password>
   ```

### URL Management Commands
1. **Add URL**
   ```
   ADD~<url>
   ```

2. **Remove URL**
   ```
   DEL~<fake_url>
   ```

3. **Get Real URL**
   ```
   GET~<fake_url>
   ```

4. **Request URL Information**
   ```
   REQ~<fake_url>
   ```

### Connection Establishment
1. **Client Hello**
   ```
   HELLO
   ```

## Server Response Types

### Success Responses
1. **Generic Success**
   ```
   ACK
   ```

2. **URL Response**
   ```
   URL~<actual_url>
   ```

3. **Statistics Response**
   ```
   STATS~<pickled_data>~<fake_url>~<real_url>
   ```
   Where pickled_data contains a list of PacketData with fields:
   - IP: string
   - Time: string

### Error Response
```
ERR~<error_code>~<error_message>
```

## Network Implementation Details

### Socket Configuration
- Uses TCP sockets
- Enables address reuse (SO_REUSEADDR)
- Supports both IPv4 and IPv6

### Message Reception
The protocol implements a robust message reception mechanism that:
1. Reads the message size until the delimiter (~) is found
2. Converts size to integer
3. Continues reading chunks of data until the complete message is received
4. Handles disconnections gracefully

### Message Transmission
Messages are sent with the following process:
1. Calculate message length
2. Prepend length and delimiter to message
3. Send complete message through socket

### Error Handling
- Handles client disconnections
- Validates message formats
- Provides detailed error messages
- Includes error codes for different failure scenarios

## Data Types

### PacketData Structure
```python
class PacketData(TypedDict):
    IP: str    # Client IP address
    Time: str  # Timestamp of the request
```

## Connection Lifecycle
1. Client creates socket connection to server
2. Client sends HELLO message
3. Client can then send any supported command
4. Each command receives a corresponding response
5. Connection remains open until explicitly closed
6. Resources are cleaned up on connection termination
7. Server maintains persistent URL mappings in JSON format

## Server Response Codes
The server uses specific error codes:
- `ERR~1`: URL not found (during removal)
- `ERR~2`: URL not found (during lookup)
- `ERR~4`: URL not found (during stats retrieval)
- `ERR~255`: Unknown command

## File Structure
- `urls.json`: Stores URL mappings
- Server tracks URL statistics including:
  - IP addresses of requesters
  - Access timestamps
  - URL mapping details

## Server Configuration
- Default IP: 127.0.0.1
- Configurable port (0 for debug mode)
- Maximum concurrent connections: 100
- URL storage path: Relative to server location
