// Verificación en navegador real (Chrome headless vía CDP, sin dependencias).
// Reporta violaciones de CSP, errores JS, peticiones fallidas/404 y guarda capturas.
// Uso: node tools/check-browser.mjs http://127.0.0.1:8765 / /store/ /producto/molde-poste/
import { spawn } from "node:child_process";
import { mkdtempSync, writeFileSync, mkdirSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const [base, ...paths] = process.argv.slice(2);
// Por defecto Chrome Canary (motor más reciente); CHROME_PATH lo reemplaza.
const CHROME = process.env.CHROME_PATH ||
  join(process.env.LOCALAPPDATA || "", "Google", "Chrome SxS", "Application", "chrome.exe");
const port = 9300 + Math.floor(Math.random() * 500);
const profile = mkdtempSync(join(tmpdir(), "cvm-chrome-"));
const proc = spawn(CHROME, ["--headless=new", `--remote-debugging-port=${port}`,
  `--user-data-dir=${profile}`, "--no-first-run", "--window-size=1366,900", "about:blank"],
  { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let wsUrl;
for (let i = 0; i < 50 && !wsUrl; i++) {
  try {
    const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
    wsUrl = list.find((t) => t.type === "page")?.webSocketDebuggerUrl;
  } catch { /* esperando */ }
  if (!wsUrl) await sleep(200);
}
const ws = new WebSocket(wsUrl);
await new Promise((r) => ws.addEventListener("open", r));
let id = 0; const pending = new Map(); const events = [];
ws.addEventListener("message", (m) => {
  const msg = JSON.parse(m.data);
  if (msg.id && pending.has(msg.id)) { pending.get(msg.id)(msg.result); pending.delete(msg.id); }
  else if (msg.method) events.push(msg);
});
const send = (method, params = {}) => new Promise((r) => {
  const i = ++id; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params }));
});
for (const d of ["Page", "Runtime", "Log", "Network", "Audits"]) await send(`${d}.enable`);
// MOBILE=1 emula un teléfono (390x844, DPR 3, táctil)
const mobile = process.env.MOBILE === "1";
if (mobile) {
  await send("Emulation.setDeviceMetricsOverride",
    { width: 390, height: 844, deviceScaleFactor: 3, mobile: true });
  await send("Emulation.setTouchEmulationEnabled", { enabled: true });
}

mkdirSync("screenshots", { recursive: true });
let problems = 0;
for (const p of paths) {
  events.length = 0;
  await send("Page.navigate", { url: base + p });
  await sleep(5000);
  const urls = new Map();
  const issues = [];
  for (const e of events) {
    if (e.method === "Network.requestWillBeSent") urls.set(e.params.requestId, e.params.request.url);
    if (e.method === "Network.responseReceived" && e.params.response.status >= 400)
      issues.push(`HTTP ${e.params.response.status} ${e.params.response.url}`);
    if (e.method === "Network.loadingFailed" && !e.params.canceled)
      issues.push(`FAILED ${e.params.blockedReason || e.params.errorText} ${urls.get(e.params.requestId)}`);
    if (e.method === "Runtime.exceptionThrown")
      issues.push(`JS ${e.params.exceptionDetails.exception?.description?.split("\n")[0] || e.params.exceptionDetails.text}`);
    if (e.method === "Log.entryAdded" && e.params.entry.level === "error")
      issues.push(`LOG ${e.params.entry.text.slice(0, 220)}`);
    if (e.method === "Runtime.consoleAPICalled" && e.params.type === "error")
      issues.push(`CONSOLE ${JSON.stringify(e.params.args.map((a) => a.value ?? a.description)).slice(0, 220)}`);
    if (e.method === "Audits.issueAdded") {
      const d = e.params.issue.details;
      const csp = d.contentSecurityPolicyIssueDetails;
      if (csp) issues.push(`CSP ${csp.violatedDirective} ${csp.blockedURL || csp.contentSecurityPolicyViolationType}`);
    }
  }
  const uniq = [...new Set(issues)];
  problems += uniq.length;
  console.log(`\n=== ${p}  (${uniq.length} problemas)`);
  uniq.slice(0, 40).forEach((x) => console.log("  " + x));
  const shot = await send("Page.captureScreenshot", { format: "png" });
  writeFileSync(join("screenshots", (mobile ? "m" : "") + (p.replace(/\W+/g, "_") || "home") + ".png"),
    Buffer.from(shot.data, "base64"));
}
ws.close(); proc.kill();
try { rmSync(profile, { recursive: true, force: true }); } catch { /* chrome aún liberando */ }
console.log(`\nTotal: ${problems} problemas`);
process.exit(problems ? 1 : 0);
