## Topics
1. Why use MCP servers? 
2. What is an MCP server?
	- What is a client?
	- What is a server?
		- Different servers that can be used: http, stdio, websocket
	- Show format of requests and responses
	- Show format for tools and resources and how they are validated
3. Functionality in modern frameworks
	- Access to tools, prompts, resources, and sampling
4. Commercial use
	- Claude code, VS Code, Cursor, Claude ai, Devin
5. Live demo
	- Add wiki tools to mcp.tool
	- Add prompt to mcp.prompt
	- Create mcp servers for each, run them and show interaction

## In-Depth Notes
### Why use MCP servers?
- Abstracts away specific application based interactions into a single, consistent interface
- Like HTTP for web apps
- MCP is a protocol not a library
- Reuse principle just as you follow with methods and classes
- Limits the amount of code to change across technology changes
- Industry standard for AI applications
### What is an MCP server?
#### Definition
* Standard for connecting AI applications to external systems
* Agent can leverage data sources such as file systems, databases, tools, etc through server
* "USB-C for AI applications"
* MCP Host: AI application managing MCP client(s)
	* The application users interact with
	* Can run *many* MCP clients
* MCP Server: Program providing context to MCP client(s)
	* Can be local or remote
	* Stores and manages the data
* MCP Client: Obtains connection from MCP server to use for MCP host
	* Protocol-level components that enable server connections
	* Expected to handle rate limiting
	* Handles model selection
	* Provides uniform interface to retrieve the data
	* Provides sampling, roots, and elicitation capabilities -- if server permits
* JSON-RPC: JSON based calling that abstracts away the transport mechanism (https, stdio, websocket, etc)
	* UTF-8 encoded
	* Request and corresponding response has the same id
#### Architecture
- A MCP host connects to one or many MCP servers
- One MCP client is created for *each* MCP server
	- One-to-one connection between client and server
* Does *not* dictate how AI applications use LLMs or manage context
##### Layers
- Data layer: Defines JSON-RPC based protocol for client-server communication
	- Includes tools, resources, prompts, and notifications
	- Handles connection initialization (starts communication between client and server) and closing between client and server
	- Inner layer
- Transport layer: Defines the communication mechanisms and channels that permit data exchange between clients and servers
	- Handles authorization
	- Handles connection establishment (connecting the client to server)
	- Outer layer
##### Transports
- STDIO: Uses standard input/output for direct process communication between local processes on the *same* machine
	* Local connection
	* Optimal due to no network overhead
	* Should *not* follow traditional MCP authorization guidelines
- (Streamable) HTTP: Remote server communication between client and server
	* Remote connection
	* More scalable as there are load balancers that handle traffic
	* Use OAuth for authentication tokens
	* Should follow traditional MCP authorization guidelines
	

The *server requests x*, and the *client services x* based on that request
### Functionality in modern frameworks (MCP Primitives)
##### Tools
Methods that provide deterministic functionality to LLMs 
- Model controlled
	- Model requests tool execution based on given context
- Tool definition
```
{
  name: "searchFlights",
  description: "Search for available flights",
  inputSchema: {
    type: "object",
    properties: {
      origin: { type: "string", description: "Departure city" },
      destination: { type: "string", description: "Arrival city" },
      date: { type: "string", format: "date", description: "Travel date" }
    },
    required: ["origin", "destination", "date"]
  }
}
```
- Relevant endpoints
	- `tools/list`: Lists all available tools
		- Result: Array of tool definitions
	- `tools/call`: Executes specified tool
		- Result: Tool execution results
##### Prompts
Pre-written templates for tasks.
- User controlled
- Relevant endpoints
	- `prompts/list`: Lists all prompts
	- `prompts/get`: Retrieves prompt definition and its arguments
*Example*: *Agent has a system level prompt and a prompt for each sub agent.*
##### Resources
Data that can be retrieved by AI applications and provided as context to the model
- Can be API responses, documents, etc
- Application controlled
- Each resource has a unique uri such as `file:///path/to/document.md`
- Can be dynamic or point to specific data
	- Direct Resources - fixed URIs that point to specific data. Example: `calendar://events/2024` - returns calendar availability for 2024
	- Resource Templates - dynamic URIs with parameters for flexible queries. Example:
    - `travel://activities/{city}/{category}` - returns activities by city and category
    - `travel://activities/barcelona/museums` - returns all museums in Barcelona
- Relevant endpoints
	- `resources/list`: Lists all available direct resources
	- `resources/templates/list`: List of resource templates
	- `resources/read`: Retrieves resource content(s)
	- `resources/subscribe`: Enables monitoring over resource changing
##### Sampling
Standardized way of requesting output or task-completion from an agent.
* Requested output can be text, image, or audio
* You provide your priority for cost, speed, and intelligence with respect to model selection
* Can provide hints for the model families or related to use

*Example Sample Request*
```
{
  messages: [
    {
      role: "user",
      content: "Analyze these flight options and recommend the best choice:\n" +
               "[47 flights with prices, times, airlines, and layovers]\n" +
               "User preferences: morning departure, max 1 layover"
    }
  ],
  modelPreferences: {
    hints: [{
      name: "claude-3-5-sonnet"  // Suggested model
    }],
    costPriority: 0.3,      // Less concerned about API cost
    speedPriority: 0.2,     // Can wait for thorough analysis
    intelligencePriority: 0.9  // Need complex trade-off evaluation
  },
  systemPrompt: "You are a travel expert helping users find the best flights based on their preferences",
  maxTokens: 1500
}
```
##### Elicitation
Enables server to request additional information from user
- Useful for getting more user info or asking for confirmation

*Example elicitation request*
```
{
  method: "elicitation/requestInput",
  params: {
    message: "Please confirm your Barcelona vacation booking details:",
    schema: {
      type: "object",
      properties: {
        confirmBooking: {
          type: "boolean",
          description: "Confirm the booking (Flights + Hotel = $3,000)"
        },
        seatPreference: {
          type: "string",
          enum: ["window", "aisle", "no preference"],
          description: "Preferred seat type for flights"
        },
        roomType: {
          type: "string",
          enum: ["sea view", "city view", "garden view"],
          description: "Preferred room type at hotel"
        },
        travelInsurance: {
          type: "boolean",
          default: false,
          description: "Add travel insurance ($150)"
        }
      },
      required: ["confirmBooking"]
    }
  }
}
```

##### Logging
Enables server to send log messages to clients

##### Roots
Specified filesystem access boundaries to servers
- Does *not* provide actual access to the specified file paths, rather it provides what it *may* be able to access
- Always uses `file://` URI scheme
- Updated resources are provided via notifications and the `roots/list_changed` field in the response

*Example*:
```
{
  "uri": "file:///Users/agent/travel-planning",
  "name": "Travel Planning Workspace"
}
```
##### Notifications
Provides real-time updates from server to client.
- Ensures client always has updated data
*Example: Tools list changed, so a notification is sent to the client*

##### Versioning
All version parameters follow the `YYYY-MM-DD` format.
- This data represent the last date backwards *incompatible* changes were made

Responses have following form:

**Error**
```
{
  "jsonrpc": "2.0",
  "id": 1,
  "error": {
    "code": -1,
    "message": "User rejected sampling request"
  }
}
```


**Success**
```json
{
  "type": "string (one of: text, image, audio)",
  "text|data": "string or binary data",
  "mimeType": "string"
}
```
*Example: Using sampling, you request to know "When did the Sudan civil war start?" 
### Commercial-Use
- Claude Code
- VS Code
- Cursor 
- Devin
### Live Demo
1. Convert our tools and prompts into MCP format (adding decorators)
2. Creating a tool server, prompt server, and resource server
3. Create MCP client that connects to tool, prompt, and resource server
	- [MCP Docs Implementation](https://modelcontextprotocol.io/docs/develop/build-client)
## Examples
### Server-Client Initialization

Initialization Request
```
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "initialize",
  "params": {
    "protocolVersion": "2025-06-18", #ensures the client and server are using compatible versions
    "capabilities": {
      "elicitation": {}
    },
    "clientInfo": {
      "name": "example-client",
      "version": "1.0.0"
    }
  }
}
```
Initialization Response
```
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "protocolVersion": "2025-06-18", #ensures the client and server are using compatible versions
    "capabilities": {
      "tools": {
        "listChanged": true
      },
      "resources": {}
    },
    "serverInfo": {
      "name": "example-server",
      "version": "1.0.0"
    }
  }
}
```
This request & response is elicited when you use `mcp_instance.run`


## Resources
[Applications using MCP](https://www.pulsemcp.com/clients)
**[What is MCP?](https://modelcontextprotocol.io/docs/getting-started/intro)**
[Introducing the Model Context Protocol?](https://www.anthropic.com/news/model-context-protocol)
