# Reference host card: llama.cpp b12066 on Darwin arm64

## What is measured, and what is conjecture

**Measured:** the publisher's metadata for the build and the weights, fetched on
2026-11-21; the reference machine's own reported hardware; and the settings the
source carries at `0e4a9b68`, quoted from its files.

**Conjecture:** none of this has served a request yet. That the pinned command
loads the pinned file and answers is P4.2's to demonstrate; this card states what
the configuration *is*, with the evidence beside each value.

## The machine

- Apple M5 Max, 128 GB unified memory, macOS 27.2.1, `arm64`.
  From `sysctl -n machdep.cpu.brand_string`, `sysctl -n hw.memsize`,
  `sw_vers -productVersion` and `uname -m`.
- Homebrew's `llama.cpp` 0.9.0 — build 12110, commit `cd959bae9`, at
  `/opt/homebrew/bin/llama-server` — is installed here and is **not** the subject.
  The documented command names the b12066 binary by path, so `PATH` cannot
  substitute a different build.
- Disk headroom at the time of writing: 578 GiB, against an 8.1 GB download.

## The build

Fetched from `https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b12066`:

| Value | Recorded |
| --- | --- |
| Tag | `b12066`, released 2026-11-03 |
| Source commit | `713319e28492d319b81e49646151f6bbdb9d4551` (the tag's object, `git/ref/tags/b12066`) |
| Asset | `llama-b12066-bin-macos-arm64.tar.gz` |
| Asset size | 16,548,566 bytes |
| Asset sha256 | `909053143be864f6b2c45b45e140575904fde163978d33cea53f30f318e09a19` |

The same release publishes 38 assets, including six Ubuntu CUDA variants and a
separate `macos-x64` build. Only the `macos-arm64` asset is claimed by this card:
a build tag does not name one artifact, which is why the digest is recorded
rather than the tag alone.

```sh
curl -sS https://api.github.com/repos/ggml-org/llama.cpp/releases/tags/b12066 |
  jq -r '.assets[] | select(.name=="llama-b12066-bin-macos-arm64.tar.gz") |
         "\(.size) \(.digest)"'
```

## The weights

Fetched from `https://huggingface.co/api/models/JetBrains/Mellum2.1-12B-A2.5B-Thinking-GGUF`
and its `/tree/main?recursive=1` listing:

| Value | Recorded |
| --- | --- |
| Repository | `JetBrains/Mellum2.1-12B-A2.5B-Thinking-GGUF` |
| Revision | `4159d684ffdb09ba89dc2a58feb3e75c54eef036` |
| File | `Mellum2.1-12B-A2.5B-Thinking-Q4_K_M.gguf` |
| Size | 8,071,295,264 bytes |
| sha256 | `ecc4d5b8107fc219e23c494b2d107552137637b6c6002ee713e0ba8af7fa2755` |

The repository also publishes `MXFP4_MOE` (7,029,537,056 bytes) and `Q8_0`
(12,925,417,760 bytes) — the two quantisations already on this machine, whose
sizes match the repository's listing exactly. Same publisher, wrong quant. The
`mtp/` files carry their own digests and are a different artifact again.

The revision, not the file name, is the pin: `Q4_K_M` names a quantisation, and
the file under that name can be replaced at the repository's head.

```sh
curl -sS "https://huggingface.co/api/models/JetBrains/Mellum2.1-12B-A2.5B-Thinking-GGUF/tree/main?recursive=1" |
  jq -r '.[] | select(.path=="Mellum2.1-12B-A2.5B-Thinking-Q4_K_M.gguf") |
         "\(.size) \(.lfs.oid)"'
```

## What the source held, and what this card holds instead

The source's llama path is looser than this card. `scripts/baseline/pins.env` at
`0e4a9b68` pins the image by a bare tag, `vastai/llama-cpp:b11985-mix-c116c32-cuda-12.9`
(line 23), and the GGUF by repository and quant alone (lines 24–25): no revision,
no hash. The only `@sha256` in that file belongs to the vLLM image (line 19), which
is a different serving stack — so the container-digest shape was vLLM's, and it was
never the llama batch's to mirror.

That turns these five values from a shape copied into a gap closed: the card pins
the file the source's selector left loose. A rented llama host, when one is
qualified, takes this shape and adds an `@sha256` image digest — tighter than the
bare tag the source settled for.

*(Andre, 2026-11-22, reviewing this card.)*

## The settings

Quoted from the source at `0e4a9b68`, not newly measured:

| Where | Value |
| --- | --- |
| `pyproject.toml` `[tool.mellum].model` | `JetBrains/Mellum2.1-12B-A2.5B-Thinking-GGUF:Q4_K_M` |
| `pyproject.toml` `[tool.mellum].context` | 50000 |
| `pyproject.toml` `[tool.mellum].max_tokens` | 16384 |
| `pyproject.toml` `[tool.mellum].temperature` | 1.0 |
| `pyproject.toml` `[tool.mellum].top_p` | 0.95 |
| `pyproject.toml` `[tool.mellum].top_k` | 20 |
| `scripts/backend.py` `HOST`, `PORT` | `127.0.0.1`, `8001` |
| `scripts/backend.py` `ALIAS` | `Mellum2.1-12B-A2.5B-Thinking` |

`scripts/backend.py` also carries `MIN_BUILD = 9482` and `TESTED_BUILD = 11669`;
b12066 is past both, which is why b12066 can be the documented build at all.

## The serve command

The source's own argv, from `serve_argv` in `scripts/backend.py`:

```sh
llama-server -hf JetBrains/Mellum2.1-12B-A2.5B-Thinking-GGUF:Q4_K_M \
  -a Mellum2.1-12B-A2.5B-Thinking --host 127.0.0.1 --port 8001 \
  -c 50000 -np 1 --jinja -fa auto -b 512 -ub 512 -ctk q8_0 -ctv q8_0
```

The documented command keeps those flags and replaces `-hf` with an explicit
`-m` path to the verified file. `-hf` resolves a repository at its head, which is
a selector rather than a content pin — the [rig note](2026-11-16-reference-rig.md)
names that as the risk this card exists to close. Everything else is preserved.

- **Offload:** the source passes no `-ngl`, leaving llama.cpp's `--fit` to split
  the model against free device memory, and sets `-c` so `--fit` cannot shrink
  the context. The macOS artifact builds with Metal, so the split is across
  unified memory. The rented-CUDA baseline recorded `BASELINE_LLAMA_NGL=999` in
  `scripts/baseline/pins.env`; that is a different platform's record, not this
  card's.
- **Flags are confirmed, not assumed:** P4.2 reads b12066's own `--help` and
  records any flag this build spells or defaults differently.

## What the pinned command actually did (P4.2, 2026-11-24)

The bytes landed and the command ran. Both digests were checked **before**
anything executed: the archive matched `9090531…09a19` at 16,548,566 bytes, the
GGUF matched `ecc4d5b8…fa2755` at 8,071,295,264 bytes, and
`llama-server --version` reported `build 12066, commit 713319e28`.

Startup reported the allocation below, read from the server's own log at
`-lv 4` — the default verbosity does not print it:

| Buffer | Size |
| --- | --- |
| `CPU_Mapped` model buffer | 121.50 MiB |
| `MTL0_Mapped` model buffer | 177.20 MiB |
| `MTL0_Mapped` model buffer | 7,395.27 MiB |
| `MTL0` KV cache | 364.44 MiB |
| `MTL0` KV cache | 33.47 MiB |
| `MTL0` compute buffer | 199.01 MiB |
| `CPU` compute buffer | 68.53 MiB |

`n_ctx = 50176`, model type `12B.A2.5B`, file type `Q4_K - Medium`.

Two observations about memory, and they disagree on purpose:

- The process's **own footprint** peaked at 634 MB (`footprint -p`), and sat near
  8.0 GiB resident (`ps -o rss`) while serving.
- The gap is the GGUF: it is mapped from the file rather than read into private
  memory, so most of those 8 GiB are clean, file-backed pages the system can drop
  when the model is idle.

So the number a reader needs is not "500 MB" and not "8 GB" alone: the model needs
roughly 8 GiB of memory reachable, and the server's private working set is under a
gigabyte on top of it.

## What this card does not establish

- Nothing here says how fast, or how good: no rate, no latency, no grade.
- Nothing about Linux, CUDA, Windows or the `macos-x64` build. Those stay
  unverified until someone runs them.
- No historical measurement transfers. Historical baselines used b11985 and
  build 11669; matching a model name does not match a stack.

## Reopens when

- P4.2 finds b12066 cannot load the pinned file, or a flag behaves differently.
- The Hugging Face revision stops resolving, or a published digest changes.
- Another platform is exercised, which earns its own card rather than a sentence
  here.

## The shape of the next card

A host card carries five things: the platform and its reported hardware; the
server build by source commit *and* binary digest; the weights by revision,
size and digest; the settings and where they were quoted from; and the whole
command. Rented hosts copy this shape, and a batch that cannot fill it in does
not qualify as a comparable host.
