# UniContentDownloader

UniContentDownloader is currently a minimal repository containing only documentation. The repository is in its initial state and ready for development of content downloading functionality.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Current Repository State
- **IMPORTANT**: This repository currently contains only a README.md file (44 bytes)
- No source code, build systems, or dependencies are present yet
- Repository is ready for initial development and project setup

### Initial Setup and Exploration
Always start by exploring the current state of the repository:
```bash
# Navigate to repository root
cd /home/runner/work/UniContentDownloader/UniContentDownloader

# Check current file structure
ls -la
find . -type f | grep -v "/.git/" | head -20

# Review any documentation
cat README.md

# Check for hidden configuration files
find . -name ".*" -type f | head -10

# Check git status and recent commits
git --no-pager status
git --no-pager log --oneline -10
```

### When Source Code is Added
Once the repository contains actual source code, follow these validation steps:

#### Identify Project Type and Build System
```bash
# Check for common project files (run all that exist)
ls -la package.json      # Node.js project
ls -la requirements.txt  # Python project
ls -la Cargo.toml       # Rust project
ls -la pom.xml          # Maven Java project
ls -la build.gradle     # Gradle project
ls -la Makefile         # Make-based project
ls -la setup.py         # Python setuptools
ls -la composer.json    # PHP project
ls -la go.mod           # Go project
```

#### Build and Dependencies
**CRITICAL TIMING REQUIREMENTS:**
- **NEVER CANCEL** any build or install commands
- Use timeouts of **60+ minutes** for builds
- Use timeouts of **30+ minutes** for dependency installation
- Document actual timing after validation

Common dependency installation patterns to try (when applicable):
```bash
# Node.js projects
npm install                    # Timeout: 30+ minutes. NEVER CANCEL.
npm run build                  # Timeout: 60+ minutes. NEVER CANCEL.

# Python projects  
pip install -r requirements.txt   # Timeout: 30+ minutes. NEVER CANCEL.
python setup.py build            # Timeout: 60+ minutes. NEVER CANCEL.

# Rust projects
cargo build                    # Timeout: 60+ minutes. NEVER CANCEL.

# Make-based projects
make                          # Timeout: 60+ minutes. NEVER CANCEL.

# Go projects
go mod download               # Timeout: 30+ minutes. NEVER CANCEL.
go build                      # Timeout: 60+ minutes. NEVER CANCEL.
```

#### Testing
Always identify and run the test suite (when available):
```bash
# Common test commands to try
npm test                      # Timeout: 30+ minutes. NEVER CANCEL.
npm run test                  # Timeout: 30+ minutes. NEVER CANCEL.
python -m pytest             # Timeout: 30+ minutes. NEVER CANCEL.
python -m unittest discover  # Timeout: 30+ minutes. NEVER CANCEL.
cargo test                   # Timeout: 30+ minutes. NEVER CANCEL.
make test                    # Timeout: 30+ minutes. NEVER CANCEL.
go test ./...                # Timeout: 30+ minutes. NEVER CANCEL.
```

#### Running the Application
Once built, identify how to run the application:
```bash
# Common run patterns
npm start                     # Web applications
npm run dev                   # Development server
python main.py               # Python scripts
python -m [module_name]      # Python modules
cargo run                    # Rust applications
./[executable_name]          # Compiled binaries
java -jar [jarfile]          # Java applications
go run .                     # Go applications
```

### Validation Requirements

#### Manual Testing Protocol
**CRITICAL**: After any changes, ALWAYS perform complete end-to-end validation:

1. **Build Validation**:
   - Verify all build commands complete successfully
   - Document any new build errors and resolve them
   - Time each build step and update timeout recommendations

2. **Functional Validation**:
   - Run the application if it exists
   - Test core functionality workflows
   - Verify output files, network requests, or UI interactions as appropriate
   - Document any runtime issues

3. **Test Suite Validation**:
   - Run all existing tests
   - Verify tests pass after your changes
   - Add new tests for new functionality when possible

#### Linting and Code Quality
Always check for and run code quality tools:
```bash
# Common linting commands
npm run lint                  # JavaScript/TypeScript
npm run format               # Code formatting
eslint .                     # ESLint
prettier --check .           # Prettier
black .                      # Python Black formatter
cargo fmt                   # Rust formatting
cargo clippy                 # Rust linting
go fmt ./...                 # Go formatting
go vet ./...                 # Go static analysis
```

### Pre-commit Validation Checklist
Before completing any work, ALWAYS:
- [ ] Build succeeds with no new errors
- [ ] All existing tests pass
- [ ] Linting/formatting passes
- [ ] Application runs and core functionality works
- [ ] New functionality has been manually tested
- [ ] Documentation updated if needed

### Expected Project Evolution
As UniContentDownloader develops, expect to find:
- Download/scraping functionality for various content types
- Configuration files for target sites or content sources
- Storage/output directory management
- Possibly CLI interface or web interface
- Authentication/session management for protected content
- Rate limiting and respectful scraping practices

### Troubleshooting Common Issues

#### If Build Fails
1. Check for missing system dependencies
2. Verify correct language/runtime version
3. Clear dependency caches (npm cache clean, pip cache purge, etc.)
4. Check for proxy/firewall issues blocking downloads
5. Document the failure in these instructions for future reference

#### If Tests Fail
1. Run individual test files to isolate failures
2. Check for test data dependencies
3. Verify test environment setup requirements
4. Only fix test failures related to your changes

#### If Application Won't Start
1. Check for missing runtime configuration
2. Verify required environment variables
3. Check for required external services (databases, APIs)
4. Review application logs for specific error messages

### Repository Structure Reference
Current structure (as of last validation):
```
.
├── .git/                    # Git repository data
├── .github/                 # GitHub configuration
│   └── copilot-instructions.md  # This file (7,991 bytes)
└── README.md               # Project documentation (44 bytes)
```

## Common Commands Reference

### Repository Information
```bash
# Get repository status
git --no-pager status

# View recent commits  
git --no-pager log --oneline -10

# Check for uncommitted changes
git --no-pager diff

# View file tree
find . -type f | grep -v "/.git/" | sort
```

### File Analysis
```bash
# Check file sizes
ls -lah

# Search for specific patterns
grep -r "TODO" . --exclude-dir=.git
grep -r "HACK" . --exclude-dir=.git
grep -r "FIXME" . --exclude-dir=.git

# Find configuration files
find . -name "*.json" -o -name "*.yml" -o -name "*.yaml" -o -name "*.toml" -o -name "*.ini" | grep -v "/.git/"
```

### Development Workflow
1. Always explore repository state first
2. Identify project type and requirements
3. Install dependencies with appropriate timeouts
4. Build project with appropriate timeouts  
5. Run tests with appropriate timeouts
6. Make minimal, focused changes
7. Validate changes thoroughly
8. Run pre-commit checks

---

**Last Updated**: Generated for minimal repository state
**Validation Status**: Instructions validated for empty repository exploration
**Next Review**: Required when source code is added to repository