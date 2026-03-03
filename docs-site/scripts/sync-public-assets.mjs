import { cpSync, mkdirSync, rmSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const docsSiteRoot = path.resolve(__dirname, '..');
const repoRoot = path.resolve(__dirname, '..', '..');

const publicDir = path.join(docsSiteRoot, 'public');
const srcMedia = path.join(repoRoot, 'docs', 'media');
const srcVendordep = path.join(repoRoot, 'docs', 'vendordep');
const srcJavadocs = path.join(repoRoot, 'docs', 'javadocs');

const destMedia = path.join(publicDir, 'media');
const destVendordep = path.join(publicDir, 'vendordep');
const destJavadocs = path.join(publicDir, 'javadocs');

mkdirSync(publicDir, { recursive: true });

rmSync(destMedia, { recursive: true, force: true });
rmSync(destVendordep, { recursive: true, force: true });
rmSync(destJavadocs, { recursive: true, force: true });

cpSync(srcMedia, destMedia, { recursive: true });
cpSync(srcVendordep, destVendordep, { recursive: true });
cpSync(srcJavadocs, destJavadocs, { recursive: true });

console.log('Synced docs assets to docs-site/public.');
