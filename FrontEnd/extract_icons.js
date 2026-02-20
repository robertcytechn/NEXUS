const fs = require('fs');
const css = fs.readFileSync('node_modules/primeicons/primeicons.css', 'utf8');
const matches = css.match(/\.pi-[a-z0-9-]+(?=:before)/g);
if (matches) {
    const icons = matches.map(m => m.replace('.', ''));
    fs.writeFileSync('src/config/primeicons.json', JSON.stringify([...new Set(icons)], null, 2));
    console.log('Saved', icons.length);
} else {
    console.log('No matches');
}
