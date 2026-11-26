---
title: Getting Started
---

# Getting Started

Run **Mellum 2.1** on your own machine and get an answer back from it. One
download of about 8 GB, one command to serve it, and no repository to clone.

This page stops where the software stops. Satyrn Pi's worker — the part that
hands this model a bounded task inside Pi — is not published yet; when it is, it
gets its own section here. The [roadmap](https://github.com/satyrn-ai/satyrn-pi/blob/main/ROADMAP.md)
says what is being built.

## What you need

- An Apple silicon Mac. This page covers `arm64` only; Linux, CUDA and Windows are
  untested, and their builds use different flags.
- About 8 GB of free disk for the weights, and 16 GB of memory. The weights are
  8.1 GB of mapped file, so the server's own footprint reads as under a gigabyte
  while the machine still has to hold the file: `ps` reports about 8 GB resident.
  A 16 GB laptop that ran it used 8.5 GB and swapped, so treat 16 GB as the minimum
  rather than a comfortable margin.
- A terminal, and `curl`.

Paths below are examples. This page uses `~/.local/share/satyrn-llama` for the
server and `~/models` for the weights, because that is where the recorded setup
put them; any directory you own works if you change both.

## 1. Get the server

Satyrn Pi records one llama.cpp build, `b12066` — source commit
`713319e28492d319b81e49646151f6bbdb9d4551` — and this page installs that build
beside whatever else you already have rather than replacing it.

```sh
mkdir -p ~/.local/share/satyrn-llama/b12066
cd ~/.local/share/satyrn-llama/b12066
curl -sSL -O https://github.com/ggml-org/llama.cpp/releases/download/b12066/llama-b12066-bin-macos-arm64.tar.gz
shasum -a 256 llama-b12066-bin-macos-arm64.tar.gz
```

That should print `909053143be864f6b2c45b45e140575904fde163978d33cea53f30f318e09a19`,
for a file of 16,548,566 bytes. If it prints anything else, stop: the download is
not the build this page describes.

```sh
tar xzf llama-b12066-bin-macos-arm64.tar.gz
./llama-b12066/llama-server --version
```

Expect `version: 0.8.0-dev (build 12066, commit 713319e28)`.

**If `--version` reports a different build number**, you are running a different
`llama-server` — most often Homebrew's, which is likely on your `PATH` and newer
than this. Every command below names the binary by its full path so that this
cannot happen by accident.

**If macOS refuses to run an unsigned file** — *"cannot be opened because the
developer cannot be verified"* — the download picked up a quarantine flag, which
happens when a browser saves it. Clear it, or unzip from the terminal:

```sh
xattr -d com.apple.quarantine llama-b12066-bin-macos-arm64.tar.gz
```

## 2. Get the weights

The file is Q4_K_M, and it is fetched at a pinned revision. The quantisation name
alone is not a pin: the file behind that name can be replaced. Create the
directory first — `curl -o` will not create it, and the download fails on the
line you just copied if it is missing.

```sh
mkdir -p ~/models
curl -sSL -o ~/models/Mellum2.1-12B-A2.5B-Thinking-Q4_K_M.gguf \
  https://huggingface.co/JetBrains/Mellum2.1-12B-A2.5B-Thinking-GGUF/resolve/4159d684ffdb09ba89dc2a58feb3e75c54eef036/Mellum2.1-12B-A2.5B-Thinking-Q4_K_M.gguf
shasum -a 256 ~/models/Mellum2.1-12B-A2.5B-Thinking-Q4_K_M.gguf
```

Expect `ecc4d5b8107fc219e23c494b2d107552137637b6c6002ee713e0ba8af7fa2755`, for a
file of 8,071,295,264 bytes. If those two numbers do not match, the file is not
the one the rest of this page was recorded against.

## 3. Serve it

**First, check the port.** Something else may already be answering on 8001:

```sh
lsof -nP -iTCP:8001 -sTCP:LISTEN
```

If anything prints, stop that program or pick a different port and use it
consistently. On a Mac this is often another inference app — and some of them
serve a *different* Mellum under the same model name, which produces answers that
look exactly like the ones below. This is the failure most likely to waste your
afternoon.

```sh
~/.local/share/satyrn-llama/b12066/llama-b12066/llama-server \
  -m ~/models/Mellum2.1-12B-A2.5B-Thinking-Q4_K_M.gguf \
  -a Mellum2.1-12B-A2.5B-Thinking --host 127.0.0.1 --port 8001 \
  -c 50000 -np 1 --jinja -fa auto -b 512 -ub 512 -ctk q8_0 -ctv q8_0
```

Those flags are the recorded configuration, not a tuning exercise: 50,000 tokens
of context, one slot, the model's own chat template, and an 8-bit KV cache. Leave
the terminal open. It is ready when it prints `listening on
http://127.0.0.1:8001`, and `curl -s http://127.0.0.1:8001/health` answers
`{"status":"ok"}`. On the recorded machine that took about 23 seconds.

## 4. Check that it is this build

An answer on its own proves nothing, because any server on that port will answer.
Two things together do:

```sh
curl -s http://127.0.0.1:8001/v1/models
```

The listing should name `Mellum2.1-12B-A2.5B-Thinking`. Then read the line your
server printed when it started:

```
load_model: loading model '/Users/you/models/Mellum2.1-12B-A2.5B-Thinking-Q4_K_M.gguf'
listening on http://127.0.0.1:8001
```

If `--version` said `build 12066` and this line names the file whose sha256 you
just checked, then the reply below comes from the configuration this page
describes. If the path is somewhere else, or the build number differs, it does not
— and the answer would still have looked fine.

## 5. Ask it something

```sh
curl -s http://127.0.0.1:8001/v1/chat/completions \
  -H 'Content-Type: application/json' \
  -d '{"model":"Mellum2.1-12B-A2.5B-Thinking","messages":[{"role":"user","content":"In one sentence, what does a bounded coding worker do?"}],"max_tokens":1024,"temperature":1.0,"top_p":0.95,"top_k":20}'
```

You get JSON with a `reasoning_content` field and a `content` field: the model
thinks first, then answers. The thinking is billed against the same
`max_tokens`, so leave room for the answer — at 256 the model sometimes spent
the whole budget thinking and returned `finish_reason: "length"` with an empty
`content`. If you see that, raise `max_tokens` rather than doubting the server.
When you are done, `Ctrl-C` in the serving terminal, and
`lsof -nP -iTCP:8001 -sTCP:LISTEN` should print nothing.

## What you have now

A model answering on your machine, at a pinned build and a pinned file, and enough
evidence to know it is that one. What is missing is the part that makes it a
worker: Satyrn Pi's contribution arrives with the [roadmap](https://github.com/satyrn-ai/satyrn-pi/blob/main/ROADMAP.md)'s
worker and eval cycles.

The [glossary](glossary.md) defines the project's words — *worker*, *task*,
*remedy* — as they are used here.
