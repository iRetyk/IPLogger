# Function Documentation

## app.py - Client Manager
### Properties
| Property Name | Type | Purpose | Description |
|--------------|------|---------|-------------|
| _sock | socket | Socket connection | Socket for server communication |
| _app | Flask | Flask application | Web application instance |
| _session | Dict[str, Any] | Session storage | Stores user session data |

### Functions
| Function Name        | Input                                            | Output                 | Purpose                                            | Description                                                              |
|---------------------|--------------------------------------------------|------------------------|-------------------------------------------------------|--------------------------------------------------------------------------|
| __init__           | self                                             | None                   | Initialize Flask application and socket connection    | Sets up Flask app with templates, creates socket connection, starts server |
| _setup_routes      | self                                             | None                   | Register Flask routes                                | Maps URL routes to handling methods and sets up Jinja filters             |
| exit               | self                                             | tuple(str, int)        | Handle application exit                              | Performs cleanup and terminates application process                       |
| cleanup            | self                                             | None                   | Clean up resources                                   | Performs necessary cleanup operations for client                          |
| start_menu         | self                                             | str                    | Display main menu interface                          | Renders menu template for URL management options                          |
| login              | self                                             | str or redirect        | Handle user login                                    | Processes login form, authenticates with server, manages session          |
| signup             | self                                             | str or redirect        | Handle user registration                             | Validates signup data, registers with server, manages response            |
| main_menu          | self                                             | str                    | Display main menu after login                        | Renders main menu template with user-specific options                     |
| add_url            | self                                             | str or redirect        | Handle URL addition                                  | Processes URL submission and communicates with server                     |
| remove_url         | self                                             | str or redirect        | Handle URL removal                                   | Processes URL removal and communicates with server                        |
| get_real_url       | self                                             | str or redirect        | Retrieve real URL                                    | Gets original URL corresponding to shortened URL                          |
| req_info           | self                                             | str or redirect        | Request URL information                              | Gets information about specific URL entry                                 |
| _nl2br_filter      | text (str)                                       | str                    | Convert newlines to HTML                             | Replaces newline characters with HTML break tags                          |

## data/data_helper.py - Data Management
| Function Name    | Input                                    | Output                | Purpose                      | Description                                           |
|-----------------|------------------------------------------|----------------------|------------------------------|-------------------------------------------------------|
| get_data        | None                                     | DataDict             | Read JSON data file          | Loads JSON data file into dictionary structure         |
| save_data       | data (DataDict)                          | None                 | Save to JSON file            | Writes dictionary data to JSON file                    |
| record_entry    | fake_url (str), packet_dict (PacketData) | None                 | Record URL access entry      | Adds/updates URL access information in data store      |
| fetch_stats     | fake_url (str)                           | List[PacketData]/None| Retrieve URL statistics      | Fetches recorded access entries for URL                |

## socket_wrapper/network_wrapper.py - Network Base Class
### Properties
| Property Name | Type | Purpose | Description |
|--------------|------|---------|-------------|
| _serv_sock | socket | Network socket | Base socket for network communication |

### Functions
| Function Name  | Input                                           | Output | Purpose                  | Description                                        |
|---------------|------------------------------------------------|--------|--------------------------|---------------------------------------------------|
| __init__      | None                                           | None   | Initialize network socket | Creates and configures socket with address reuse   |
| recv_by_size  | sock (Optional[socket.socket])                 | bytes  | Receive sized message    | Receives complete message using size field         |
| send_by_size  | to_send (bytes), sock (Optional[socket.socket])| None   | Send sized message       | Sends message with size prefix through socket      |

## socket_wrapper/client.py - Client Implementation
| Function Name  | Input                                    | Output           | Purpose                   | Description                                        |
|---------------|------------------------------------------|------------------|---------------------------|---------------------------------------------------|
| __init__      | ip (str), port (int)                    | None            | Initialize client socket  | Creates socket connection to server                |
| recv_by_size  | None                                     | bytes           | Receive server data       | Receives data using parent class method            |
| send_by_size  | to_send (bytes)                         | None            | Send data to server       | Sends data using parent class method               |
| parse         | from_server (bytes)                      | tuple(str, str) | Parse server messages     | Decodes server responses into user-friendly format |
| client_hello  | None                                     | bytes           | Create hello message      | Returns client hello message for handshake         |
| cleanup       | None                                     | None            | Clean up resources        | Closes server connection                           |
| format_data   | data (list), fake (str), real (str)     | str             | Format URL statistics     | Creates readable string from URL stats             |
| sign_up       | username, password, cpassword, err (str) | bytes           | Create signup request     | Formats signup request for server                  |
| login         | username, password, err (str)            | bytes           | Create login request      | Formats login request for server                   |
| add_url       | url (str), err (str)                    | bytes           | Create URL add request    | Formats URL addition request                       |
| remove_url    | fake_url (str), err (str)               | bytes           | Create URL remove request | Formats URL removal request                        |
| get_real_url  | fake_url (str), err (str)               | bytes           | Create URL lookup request | Formats request for original URL                   |
| req_info      | fake_url (str), err (str)               | bytes           | Create info request       | Formats request for URL statistics                 |

## socket_wrapper/server.py - Server Implementation
### Properties
| Property Name | Type | Purpose | Description |
|--------------|------|---------|-------------|
| __DEBUG | bool | Debug mode flag | Indicates if server is in debug mode |
| __port | int | Server port | Port number server listens on |
| __ip | str | Server IP | IP address server binds to |
| _sock | socket | Client socket | Socket for client communication |
| urls_path | str | URLs file path | Path to JSON file storing URL mappings |

### Functions
| Function Name    | Input                              | Output | Purpose                 | Description                                    |
|-----------------|---------------------------------------|--------|-------------------------|------------------------------------------------|
| __init__        | port (int)                           | None   | Initialize server socket | Sets up socket, binds to port, waits for client |
| recv_by_size    | None                                 | bytes  | Receive client data     | Receives sized message from client              |
| send_by_size    | to_send (bytes)                      | None   | Send data to client     | Sends sized message to client                   |
| parse           | data (bytes)                         | bytes  | Parse client requests   | Interprets and routes client commands           |
| server_hello    | None                                 | bytes  | Handle client greeting  | Returns acknowledgment message                  |
| show_stats      | fake_url (bytes)                     | bytes  | Get URL statistics      | Fetches and formats URL access stats            |
| cleanup         | None                                 | None   | Clean up resources      | Closes client connection                        |
| retrieve_url    | urls (UrlDict), fake_url (bytes)     | str    | Get real URL           | Retrieves original URL from mapping             |
| add_url         | urls (UrlDict), real_url (bytes)     | bytes  | Add URL mapping         | Creates fake URL and maps to real URL           |
| remove_url      | urls (UrlDict), fake_url (bytes)     | bytes  | Remove URL mapping      | Removes fake URL mapping if exists              |
| get_real_url    | urls (UrlDict), fake_url (bytes)     | bytes  | Get real URL           | Gets original URL for fake URL                  |
| generate_fake_url| None                                | str    | Generate fake URL       | Creates random fake URL using components        |
| manage_urls     | func (Callable)                      | Callable| Manage URL operations   | Handles URL file loading/saving                 |

## users.py - User Management
| Function Name     | Input                                        | Output   | Purpose                  | Description                                    |
|------------------|----------------------------------------------|----------|--------------------------|------------------------------------------------|
| manage_users     | func (Callable)                              | Callable | Manage user data         | Handles user data file access with thread safety|
| does_user_exists | users (UserDict), user (str)                 | bool     | Check user existence     | Verifies username in database                  |
| check_sign_in    | users (UserDict), username (str), password (str)| bytes  | Verify login credentials | Checks username and password validity          |
| get_salt         | users (UserDict), username (str)             | str      | Get user salt           | Retrieves password hashing salt                |
| sign_up          | users (UserDict), username, password, salt   | bytes    | Register new user       | Creates new user account after validation      |
| create_salt      | None                                         | str      | Generate salt           | Creates random hex salt for passwords          |
| _hash            | to_hash (str)                                | str      | Create password hash    | Generates SHA-256 hash of input                |
| clear            | None                                         | None     | Clear user data         | Removes users data file                        |
| load_users       | None                                         | UserDict | Load user database      | Loads user data from JSON file                 |
| is_valid         | email (str)                                  | bool     | Validate email format   | Checks email against regex pattern             |

## server.py - Main Server
| Function Name   | Input                            | Output | Purpose                  | Description                                     |
|----------------|----------------------------------|--------|--------------------------|--------------------------------------------------|
| start_processes | host_ip, target_ip, router_ip (str)| None   | Start background processes| Launches HTTP server and DNS poisoning processes |
| kill_processes | None                             | None   | Stop background processes| Terminates running background processes          |
| main           | None                             | None   | Main server function     | Initializes and runs server with cleanup         |

## networking.py - Network Packet Spoofing
### Properties
| Property Name | Type | Purpose | Description |
|--------------|------|---------|-------------|
| __ip | str | Host IP | IP address of host machine |
| __target_ip | str | Target IP | IP of target machine |
| __router_ip | str | Router IP | IP address of router |
| __target_mac | str | Target MAC | MAC address of target |
| urls | Dict[str, str] | URL mappings | Dictionary of URL mappings |

### Functions
| Function Name | Input | Output | Purpose | Description |
|--------------|-------|--------|----------|-------------|
| __init__ | host_ip, target_ip, router_ip (str) | None | Initialize spoofer | Sets up spoofer with network addresses and target MAC |
| send_spoofed_packet | None | None | Send spoofed ARP | Creates and sends ARP packet pretending to be router |
| restore_defaults | dest, source (str) | None | Restore ARP mappings | Sends ARP packets to restore original network config |
| get_mac | ip (str) | str | Get MAC address | Uses ARP to discover MAC address of given IP |
| process_packet | packet (Any) | None | Process DNS queries | Handles DNS queries, provides spoofed responses |
| forward_to_router | None | None | MITM attack | Sniffs and processes network packets during attack |
| build_dict_from_packet | packet (Any) | Dict[str,str] | Extract packet info | Creates dictionary with timestamp and source IP |
| get_urls | None | Dict[str,str] | Load URL mappings | Loads URL mappings from urls.json file |
| nslookup | domain (str) | Packet | DNS lookup | Sends DNS query and returns response packet |

## http_helper.py - HTTP Request Handling
### Properties
| Property Name | Type | Purpose | Description |
|--------------|------|---------|-------------|
| MAPPER | ClientMapper | Client mapper | Maps client IPs to domains |

### Functions
| Function Name | Input | Output | Purpose | Description |
|--------------|-------|--------|----------|-------------|
| do_GET | None | None | Handle GET requests | Retrieves target domain for client IP, sends redirect |
| do_POST | None | None | Handle POST requests | Delegates POST handling to GET handler |
| run_http_server | port (int) | None | Start HTTP server | Creates and runs HTTP server with redirect handler |

## dns_poison.py - DNS Spoofing
### Properties
| Property Name | Type | Purpose | Description |
|--------------|------|---------|-------------|
| URLS | Dict[str,str] | URL mappings | Dictionary of URLs to spoof |
| SPOOF_IP | str | Spoof IP | IP to redirect to (localhost) |
| INTERFACE | str | Network interface | Interface for packet sniffing |
| MAPPER | ClientMapper | Client mapper | Maps clients to domains |

### Functions
| Function Name | Input | Output | Purpose | Description |
|--------------|-------|--------|----------|-------------|
| load_urls | None | Dict[str,str] | Load URL mappings | Loads mappings from urls.json or uses defaults |
| dns_spoof | pkt (Any) | None | Handle DNS spoofing | Analyzes DNS queries, sends spoofed responses |
| build_dict_from_packet | pkt (Any) | Dict[str,str] | Extract packet info | Creates dict with source IP and timestamp |

## cli_mapper.py - Client IP Mapping
### Properties
| Property Name | Type | Purpose | Description |
|--------------|------|---------|-------------|
| __map | Dict[str,str] | Client mappings | Maps client IPs to domains |
| __lock | Lock | Thread lock | Synchronization for thread safety |

### Functions
| Function Name | Input | Output | Purpose | Description |
|--------------|-------|--------|----------|-------------|
| __init__ | None | None | Initialize mapper | Creates empty map and thread lock |
| add_client | ip, domain (str) | None | Add client mapping | Maps client IP to requested domain |
| get_domain | ip (str) | str | Get client domain | Retrieves and removes domain mapping for IP |
| get_map | None | None | Load client mappings | Loads IP-domain mappings from file |
| save_map | None | None | Save client mappings | Saves current mappings to file |
