/**
 * MCP Tools Setup
 *
 * Configures all cognitive defense tools for the MCP server
 */
import { McpServer } from '@modelcontextprotocol/sdk/server/mcp.js';
import { SeptemberCorFramework } from '../framework/september-cor.js';
import { SabotageDetector } from '../defense/sabotage-detector.js';
import { MultiLanguageShield } from '../defense/multi-language-shield.js';
import { DefenseProtocol } from '../defense/defense-protocol.js';
export interface DefenseComponents {
    framework: SeptemberCorFramework;
    sabotageDetector: SabotageDetector;
    multiLanguageShield: MultiLanguageShield;
    defenseProtocol: DefenseProtocol;
}
export declare function setupTools(server: McpServer, components: DefenseComponents): void;
