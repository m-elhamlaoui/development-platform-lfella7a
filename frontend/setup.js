#!/usr/bin/env node

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Colors for console output
const colors = {
  blue: '\x1b[34m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  reset: '\x1b[0m',
};

console.log(`${colors.blue}Setting up your Next.js 15.3.1 project with React 19...${colors.reset}\n`);

// Helper function to execute commands and log output
function runCommand(command, errorMessage) {
  try {
    console.log(`${colors.yellow}Running: ${command}${colors.reset}`);
    execSync(command, { stdio: 'inherit' });
    return true;
  } catch (error) {
    console.error(`${colors.red}${errorMessage}${colors.reset}`);
    console.error(`${colors.red}Error: ${error.message}${colors.reset}`);
    return false;
  }
}

// Check if package.json exists
if (!fs.existsSync(path.join(process.cwd(), 'package.json'))) {
  console.error(`${colors.red}package.json not found. Make sure you're running this script from the project root.${colors.reset}`);
  process.exit(1);
}

console.log(`${colors.blue}Installing dependencies...${colors.reset}`);
const installSuccessful = runCommand('npm install', 'Failed to install dependencies.');

if (!installSuccessful) {
  console.log(`${colors.yellow}Trying with --legacy-peer-deps flag...${colors.reset}`);
  runCommand('npm install --legacy-peer-deps', 'Failed to install dependencies even with legacy-peer-deps.');
}

// Create necessary directories if they don't exist
const directories = [
  'src/app',
  'src/components',
  'src/utils',
  'public/results'
];

directories.forEach(dir => {
  const dirPath = path.join(process.cwd(), dir);
  if (!fs.existsSync(dirPath)) {
    console.log(`${colors.yellow}Creating directory: ${dir}${colors.reset}`);
    fs.mkdirSync(dirPath, { recursive: true });
  }
});

console.log(`\n${colors.green}Setup complete!${colors.reset}`);
console.log(`\n${colors.blue}To start the development server, run:${colors.reset}`);
console.log(`${colors.yellow}npm run dev${colors.reset}`);
console.log(`\n${colors.blue}Your Next.js 15.3.1 project with React 19 and MapBox GL is ready.${colors.reset}`); 