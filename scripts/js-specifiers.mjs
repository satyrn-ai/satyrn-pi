// Shared JavaScript specifier extraction. Comments are blanked (preserving
// length and newlines) so matches never come from comments and line numbers stay
// aligned with the original text.

const REGEX_PRECEDERS = new Set(["(", "[", "{", "=", ",", ";", ":", "!", "&", "|", "?", "+", "-", "*", "%", "^", "~", "<", ">"]);
const REGEX_KEYWORDS = new Set([
  "return", "typeof", "instanceof", "in", "of", "new", "delete", "void",
  "throw", "case", "do", "else", "yield", "await",
]);

const regexAllowed = (lastChar, lastWord) =>
  lastChar === "" || REGEX_PRECEDERS.has(lastChar) || REGEX_KEYWORDS.has(lastWord);

export function stripJsComments(text) {
  let out = "";
  let quote = null;
  let lastChar = "";
  let lastWord = "";
  let index = 0;
  while (index < text.length) {
    const char = text[index];
    const next = text[index + 1];
    if (quote) {
      out += char;
      if (char === "\\") {
        out += next ?? "";
        index += 2;
        continue;
      }
      if (char === quote) quote = null;
      index += 1;
      continue;
    }
    if (char === '"' || char === "'" || char === "`") {
      quote = char;
      out += char;
      index += 1;
      continue;
    }
    if (char === "/" && next === "/") {
      while (index < text.length && text[index] !== "\n") {
        out += " ";
        index += 1;
      }
      continue;
    }
    if (char === "/" && next === "*") {
      out += "  ";
      index += 2;
      while (index < text.length && !(text[index] === "*" && text[index + 1] === "/")) {
        out += text[index] === "\n" ? "\n" : " ";
        index += 1;
      }
      if (index < text.length) {
        out += "  ";
        index += 2;
      }
      continue;
    }
    if (char === "/" && regexAllowed(lastChar, lastWord)) {
      out += char;
      index += 1;
      let inClass = false;
      while (index < text.length) {
        const current = text[index];
        if (current === "\\") {
          out += current + (text[index + 1] ?? "");
          index += 2;
          continue;
        }
        out += current;
        if (current === "[") inClass = true;
        else if (current === "]") inClass = false;
        else if (current === "/" && !inClass) {
          index += 1;
          break;
        }
        index += 1;
      }
      while (index < text.length && /[a-z]/i.test(text[index])) {
        out += text[index];
        index += 1;
      }
      lastChar = "";
      lastWord = "";
      continue;
    }
    out += char;
    if (!/\s/.test(char)) lastChar = char;
    if (/[A-Za-z_$]/.test(char)) lastWord += char;
    else if (!/\s/.test(char)) lastWord = "";
    index += 1;
  }
  return out;
}

const SPECIFIER = /(?:\bfrom\s*|\bimport\s*|\brequire\s*\(\s*|\bimport\s*\(\s*)["']([^"']+)["']/g;

export function findSpecifiers(text) {
  const clean = stripJsComments(text);
  return [...clean.matchAll(SPECIFIER)].map((match) => ({
    specifier: match[1],
    index: match.index,
  }));
}

export function lineOf(text, index) {
  return text.slice(0, index).split("\n").length;
}
