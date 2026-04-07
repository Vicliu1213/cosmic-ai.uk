---
name: bun-toolkit
description: Comprehensive guide to Bun runtime, package manager, test runner, and bundler
license: MIT
compatibility: opencode
metadata:
  audience: developers
  categories:
    - development-tools
    - javascript
    - typescript
    - package-management
    - testing
    - bundling
  version: 1.0.0
  tags:
    - bun
    - runtime
    - bundler
    - test-runner
    - package-manager
    - performance
---

## What I do

- Provide complete Bun command reference with practical examples
- Guide TypeScript/JavaScript project setup and execution
- Optimize development workflows with fast tooling
- Configure testing, building, and deployment pipelines
- Explain performance tuning and best practices
- Troubleshoot common issues with Bun runtime

## When to use me

Use this skill when:
- Setting up a new JavaScript/TypeScript project with Bun
- Running scripts and managing dependencies
- Writing and running unit tests
- Bundling code for production deployment
- Executing npm package CLIs with bunx
- Optimizing project build and test performance
- Migrating from Node.js to Bun
- Creating standalone executables

## Key Features

### 1. Runtime Execution (`bun run`)
Execute TypeScript, JSX, and JavaScript directly with hot reload and debugging:
```bash
bun run script.ts              # Direct execution
bun run --watch server.ts      # Monitor mode
bun run --hot app.ts           # Hot reload
bun run --inspect script.ts    # Enable debugger
```

### 2. Package Management (`bun install`)
Ultra-fast dependency management with caching and workspaces:
```bash
bun install                    # Install all dependencies
bun add express               # Add package
bun remove express            # Remove package
bun audit                      # Check vulnerabilities
```

### 3. Testing (`bun test`)
Jest-compatible test runner with coverage and watch mode:
```bash
bun test                       # Run all tests
bun test --watch              # Monitor mode
bun test --coverage           # Generate coverage
bun test --concurrent         # Parallel execution
```

### 4. Bundling (`bun build`)
Native bundler for browser, server, and standalone executables:
```bash
bun build ./src/index.ts      # Bundle for browser
bun build --target=bun ./server.ts  # Optimize for Bun
bun build --compile ./app.ts  # Create executable
```

### 5. Package Execution (`bunx`)
Run npm package CLIs without global installation:
```bash
bunx prisma migrate          # Database migrations
bunx prettier ./src           # Code formatting
bunx vite dev                # Development server
```

## Command Reference

### Core Commands

| Command | Purpose | Example |
|---------|---------|---------|
| `bun run` | Execute files/scripts | `bun run app.ts` |
| `bun install` | Manage dependencies | `bun install express` |
| `bun test` | Run tests | `bun test --watch` |
| `bun build` | Bundle code | `bun build ./src/index.ts` |
| `bunx` | Execute npm CLI | `bunx prisma migrate` |
| `bun repl` | Interactive shell | `bun repl` |
| `bun init` | Create project | `bun init` |
| `bun create` | Use template | `bun create next-app` |

### Run Flags

| Flag | Use Case | Example |
|------|----------|---------|
| `--watch` | File change restart | `bun run --watch server.ts` |
| `--hot` | Hot module reload | `bun run --hot app.ts` |
| `--inspect` | Enable debugger | `bun run --inspect script.ts` |
| `--cpu-prof` | CPU profiling | `bun run --cpu-prof app.ts` |
| `--heap-prof` | Memory analysis | `bun run --heap-prof app.ts` |
| `-i` | Auto-install deps | `bun run -i script.ts` |
| `--env-file` | Load .env | `bun run --env-file=.env.local` |

### Install Flags

| Flag | Use Case | Example |
|------|----------|---------|
| `-d, --dev` | Dev dependency | `bun add -d @types/node` |
| `--production` | Skip dev deps | `bun install --production` |
| `-f, --force` | Reinstall all | `bun install -f` |
| `--frozen-lockfile` | Lock versions | `bun install --frozen-lockfile` |
| `--dry-run` | Simulate install | `bun install --dry-run` |
| `--audit` | Check security | `bun audit` |
| `--outdated` | Show old versions | `bun outdated` |

### Test Flags

| Flag | Use Case | Example |
|------|----------|---------|
| `--watch` | Monitor tests | `bun test --watch` |
| `--coverage` | Generate report | `bun test --coverage` |
| `--timeout` | Test timeout (ms) | `bun test --timeout=10000` |
| `--concurrent` | Parallel tests | `bun test --concurrent` |
| `--randomize` | Random order | `bun test --randomize` |
| `--retry` | Retry failures | `bun test --retry=3` |
| `--bail` | Stop after N fails | `bun test --bail=5` |

### Build Flags

| Flag | Use Case | Example |
|------|----------|---------|
| `--production` | Optimize output | `bun build --production ./src` |
| `--minify` | Minimize size | `bun build --minify ./src` |
| `--splitting` | Code splitting | `bun build --splitting ./src` |
| `--sourcemap` | Debug info | `bun build --sourcemap=external` |
| `--compile` | Executable | `bun build --compile ./app.ts` |
| `--target=bun` | Bun runtime | `bun build --target=bun ./server.ts` |
| `--target=browser` | Browser | `bun build --target=browser ./app.ts` |

## Workflow Examples

### Development Workflow
```bash
# Start project
bun create vite-app my-app
cd my-app
bun install

# Development with hot reload
bun run --watch --hot dev

# Run tests during development
bun test --watch
```

### Production Workflow
```bash
# Install only production dependencies
bun install --production

# Run full test suite with coverage
bun test --coverage --reporter=junit --reporter-outfile=results.xml

# Build optimized bundle
bun build --production --minify --splitting --outdir=dist ./src/index.ts

# Security check
bun audit
```

### Deployment Workflow
```bash
# Create standalone executable
bun build --compile --outfile=app ./src/server.ts

# Copy executable to server
# ./app  (no Node.js needed!)
```

### Plugin System (Your Project)
```bash
# Run plugin loader with auto-install
bun run -i src/plugins/plugin_loader.py

# Watch plugin development
bun run --watch src/plugins/multi_agent_trading.py

# Test plugin system
bun test src/plugins/__tests__/

# Build plugin distribution
bun build --target=bun --outfile=dist/plugins.js ./src/plugins/*.py
```

## Quick Reference

### Essential Commands
```bash
# Development
bun run --watch --hot app.ts        # Dev with hot reload
bun test --watch                    # Tests with watch
bun repl                            # Interactive shell

# Package Management
bun install                         # Install deps
bun add <pkg>                       # Add package
bun remove <pkg>                    # Remove package
bun audit                           # Check vulnerabilities

# Building
bun build ./src/index.ts           # Bundle
bun build --compile ./app.ts       # Create executable
bun build --production ./src/index.ts  # Optimize

# Execution
bunx prisma migrate                 # Run CLI tools
bunx prettier ./src                 # Format code
```

### Version Info
```bash
bun --version                       # Current version
bun upgrade                         # Upgrade Bun
bun --help                          # Full help text
```

## Performance Tips

1. **Use `--hot` for development**: Enables hot module reloading without full restart
2. **Enable code splitting**: `bun build --splitting` reduces bundle size
3. **Run tests concurrently**: `bun test --concurrent --max-concurrency=20`
4. **Use `--production` flag**: Enables minification and optimization
5. **Cache dependencies**: Bun uses global cache by default (faster installs)
6. **Profile with `--cpu-prof`**: Identify performance bottlenecks

## Files Reference

- **Main Guide**: `BUN_FEATURES_GUIDE.md` - Comprehensive documentation
- **Configuration**: `bunfig.toml` - Project configuration
- **Package**: `package.json` - Dependencies and scripts
- **Lock file**: `bun.lock` - Dependency versions

## Configuration

Create `bunfig.toml` in project root:
```toml
[install]
production = false
exact = false

[build]
target = "browser"
format = "esm"
minify = "all"

[runtime]
alwaysFreeze = true
```

## Integration with Your Project

For the cosmic-ai.uk plugin system:

1. **Run plugins**:
   ```bash
   bun run -i src/plugins/plugin_loader.py
   ```

2. **Monitor plugins**:
   ```bash
   bun run --watch src/plugins/multi_agent_trading.py
   ```

3. **Build plugin distribution**:
   ```bash
   bun build --target=bun --outfile=dist/plugins.js ./src/plugins/
   ```

4. **Create standalone plugin app**:
   ```bash
   bun build --compile --outfile=plugins-app ./src/plugins/plugin_loader.py
   ```

## Common Troubleshooting

### Issue: "Module not found"
- Use `bun run -i` to auto-install missing dependencies
- Ensure `bunfig.toml` has correct paths

### Issue: Hot reload not working
- Use `bun run --hot` instead of `--watch`
- Some frameworks need specific configuration

### Issue: Bundle too large
- Use `--minify --splitting` flags
- Check for unused dependencies with `bun audit`

### Issue: Tests timeout
- Increase timeout: `bun test --timeout=30000`
- Check for infinite loops or async issues

## Resources

- **Official Docs**: https://bun.sh/docs
- **GitHub**: https://github.com/oven-sh/bun
- **Discussions**: https://github.com/oven-sh/bun/discussions

---

**Version**: 1.0.0  
**Last Updated**: 2024-04-06  
**Bun Version**: 1.3.11+
