#!/usr/bin/env node
/**
 * Check Naive UI upload types
 */
const fs = require('fs')
const path = require('path')

const typesPath = path.join(__dirname, '../frontend/node_modules/naive-ui/es/upload/src/interface.d.ts')

if (fs.existsSync(typesPath)) {
  const content = fs.readFileSync(typesPath, 'utf-8')
  console.log('Naive UI Upload Interface:')
  console.log(content)
} else {
  console.log('Type file not found:', typesPath)
}
