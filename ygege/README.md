# Home Assistant Add-on: Ygege — YGG Indexer

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![amd64](https://img.shields.io/badge/amd64-yes-green)
![aarch64](https://img.shields.io/badge/aarch64-yes-green)
![armv7](https://img.shields.io/badge/armv7-yes-green)

Ships [Ygege](https://github.com/djerayane/ygege) as an add-on: a **YGG Torrent** indexer working through a **Nostr** relay, queryable by **Prowlarr** (or any Torznab client).

## Features

- **Torznab indexer** — plugs into Prowlarr like any regular indexer
- **Nostr relay** — no direct dependency on the site, configurable relay
- **Built from source** — multi-stage Rust build at install time

## Configuration

```yaml
relay_url: "wss://relay.ygg.gratis"   # Nostr relay to use
log_level: "info"                      # trace | debug | info | warn | error
```

## Prowlarr integration

1. Start the add-on — it listens on port `8715`
2. Prowlarr → **Indexers → Add Indexer** → look for the generic/Ygege type
3. URL: `http://<home-assistant-ip>:8715`

## Notes

- The initial build compiles Ygege from the `develop` branch: the first install may take several minutes depending on the machine.
- Using tracker indexers is subject to the laws applicable where you live; this add-on is a purely technical wrapper.

## License

Add-on: MIT — Ygege: see upstream repository.
