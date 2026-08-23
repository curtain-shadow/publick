const fs = require('fs');
const path = require('path');

function generateTree(dir, prefix = '') {
  const files = fs.readdirSync(dir);
  let result = '';

  files.forEach((file, idx) => {
    // 这里可以添加你希望忽略的文件夹
    if (file === 'node_modules' || file === '.git') return;

    const isLast = idx === files.length - 1;
    const fullPath = path.join(dir, file);
    const stats = fs.statSync(fullPath);

    result += `${prefix}${isLast ? '└── ' : '├── '}${file}\n`;

    if (stats.isDirectory()) {
      result += generateTree(fullPath, `${prefix}${isLast ? '    ' : '│   '}`);
    }
  });

  return result;
}

// 从当前目录开始生成，并输出到控制台
console.log(generateTree(process.argv[2] || '.'));