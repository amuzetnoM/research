const fs = require('fs');
const path = require('path');
const util = require('util');

const readdir = util.promisify(fs.readdir);
const stat = util.promisify(fs.stat);

// Configuration
const ignoreDirs = ['.git', 'node_modules', '.github'];
const ignoreFiles = ['.gitignore', '.DS_Store'];

async function scanDirectory(dir, relativePath = '') {
  const entries = await readdir(dir);
  let result = [];

  for (const entry of entries) {
    if (ignoreDirs.includes(entry) || ignoreFiles.includes(entry)) continue;
    
    const fullPath = path.join(dir, entry);
    const entryRelativePath = path.join(relativePath, entry);
    const stats = await stat(fullPath);
    
    if (stats.isDirectory()) {
      const children = await scanDirectory(fullPath, entryRelativePath);
      result.push({
        type: 'directory',
        name: entry,
        path: entryRelativePath,
        children
      });
    } else {
      result.push({
        type: 'file',
        name: entry,
        path: entryRelativePath,
        size: stats.size
      });
    }
  }
  
  return result;
}

async function generateIndex(repoPath) {
  try {
    console.log(`Scanning repository at: ${repoPath}`);
    const structure = await scanDirectory(repoPath);
    
    // Write JSON structure
    fs.writeFileSync(
      path.join(repoPath, 'workspace-index.json'), 
      JSON.stringify(structure, null, 2)
    );
    
    // Generate markdown
    let markdown = `# Repository Workspace Index\n\n`;
    markdown += `Generated on: ${new Date().toISOString()}\n\n`;
    markdown += `## Repository Structure\n\n`;
    
    function addToMarkdown(items, level = 0) {
      for (const item of items) {
        const indent = '  '.repeat(level);
        if (item.type === 'directory') {
          markdown += `${indent}- 📁 **${item.name}/**\n`;
          addToMarkdown(item.children, level + 1);
        } else {
          markdown += `${indent}- 📄 [${item.name}](${item.path.replace(/\\/g, '/')})\n`;
        }
      }
    }
    
    addToMarkdown(structure);
    
    fs.writeFileSync(
      path.join(repoPath, 'WORKSPACE.md'), 
      markdown
    );
    
    console.log('Workspace index created successfully!');
    console.log('Check WORKSPACE.md for a human-readable index.');
  } catch (error) {
    console.error('Error generating index:', error);
  }
}

// Get the repository path from command line arguments or use current directory
const repoPath = process.argv[2] || process.cwd();
generateIndex(repoPath);
