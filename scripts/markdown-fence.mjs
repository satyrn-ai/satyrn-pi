// CommonMark-style fence scanning shared by the document checks: up to three
// leading spaces, backtick or tilde, closing delimiter of the same character at
// least as long as the opener.
const FENCE = /^ {0,3}(`{3,}|~{3,})(.*)$/;

export function scanFences(text) {
  const lines = text.split("\n");
  const inFence = new Array(lines.length).fill(false);
  const delimiter = new Array(lines.length).fill(false);
  let open = null;
  lines.forEach((line, index) => {
    const match = FENCE.exec(line);
    if (!open) {
      if (match && !(match[1][0] === "`" && match[2].includes("`"))) {
        open = { char: match[1][0], length: match[1].length };
        inFence[index] = true;
        delimiter[index] = true;
      }
      return;
    }
    inFence[index] = true;
    if (
      match &&
      match[1][0] === open.char &&
      match[1].length >= open.length &&
      match[2].trim() === ""
    ) {
      delimiter[index] = true;
      open = null;
    }
  });
  return { inFence, delimiter };
}
