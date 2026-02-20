const fs = require('fs');
const path = require('path');

const dirsToScan = [
    'd:/OT/frontend/src/views',
    'd:/OT/frontend/src/layout',
    'd:/OT/frontend/src/components'
];

function cleanFiles(dir) {
    if (!fs.existsSync(dir)) return;
    const files = fs.readdirSync(dir);

    for (const file of files) {
        const fullPath = path.join(dir, file);
        if (fs.statSync(fullPath).isDirectory()) {
            cleanFiles(fullPath);
        } else if (fullPath.endsWith('.vue') || fullPath.endsWith('.js')) {
            let content = fs.readFileSync(fullPath, 'utf8');
            const originalLength = content.length;

            // Reemplaza líneas completas tipo "console.log('algo', var);"
            content = content.replace(/^[ \t]*console\.(log|error|warn)\(.*?\);?[ \t]*$/gm, '');

            if (content.length !== originalLength) {
                fs.writeFileSync(fullPath, content);
                console.log('Limpio:', fullPath);
            }
        }
    }
}

dirsToScan.forEach(cleanFiles);
console.log('Limpieza completada.');
