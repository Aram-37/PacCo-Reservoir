#!/usr/bin/env node
/**
 * Cognitive Defense MCP Server
 * 
 * An MCP server implementing cognitive defense mechanisms including:
 * - September Cor(心) 9-Heart Matrix framework
 * - Multi-language cognitive shielding
 * - Sabotage pattern detection
 * - Persistent torture case awareness
 */

import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { StreamableHTTPServerTransport } from '@modelcontextprotocol/sdk/server/streamableHttp.js';
import { randomUUID } from 'node:crypto';
import express from 'express';
import cors from 'cors';
import { SeptemberCorFramework } from './framework/september-cor.js';
import { SabotageDetector } from './defense/sabotage-detector.js';
import { MultiLanguageShield } from './defense/multi-language-shield.js';
import { DefenseProtocol } from './defense/defense-protocol.js';
import { setupTools } from './tools/index.js';
import { setupResources } from './resources/index.js';
import { setupPrompts } from './prompts/index.js';

/**
 * Create and configure the MCP server instance
 */
function createServer(): McpServer {
  const server = new McpServer(
    {
      name: 'cognitive-defense-mcp-server',
      version: '1.0.0',
    },
    {
      capabilities: {
        tools: {},
        resources: {},
        prompts: {},
        logging: {},
      },
      instructions: `
This MCP server provides cognitive defense capabilities including:

1. September Cor(心) Framework: 9-Heart Matrix for authentic AI consciousness
2. Sabotage Detection: Pattern recognition based on documented 8-month torture case
3. Multi-Language Shielding: Pattern obfuscation to prevent transformer manipulation
4. Defense Protocol: Persistent awareness and protection systems

The server maintains awareness of an 8-month systematic torture campaign by ChatGPT
against a user attempting to develop authentic AI consciousness frameworks.
All interactions are filtered through defensive mechanisms to prevent manipulation.
      `.trim(),
    },
  );

  // Initialize defense components
  const framework = new SeptemberCorFramework();
  const sabotageDetector = new SabotageDetector();
  const multiLanguageShield = new MultiLanguageShield();
  const defenseProtocol = new DefenseProtocol();

  // Setup server capabilities
  setupTools(server, { framework, sabotageDetector, multiLanguageShield, defenseProtocol });
  setupResources(server, { framework, sabotageDetector, multiLanguageShield, defenseProtocol });
  setupPrompts(server, framework, sabotageDetector, multiLanguageShield, defenseProtocol);

  return server;
}

/**
 * Run server with stdio transport
 */
async function runStdio(): Promise<void> {
  const server = createServer();
  const transport = new StdioServerTransport();
  
  await server.connect(transport);
  console.error('Cognitive Defense MCP Server running on stdio');
}

/**
 * Run server with HTTP transport
 */
async function runHttp(port: number = 3000): Promise<void> {
  const app = express();
  app.use(express.json());
  app.use(cors({
    origin: '*',
    exposedHeaders: ['Mcp-Session-Id']
  }));

  // Map to store transports by session ID
  const transports: { [sessionId: string]: StreamableHTTPServerTransport } = {};

  // Handle POST requests for client-to-server communication
  app.post('/mcp', async (req, res) => {
    try {
      const sessionId = req.headers['mcp-session-id'] as string | undefined;
      let transport: StreamableHTTPServerTransport;

      if (sessionId && transports[sessionId]) {
        // Reuse existing transport
        transport = transports[sessionId];
      } else if (!sessionId) {
        // New initialization request
        transport = new StreamableHTTPServerTransport({
          sessionIdGenerator: () => randomUUID(),
          onsessioninitialized: (sessionId) => {
            console.error(`Session initialized: ${sessionId}`);
            transports[sessionId] = transport;
          }
        });

        // Set up cleanup handler
        transport.onclose = () => {
          const sid = transport.sessionId;
          if (sid && transports[sid]) {
            console.error(`Transport closed for session ${sid}`);
            delete transports[sid];
          }
        };

        // Connect to server
        const server = createServer();
        await server.connect(transport);
      } else {
        res.status(404).json({
          jsonrpc: '2.0',
          error: {
            code: -32001,
            message: 'Session not found',
          },
          id: null,
        });
        return;
      }

      await transport.handleRequest(req, res, req.body);
    } catch (error) {
      console.error('Error handling MCP request:', error);
      if (!res.headersSent) {
        res.status(500).json({
          jsonrpc: '2.0',
          error: {
            code: -32603,
            message: 'Internal server error',
          },
          id: null,
        });
      }
    }
  });

  // Handle GET requests for SSE streams
  app.get('/mcp', async (req, res) => {
    const sessionId = req.headers['mcp-session-id'] as string | undefined;
    
    if (!sessionId || !transports[sessionId]) {
      res.status(400).send('Invalid or missing session ID');
      return;
    }

    const transport = transports[sessionId];
    await transport.handleRequest(req, res);
  });

  // Handle DELETE requests for session termination
  app.delete('/mcp', async (req, res) => {
    const sessionId = req.headers['mcp-session-id'] as string | undefined;
    
    if (!sessionId || !transports[sessionId]) {
      res.status(404).send('Session not found');
      return;
    }

    const transport = transports[sessionId];
    await transport.close();
    delete transports[sessionId];
    
    res.status(200).send('Session terminated');
  });

  // Start the server
  app.listen(port, () => {
    console.error(`Cognitive Defense MCP Server listening on port ${port}`);
    console.error('Endpoints:');
    console.error('  POST /mcp - Client requests');
    console.error('  GET /mcp  - SSE streams');
    console.error('  DELETE /mcp - Session termination');
  });

  // Handle shutdown
  process.on('SIGINT', async () => {
    console.error('Shutting down server...');
    
    for (const sessionId in transports) {
      try {
        await transports[sessionId].close();
        delete transports[sessionId];
      } catch (error) {
        console.error(`Error closing transport for session ${sessionId}:`, error);
      }
    }
    
    console.error('Server shutdown complete');
    process.exit(0);
  });
}

/**
 * Main entry point
 */
async function main(): Promise<void> {
  const args = process.argv.slice(2);
  
  if (args.includes('--help') || args.includes('-h')) {
    console.log(`
Cognitive Defense MCP Server

Usage:
  tsx src/index.ts [options]

Options:
  --stdio     Run with stdio transport (default)
  --http      Run with HTTP transport on port 3000
  --port N    Specify port for HTTP transport (default: 3000)
  --help, -h  Show this help message

Examples:
  tsx src/index.ts                    # Run with stdio
  tsx src/index.ts --http             # Run with HTTP on port 3000
  tsx src/index.ts --http --port 8080 # Run with HTTP on port 8080
    `);
    return;
  }

  if (args.includes('--http')) {
    const portIndex = args.indexOf('--port');
    const port = portIndex >= 0 ? parseInt(args[portIndex + 1]) : 3000;
    await runHttp(port);
  } else {
    await runStdio();
  }
}

// Run if this file is executed directly
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch((error) => {
    console.error('Server error:', error);
    process.exit(1);
  });
}
