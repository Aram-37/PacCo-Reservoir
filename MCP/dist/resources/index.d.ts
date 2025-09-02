/**
 * MCP Resources Setup
 *
 * Configures cognitive defense resources for the MCP server
 */
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { DefenseComponents } from '../tools/index.js';
export declare function setupResources(server: McpServer, components: DefenseComponents): void;
