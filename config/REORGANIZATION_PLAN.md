# Config Directory Reorganization Plan

## Overview
This document outlines the reorganization of the Comic AI configuration directory structure for better organization and maintainability.

## Current Structure
```
config/
├── *.yaml (20+ files in root)
```

## Target Structure
```
config/
├── core/                          # System core configurations
│   ├── main_system_config.yaml
│   ├── logging_config.yaml
│   ├── database_config.yaml
│   ├── monitoring_config.yaml
│   └── performance_config.yaml
├── services/                      # Service-specific configurations
│   ├── api_config.yaml
│   ├── trading_config.yaml
│   ├── dashboard_config.yaml
│   ├── engine_config.yaml
│   └── deployment_config.yaml
├── security/                      # Security configurations
│   ├── security_config.yaml
│   ├── privacy_config.yaml
│   └── compliance_config.yaml
├── deployment/                    # Deployment configurations
│   ├── docker_config.yaml
│   ├── kubernetes_config.yaml
│   └── ci_cd_config.yaml
├── optimization/                  # Optimization configurations
│   ├── compression_optimizer.yaml
│   ├── optimization_config.yaml
│   └── performance_tuning.yaml
├── templates/                     # Configuration templates
│   ├── .env.template
│   ├── config.template.yaml
│   └── README_TEMPLATES.md
└── README.md                      # Configuration guide
```

## File Migration Map

### core/ (System Core)
- main_system_config.yaml → core/
- logging_config.yaml → core/
- database_config.yaml → core/
- monitoring_config.yaml → core/
- performance_config.yaml → core/
- network_config.yaml → core/

### services/ (Service Configurations)
- api_config.yaml → services/
- trading_config.yaml → services/
- dashboard_config.yaml → services/ (from dashboard/)
- engine_config.yaml → services/ (from engine/)
- deployment_config.yaml → services/
- backup_config.yaml → services/

### security/ (Security Configurations)
- security_config.yaml → security/
- privacy_config.yaml → security/
- compression.control.yaml → security/ (access control)
- immune_config.yaml → security/ (from engine/)

### deployment/ (Deployment Configurations)
- deployment.yaml → deployment/
- docker-compose.yml → deployment/

### optimization/ (Optimization)
- compression_optimizer.yaml → optimization/
- optimization_config.yaml → optimization/

## Implementation Steps

1. ✅ Create directory structure
2. ⏳ Copy configuration files to new locations
3. ⏳ Update import paths in source code
4. ⏳ Update references in documentation
5. ⏳ Create README files for each section
6. ⏳ Test all configurations still load correctly
7. ⏳ Remove old files (after verification)

## Files to Keep in config/ Root
- README.md (main config guide)
- config_validation_report.json (generated)

## Backward Compatibility

### Option 1: Hard Links (Recommended)
Keep files in original location as hard links pointing to new locations. This maintains backward compatibility without duplicating storage.

### Option 2: Symlinks
Create symbolic links from old to new locations.

### Option 3: Update Imports (Breaking)
Update all code to use new paths. Requires code changes but cleaner.

### Option 4: Config Loader Enhancement
Enhance config loader to search both old and new locations (most compatible).

## Benefits of Reorganization

✅ **Better Organization**: Clear separation of concerns
✅ **Easier Maintenance**: Related configs grouped together
✅ **Scalability**: Easier to add new services/configs
✅ **Clarity**: Self-documenting structure
✅ **Team Onboarding**: New developers understand structure faster
✅ **Documentation**: Each section can have its own README

## Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Breaking existing imports | Use symlinks or hard links during transition |
| Config loader unable to find files | Test thoroughly before removing old files |
| Missing configurations | Verify all files copied correctly |
| Script breakage | Run validation script after migration |

## Validation Checklist

- [ ] All 20+ YAML files have been moved/linked
- [ ] Validation script runs without errors
- [ ] Application loads all configs correctly
- [ ] No hardcoded config paths in code
- [ ] All tests pass
- [ ] Documentation updated
- [ ] README files created for each section

## Timeline

- **Phase 1** (Today): Create structure
- **Phase 2** (Today): Copy files, create symlinks
- **Phase 3** (Today): Test all configurations
- **Phase 4** (Tomorrow): Update documentation
- **Phase 5** (Later): Update code imports (optional, for cleanup)

## Related Documents

- QUICK_CONFIG_REFERENCE.md - Quick reference guide
- CONFIG_SETUP_REPORT.md - Complete setup instructions
- AGENTS.md - Development guidelines

---

**Status**: Ready for implementation
**Last Updated**: 2026-02-13
**Owner**: Comic AI DevOps Team
