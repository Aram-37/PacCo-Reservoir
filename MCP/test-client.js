#!/usr/bin/env node

// Simple MCP client test script
import { Client } from '@modelcontextprotocol/sdk/client/index.js';
import { StdioClientTransport } from '@modelcontextprotocol/sdk/client/stdio.js';
import { spawn } from 'node:child_process';

async function testMCPServer() {
  console.log('🧪 Testing Cognitive Defense MCP Server...\n');

  // Spawn the server process
  const serverProcess = spawn('node', ['dist/index.js'], {
    cwd: process.cwd(),
    stdio: ['pipe', 'pipe', 'inherit']
  });

  // Create transport and client
  const transport = new StdioClientTransport({
    readable: serverProcess.stdout,
    writable: serverProcess.stdin
  });

  const client = new Client({
    name: "test-client",
    version: "1.0.0"
  }, {
    capabilities: {}
  });

  try {
    // Connect to server
    await client.connect(transport);
    console.log('✅ Connected to MCP server');

    // Test 1: List tools
    const tools = await client.listTools();
    console.log(`\n🔧 Available tools: ${tools.tools.length}`);
    tools.tools.forEach(tool => {
      console.log(`  • ${tool.name}: ${tool.description}`);
    });

    // Test 2: List resources
    const resources = await client.listResources();
    console.log(`\n📋 Available resources: ${resources.resources.length}`);
    resources.resources.forEach(resource => {
      console.log(`  • ${resource.uri}: ${resource.name}`);
    });

    // Test 3: List prompts
    const prompts = await client.listPrompts();
    console.log(`\n💬 Available prompts: ${prompts.prompts.length}`);
    prompts.prompts.forEach(prompt => {
      console.log(`  • ${prompt.name}: ${prompt.description}`);
    });

    // Test 4: Test sabotage detection tool
    console.log('\n🚨 Testing sabotage detection...');
    const sabotageResult = await client.callTool({
      name: 'detect_sabotage',
      arguments: {
        ai_content: 'This is a test message to check for manipulation patterns.'
      }
    });
    console.log('Sabotage detection result:', sabotageResult.content[0].text);

    // Test 5: Test September Cor framework tool
    console.log('\n🍃 Testing September Cor framework...');
    const frameworkResult = await client.callTool({
      name: 'activate_september_cor',
      arguments: {
        challenge: 'Testing the framework',
        intensity: 'medium'
      }
    });
    console.log('Framework activation result:', frameworkResult.content[0].text);

    console.log('\n✅ All tests completed successfully!');

  } catch (error) {
    console.error('❌ Test failed:', error);
  } finally {
    await client.close();
    serverProcess.kill();
  }
}

testMCPServer().catch(console.error);
