import json, sys

source, out = sys.argv[1], sys.argv[2]
text = open(source, encoding="utf-8").read()
code = """async (page) => {
  const editor = page.locator('.ProseMirror').first();
  await editor.click();
  await editor.evaluate((node, text) => {
    const data = new DataTransfer();
    data.setData('text/plain', text);
    node.dispatchEvent(new ClipboardEvent('paste', { clipboardData: data, bubbles: true, cancelable: true }));
  }, %s);
  return 'pasted ' + %d + ' characters';
}
""" % (json.dumps(text), len(text))
open(out, "w", encoding="utf-8").write(code)
print(f"wrote {out}")
