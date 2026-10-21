# Run guide

## Playwright pattern for a project that already has it

Confirm first: `package.json` lists `playwright`, `node_modules/playwright` exists, and `node -e "require('playwright')"` succeeds from the project root. Do not run `npm install` or `npx playwright install` for QA.

Write the script in your scratch folder and load Playwright from the project:

```js
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const projectRoot = process.argv[2];
const outDir = process.argv[3];
const { chromium } = require(path.join(projectRoot, 'node_modules', 'playwright'));

(async () => {
  const browser = await chromium.launch({ headless: true /* add args from project environment notes */ });
  const page = await browser.newPage({ viewport: { width: 1200, height: 900 } });
  const consoleErrors = [];
  const failedRequests = [];
  page.on('pageerror', e => consoleErrors.push(e.message));
  page.on('console', m => { if (m.type() === 'error') consoleErrors.push(m.text()); });
  page.on('requestfailed', r => failedRequests.push(r.url()));
  page.on('response', r => { if (r.status() >= 400) failedRequests.push(r.status() + ' ' + r.url()); });
  try {
    const response = await page.goto(pathToFileURL(path.join(projectRoot, 'page.html')).href);
    // For http targets, check response && response.ok() before continuing.
    await page.screenshot({ path: path.join(outDir, 'j1-step0-initial.png'), fullPage: true });
    await page.locator('#some-button').click();
    const observed = await page.locator('#some-result').textContent();
    await page.screenshot({ path: path.join(outDir, 'j1-step1.png'), fullPage: true });
    console.log(JSON.stringify({ observed, consoleErrors, failedRequests }));
  } finally {
    await browser.close();
  }
})().catch(e => { console.error('ERROR', e.message); process.exitCode = 2; });
```

A missing local file makes `page.goto` throw; a missing http route usually returns 404. Both mean the journey is unavailable or failed, never pass. Exit code 2 above marks a tool or environment error so you can tell it apart from a failed expectation.

Choose selectors from the page's ids, roles or visible text. Read the page source if needed. Take a screenshot after each step that changes visible state.

## Viewports

Use the sizes the journey names. Otherwise use 1200x900 for desktop and 390x844 for mobile. For layout checks, compare `document.documentElement.scrollWidth` with `clientWidth` to detect horizontal overflow.

## Report format

```markdown
| Journey | State | Expected | Observed | Evidence |
| --- | --- | --- | --- | --- |
| J1 Lost reply and retry | pass | left 2, right 1 | left 2, right 1 | shots/j1-step2.png |

Coverage: Chromium <version>, headless, 1200x900 and 390x844.
Not covered: Firefox, WebKit, real devices, screen readers, server behavior.
Console errors: none. Failed requests and HTTP errors: none.
```

Under each journey, add its steps:

```markdown
#### J1 steps
| Step | Action | Expected | Observed | Screenshot |
| --- | --- | --- | --- | --- |
| 1 | Open page | both counts 0 | both counts 0 | shots/j1-step1.png |
| 2 | Click "1. Save, but lose the reply" | both counts 1 | both counts 1 | shots/j1-step2.png |
```

## Scoped fix retest

Before editing, save the failing screenshot and observed values. After the fix, rerun the same script for the failed journey and for journeys that use the changed element. Show both results side by side. List changed files with `git diff --stat` when the project uses Git.
