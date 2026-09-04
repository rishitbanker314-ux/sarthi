const fs = require('fs');

function hexToRgb(hex) {
  let r = 0, g = 0, b = 0;
  if (hex.length === 4) {
    r = "0x" + hex[1] + hex[1];
    g = "0x" + hex[2] + hex[2];
    b = "0x" + hex[3] + hex[3];
  } else if (hex.length === 7) {
    r = "0x" + hex[1] + hex[2];
    g = "0x" + hex[3] + hex[4];
    b = "0x" + hex[5] + hex[6];
  }
  return [+r, +g, +b];
}

function luminance(r, g, b) {
  const a = [r, g, b].map((v) => {
    v /= 255;
    return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
  });
  return a[0] * 0.2126 + a[1] * 0.7152 + a[2] * 0.0722;
}

function contrast(hex1, hex2) {
  const rgb1 = hexToRgb(hex1);
  const rgb2 = hexToRgb(hex2);
  const lum1 = luminance(rgb1[0], rgb1[1], rgb1[2]);
  const lum2 = luminance(rgb2[0], rgb2[1], rgb2[2]);
  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);
  return (brightest + 0.05) / (darkest + 0.05);
}

const colors = {
  light: { bg: '#ffffff', text: '#0f172a', accent: '#4f46e5', info: '#0284c7', tip: '#059669', warning: '#d97706', misconception: '#e11d48', ai: '#7c3aed' },
  dark: { bg: '#0f172a', text: '#f8fafc', accent: '#818cf8', info: '#38bdf8', tip: '#34d399', warning: '#fbbf24', misconception: '#fb7185', ai: '#a78bfa' }
};

let out = "Contrast Ratios:\n";
['light', 'dark'].forEach(theme => {
  out += `\n${theme.toUpperCase()} (Bg: ${colors[theme].bg})\n`;
  for (const [name, hex] of Object.entries(colors[theme])) {
    if (name === 'bg') continue;
    const ratio = contrast(colors[theme].bg, hex).toFixed(2);
    out += `${name.padEnd(15)} ${hex} : ${ratio}:1\n`;
  }
});

fs.writeFileSync('contrast.txt', out);
console.log(out);
