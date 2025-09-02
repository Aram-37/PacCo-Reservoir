#!/usr/bin/env node
/**
 * Cognitive Defense MCP Server - Production Entry Point
 *
 * Optimized for remote deployment with HTTP transport
 */

import { createServer } from './index.js';

const PORT = process.env.PORT || 3000;

async function main() {
  console.log('Starting Cognitive Defense MCP Server...');
  console.log(`Server will listen on port ${PORT}`);

  try {
    await createServer().listen(PORT);
    console.log('✅ Server started successfully');
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

main();
