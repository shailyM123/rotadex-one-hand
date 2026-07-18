const fs = require('fs');
const path = require('path');
const vm = require('vm');

const htmlPath = path.join(__dirname, '..', 'view_stl_model.html');
console.log('Evaluating script blocks in HTML:', htmlPath);
const html = fs.readFileSync(htmlPath, 'utf8');

// Find all script blocks
const rx = /<script>([\s\S]+?)<\/script>/g;
let match;
let count = 0;

// Mock window/browser globals to test execution
const sandbox = {
    window: {},
    document: {
        createElement: () => ({ className: '', style: {}, getContext: () => ({ fillStyle: '', fillRect: () => {}, fillText: () => {} }) }),
        getElementById: () => ({ appendChild: () => {}, classList: { add: () => {} } }),
        body: { appendChild: () => {} }
    },
    navigator: { userAgent: '' },
    innerWidth: 1024,
    innerHeight: 768,
    devicePixelRatio: 1,
    requestAnimationFrame: () => {},
    addEventListener: () => {}
};
sandbox.window = sandbox;

vm.createContext(sandbox);

while ((match = rx.exec(html)) !== null) {
    count++;
    console.log(`\nEvaluating Script Block #${count}...`);
    try {
        vm.runInContext(match[1], sandbox, { filename: `script_${count}.js` });
        console.log(`Script Block #${count} evaluated successfully!`);
    } catch (err) {
        console.error(`Error in Script Block #${count}:`);
        console.error(err.stack || err);
        if (err instanceof SyntaxError) {
            // Find line number from stack
            const matchStack = err.stack.match(/script_\d+\.js:(\d+)/);
            if (matchStack) {
                const lineNum = parseInt(matchStack[1], 10);
                const lines = match[1].split('\n');
                console.error('\nCode Snippet around error:');
                for (let l = Math.max(1, lineNum - 3); l <= Math.min(lines.length, lineNum + 3); l++) {
                    console.error(`${l === lineNum ? '>> ' : '   '}${l}: ${lines[l - 1]}`);
                }
            }
        }
    }
}
