# Changelog

## [1.0.2](https://github.com/FabienMeyer/elims/compare/elims-v1.0.1...elims-v1.0.2) (2026-11-27)


### Bug Fixes

* **backend:** harden CORS, settings secrets, readiness, and migrations ([f0edb0d](https://github.com/FabienMeyer/elims/commit/f0edb0d0d6a7301a9dbdeca350300d9251f8f6bd))
* **frontend:** cancel and time out API requests and close review follow-ups ([506583b](https://github.com/FabienMeyer/elims/commit/506583bffa434b57c6932213eb29206db447def0))
* **frontend:** show one accurate backend status and replace template leftovers ([1ca376e](https://github.com/FabienMeyer/elims/commit/1ca376e04df39828ee46ca9c989a92d36aa699d5))

## [1.0.1](https://github.com/FabienMeyer/elims/compare/elims-v1.0.0...elims-v1.0.1) (2026-11-27)


### Bug Fixes

* **backend:** close sessions on errors, require ENVIRONMENT, fix redirects ([e4d8cdb](https://github.com/FabienMeyer/elims/commit/e4d8cdb98b0555ef46b34f88b922c27f537e4ecf))
* **backend:** release database sessions before error responses ([ff5b3d6](https://github.com/FabienMeyer/elims/commit/ff5b3d605e638d5ceeadc9fb628709fb0d5dba81))
* **backend:** require an explicit ENVIRONMENT setting ([4ad55b1](https://github.com/FabienMeyer/elims/commit/4ad55b1f89b98becf1f520d9d76f5c0af5ca4062))
* **infra:** keep proxy redirects on the public host and scheme ([9b51618](https://github.com/FabienMeyer/elims/commit/9b516188c1e0b3c4a68456492117e041d32d533d))

## 1.0.0 (2026-11-22)


### Features

* **release:** automate changelog and package publishing ([5c55678](https://github.com/FabienMeyer/elims/commit/5c556783d182a831f94f3f3c4888ff50fb011c99))
* **release:** automate changelog and package publishing ([d620f94](https://github.com/FabienMeyer/elims/commit/d620f945627f786c410dedfadd951558aabad332))


### Bug Fixes

* **ci:** accept Dependabot development scopes ([a1096c7](https://github.com/FabienMeyer/elims/commit/a1096c7805874e53798d4adcd636c5f7bc9aad74))
* **ci:** accept Dependabot development scopes ([043cb3a](https://github.com/FabienMeyer/elims/commit/043cb3a7702bebd39843a82ae4c13af5b52737fd))
* **ci:** revalidate edited pull request titles ([c66115c](https://github.com/FabienMeyer/elims/commit/c66115cf3534fbe0a63089c119e3f97d58cb0d30))
* **deps:** align jest-dom 8 testing packages ([1eb68b6](https://github.com/FabienMeyer/elims/commit/1eb68b643467996b175e6f84c05c21b9cdd9c153))
* **deps:** align Vitest 5 testing packages ([175ca6b](https://github.com/FabienMeyer/elims/commit/175ca6be3f9a93228b377c1ac522ee5f2a3c6ae2))
* **deps:** migrate test server to MSW 3 ([62cb2c6](https://github.com/FabienMeyer/elims/commit/62cb2c6550f7ee3de0687aa034371dd6d8edd201))
* **deps:** refresh jsdom 31 lockfile ([9bb8d55](https://github.com/FabienMeyer/elims/commit/9bb8d55e56fdc736b531cb3fe8d291ddfe0c328a))

## Changelog

All notable changes to ELIMS are documented here. Release Please generates
version sections from Conventional Commit messages merged into `main`.
