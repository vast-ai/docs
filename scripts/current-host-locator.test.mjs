/** Exact source-locator regressions. Synthetic DOM indexes model the retained
 * Volume Offers browser failures; these checks do not establish Host behavior. */
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../review-server.mjs', import.meta.url), 'utf8');
const locator = source.slice(source.indexOf('  function claimWording(value) {'), source.indexOf('  var claimSectionFilter = null;'));
const fence = '```';
test('duplicate checking summaries preserve word boundaries and code punctuation', () => {
  const expression = source.match(/var summary = (redacted \|\| [^\n]+)\n/)[1];
  const differs = (sourceSummary, checkingText, redacted = false) => vm.runInNewContext(expression, {sourceSummary, checkingText, redacted});
  assert.equal(differs('Use an account.', 'Use an account.'), false);
  assert.equal(differs('vastai command --foo bar', 'vastai command --foobar'), true);
  assert.equal(differs('vastai command --foo', 'vastai command —foo'), true);
  assert.equal(differs('Same', 'Same', true), true);
});
const cases = [
  { id: 'VOL-C21', before: 'You can publish GPU and volume offers together:',
    command: 'vastai list machine <machine-id> \\\n  --vol_size <capacity-gb> \\\n  --vol_price <usd-per-gb-month> \\\n  --end_date <date>',
    after: 'Set `--vol_size 0` when you do not want the machine listing to include a volume offer. Pass an explicit size and price so the advertised capacity is intentional.' },
  { id: 'VOL-C22', before: 'You can also publish storage separately:',
    command: 'vastai list volume <machine-id> \\\n  --size <capacity-gb> \\\n  --price_disk <usd-per-gb-month> \\\n  --end_date <date>', after: '' },
];

function fixture(item, renderedCommand = item.command, copies = 1) {
  const nodes = [], blocks = [];
  function append(text, code) {
    const block = { textContent: text, closest(selector) {
      if (selector === 'pre' || selector === 'pre,code') return code ? block : null;
      if (selector === 'li,[data-as="p"],p,tr') return code ? null : block;
      return null;
    } };
    const node = { data: text, parentElement: block, order: nodes.length + 1 };
    nodes.push(node); blocks.push(block);
  }
  for (let count = 0; count < copies; count++) {
    append(item.before + '\n\n', false);
    append(renderedCommand, true);
    if (item.after) append('\n\n' + item.after.replaceAll('`', ''), false);
  }
  const heading = { textContent: 'Publish Local Storage', tagName: 'H2', order: 0,
    compareDocumentPosition(other) { return other.order > this.order ? 4 : 2; } };
  const root = { contains: node => nodes.includes(node), querySelectorAll: () => [heading] };
  const document = { querySelector: () => root, createRange() { return {
    setStart(node, offset) { this.startContainer = node; this.startOffset = offset; },
    setEnd(node, offset) { this.endContainer = node; this.endOffset = offset; },
  }; } };
  const context = { document, Node: { DOCUMENT_POSITION_FOLLOWING: 4, DOCUMENT_POSITION_PRECEDING: 2 },
    normalizedHeadingText: text => String(text).trim(), root, index: { nodes: nodes.map(node => ({ node })) },
    passage: { text: item.before + '\n\n' + fence + 'bash\n' + item.command + '\n' + fence + (item.after ? '\n\n' + item.after : ''),
      section: 'Publish Local Storage', occurrence: 0, occurrences: 1 } };
  vm.createContext(context);
  vm.runInContext(locator + '\nvar wording = passageWording(passage);', context);
  return { context, run: () => vm.runInContext('matchSourcePassage(root, index, passage, wording)', context) };
}

for (const item of cases) test(`${item.id}: mixed prose and fenced command locate the exact complete code block`, () => {
  const { context, run } = fixture(item);
  assert.ok(context.wording.text.includes(item.command));
  assert.doesNotMatch(context.wording.text, /(?:^|\n)bash(?:\n|$)|```/);
  assert.equal(context.wording.fences.length, 1);
  const match = run();
  assert.equal(match.ranges?.length, 1, match.reason);
});

test('mixed fenced commands reject option typography drift and extra command suffixes', () => {
  for (const item of cases) {
    assert.equal(fixture(item, item.command.replace('--', '—')).run().ranges, undefined);
    assert.equal(fixture(item, item.command + ' --unexpected-option').run().ranges, undefined);
  }
});

test('mixed fenced passages retain exact section and source-occurrence gates', () => {
  const wrongSection = fixture(cases[0]);
  wrongSection.context.passage.section = 'Another Section';
  assert.equal(wrongSection.run().ranges, undefined);
  const duplicated = fixture(cases[1], cases[1].command, 2);
  assert.equal(duplicated.run().ranges, undefined);
  duplicated.context.passage.occurrences = 2;
  duplicated.context.passage.occurrence = 1;
  assert.equal(duplicated.run().ranges?.length, 1);
});

test('whole fenced commands still use their complete literal code-block rule', () => {
  const { context, run } = fixture({ ...cases[1], before: '', after: '' });
  context.passage.text = fence + 'bash\n' + cases[1].command + '\n' + fence;
  vm.runInContext('wording = passageWording(passage)', context);
  assert.equal(context.wording.code, true);
  assert.equal(run().ranges?.length, 1);
});
