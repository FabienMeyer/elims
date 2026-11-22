# Architecture

This package contains generic helpers only. It must not contain business models, transport contracts, persistence logic, or application configuration.

Consumers should import the supported public API from `elims_utils` rather than internal modules.
