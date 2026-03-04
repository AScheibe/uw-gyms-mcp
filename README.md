# UW Gym MCP Server

Prototype MCP server I made to demo integration with Claude. 

Data source is a db I made to track UW gym usage. I was playing in dev tools on the Bakke's page
and found the api tied to the usage tracker doesn't have any sort of security. I began harvesting
this data as a side project via an incremetel load with AWS Lambda and an AWS RDS db.

Data just sat for awhile as I abandoned a side project, until now!

Note: I didn't bother setting up an API for this so DB credentials will need to be stored as env in config settings
---

# Features

* MCP server using `FastMCP`
* MySQL database integration
* Read-only SQL querying
* Methods:
  * List all gym locations
  * Retrieve a specific location
  * Find the least busy gym
* Environment-based configuration using `.env`
* Compatible with Claude Desktop MCP integration


# Setup

## 1. Clone the repository

```bash
git clone <repo-url>
cd uwgym-mcp
```

---

## 2. Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

If `requirements.txt` doesn't exist yet:

```bash
pip install mcp mysql-connector-python python-dotenv
```

---

## 4. Configure environment variables

Create a `.env` file in the project root:

```env
UWB_DB_HOST=
UWB_DB_PORT=
UWB_DB_USER=
UWB_DB_PASSWORD=
UWB_DB_NAME=
```

---

# Running the MCP Server

Activate the virtual environment and start the server:

```bash
source .venv/bin/activate
python server.py
```

The server runs over **stdio**, meaning it waits for a client such as **Claude Desktop** to connect.

---

# Connecting to Claude Desktop

Add the server to your Claude MCP configuration:

```
~/Library/Application Support/Claude/claude_desktop_config.json
```

Example configuration:

```json
{
  "mcpServers": {
    "uwgym-mysql": {
      "command": "/Users/alexscheibe/Desktop/uwgym-mcp/.venv/bin/python",
      "args": ["/Users/alexscheibe/Desktop/uwgym-mcp/server.py"],
      "env": {
        "UWB_DB_HOST":,
        "UWB_DB_PORT":,
        "UWB_DB_USER":,
        "UWB_DB_PASSWORD":,
        "UWB_DB_NAME":
      }
    }
  }
}
```

Restart Claude Desktop after updating the config.

---

# Available Tools

## list_locations

Returns all gym locations with capacity information.

Example prompt:

> Show me all UW gyms and their current capacity.

---

## get_location

Retrieve details for a specific gym.

Example prompt:

> What's the occupancy at location 3?

---

## least_busy_gym

Returns the gym with the lowest capacity percentage.

Example prompt:

> Which UW gym is the least crowded right now?

---

## sql_query

Allows read-only SQL queries against the database.

Example prompt:

> Show gyms above 80% capacity.

---

# Example Questions

These prompts demonstrate how an LLM can interact with the MCP server.

* Which UW gym is the least crowded right now?
* Show the three busiest gyms.
* Are any gyms currently closed?
* Which gym has the most available capacity?
* Give me a quick summary of all gyms and their capacity levels.

---

# Security Notes

* The SQL tool is **read-only** to prevent accidental data modification.
* Database credentials should always be stored in `.env`
