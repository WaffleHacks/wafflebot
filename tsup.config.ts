import { defineConfig } from 'tsup';

// defined folders from .sapphirerc.json
const sapphireFolders = ['arguments', 'commands', 'interaction-handlers', 'listeners', 'preconditions'].map(
  (folder) => `src/${folder}/*.ts`,
);

export default defineConfig({
  clean: true,
  bundle: true,
  dts: false,
  entry: ['src/index.ts', 'src/instrumentation.ts', ...sapphireFolders],
  format: ['cjs'],
  minify: false,
  tsconfig: 'tsconfig.json',
  target: 'es2020',
  splitting: true,
  skipNodeModulesBundle: true,
  sourcemap: true,
  shims: false,
  keepNames: true,
});
