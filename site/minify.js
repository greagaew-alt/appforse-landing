/*
 * Сжимает готовую страницу: JS через terser, CSS через clean-css, разметку
 * через html-minifier-terser. Разметку для поисковиков (JSON-LD) не трогаем.
 * Запуск: node minify.js index.html
 */
const fs = require('fs');
const path = require('path');
const { minify: minifyHtml } = require('html-minifier-terser');
const { minify: minifyJs } = require('terser');
const CleanCSS = require('clean-css');

const file = path.join(__dirname, process.argv[2] || 'index.html');

(async () => {
  let html = fs.readFileSync(file, 'utf8');
  const before = Buffer.byteLength(html);

  // ── CSS в <style> ──
  const cleaner = new CleanCSS({ level: 2 });
  html = html.replace(/<style>([\s\S]*?)<\/style>/g, (m, css) => {
    const out = cleaner.minify(css);
    if (out.errors.length) throw new Error('CSS: ' + out.errors.join('; '));
    return '<style>' + out.styles + '</style>';
  });

  // ── JS в <script> без src и без type ──
  const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
  for (const m of scripts) {
    const res = await minifyJs(m[1], {
      compress: { passes: 2 },
      mangle: true,
      format: { comments: false },
    });
    if (res.error) throw res.error;
    html = html.replace(m[0], '<script>' + res.code + '</script>');
  }

  // ── разметка ──
  html = await minifyHtml(html, {
    collapseWhitespace: true,
    conservativeCollapse: false,
    removeComments: true,
    removeRedundantAttributes: false,
    removeScriptTypeAttributes: false,
    keepClosingSlash: true,
    minifyCSS: false,
    minifyJS: false,
    processScripts: [],
  });

  fs.writeFileSync(file, html, 'utf8');
  const after = Buffer.byteLength(html);
  console.log('%s: %d KB → %d KB (−%d%%)', process.argv[2], Math.round(before / 1024),
    Math.round(after / 1024), Math.round((1 - after / before) * 100));
})().catch(e => {
  console.error('минификация упала:', e.message);
  process.exit(1);
});
