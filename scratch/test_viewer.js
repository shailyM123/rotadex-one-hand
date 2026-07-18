const fs = require('fs');
const path = require('path');

const htmlPath = path.join(__dirname, '..', 'view_stl_model.html');
console.log('Reading HTML file from:', htmlPath);
const html = fs.readFileSync(htmlPath, 'utf8');

// Extract script content
const scriptMatch = html.match(/<script>([\s\S]+?)<\/script>/);
if (!scriptMatch) {
    console.error('No script tag found!');
    process.exit(1);
}

const scriptContent = scriptMatch[1];

// Let's create a sandboxed execution context to check for exceptions
// Mock standard globals needed for basic parsing
const mockSandbox = {
    console: console,
    document: {
        createElement: () => ({ className: '', set innerHTML(val) {} }),
        getElementById: () => ({ appendChild: () => {} })
    },
    THREE: {
        BufferGeometry: class {
            setAttribute(name, attr) {
                console.log(`      Set attribute: ${name} with ${attr.array.length / 3} vertices`);
            }
        },
        Float32BufferAttribute: class {
            constructor(array, size) {
                this.array = array;
                this.size = size;
            }
        }
    }
};

global.THREE = mockSandbox.THREE;

// Run the parts extraction and parsing logic
try {
    // We only want to test the JSON data loading and the parsing logic, not the full Three.js scene setup.
    // Let's extract the STL_DATA, PARTS_CFG, parseSTL function, and the loop.
    
    // We can run the script content by replacing the Three.js setup parts to avoid errors,
    // or just extract the relevant functions and run them.
    
    // Let's define the parts and run
    console.log('Parsing STL data and running loader loop...');
    
    // Safe extraction of STL_DATA object
    const stlDataMatch = scriptContent.match(/const STL_DATA = (\{[\s\S]+?\});/);
    if (!stlDataMatch) {
        throw new Error('Could not find STL_DATA in script!');
    }
    const STL_DATA = JSON.parse(stlDataMatch[1]);
    console.log('Successfully loaded STL_DATA. Keys:', Object.keys(STL_DATA));

    // Extract parseSTL function
    const parseSTLMatch = scriptContent.match(/function parseSTL\([\s\S]+?return g;\s*\}/);
    if (!parseSTLMatch) {
        throw new Error('Could not find parseSTL function in script!');
    }
    
    // Create the parseSTL function in Node
    const parseSTL = new Function('text', parseSTLMatch[0] + '\nreturn parseSTL(text);');
    
    // Extract PARTS_CFG
    const partsCfgMatch = scriptContent.match(/const PARTS_CFG = (\[[\s\S]+?\]);/);
    if (!partsCfgMatch) {
        throw new Error('Could not find PARTS_CFG in script!');
    }
    // We'll evaluate PARTS_CFG. Since it contains hex numbers like 0x475569, it's valid JS.
    const PARTS_CFG = new Function(`return ${partsCfgMatch[1]};`)();
    
    // Run the parser loop
    PARTS_CFG.forEach((part, index) => {
        const text = STL_DATA[part.key];
        if (text) {
            console.log(`  Parsing: ${part.name} (${part.key})...`);
            const geo = parseSTL(text);
            console.log(`    Success!`);
        } else {
            console.log(`  Skipping: ${part.name} (no text data)`);
        }
    });
    
    console.log('\nLoader logic runs perfectly in Node.js!');
} catch (err) {
    console.error('\nERROR DETECTED during execution:');
    console.error(err);
}
