// Мінімальний DOM для перевірки скриптів без браузера (лише для тестів).
// Вхід (stdin, JSON): {code, elements, scenario}. Вихід (stdout): JSON-результат сценарію.
"use strict";
const vm = require("vm");

class ClassList {
  constructor() { this.set = new Set(); }
  add(...c) { c.forEach((x) => this.set.add(x)); }
  remove(...c) { c.forEach((x) => this.set.delete(x)); }
  contains(c) { return this.set.has(c); }
  toggle(c, force) {
    const want = force === undefined ? !this.set.has(c) : !!force;
    if (want) this.set.add(c); else this.set.delete(c);
    return want;
  }
  toString() { return [...this.set].join(" "); }
}

function compound(sel) {
  const m = sel.match(/^([a-zA-Z][a-zA-Z0-9-]*)?(#[\w-]+)?((?:\.[\w-]+)*)((?:\[[\w-]+(?:=[^\]]+)?\])*)$/);
  if (!m) throw new Error("Тестовий DOM не підтримує селектор: " + sel + " (використайте #id, .клас, тег або [атрибут])");
  return {
    tag: m[1] ? m[1].toUpperCase() : null,
    id: m[2] ? m[2].slice(1) : null,
    classes: m[3] ? m[3].split(".").filter(Boolean) : [],
    attrs: (m[4].match(/\[[^\]]+\]/g) || []).map((a) => a.slice(1, -1).split("=")),
  };
}

class Element {
  constructor(doc, spec) {
    this.doc = doc;
    this.tagName = (spec.tag || "div").toUpperCase();
    this.attrs = Object.assign({}, spec.attrs || {});
    if (spec.id) this.attrs.id = spec.id;
    this.classList = new ClassList();
    (spec.classes || []).forEach((c) => this.classList.add(c));
    this.listeners = {};
    this.children = [];
    this.parentNode = null;
    this.textContent = spec.text || "";
    this.value = spec.value || "";
    this.hidden = false;
    this.style = {};
    this.dataset = {};
  }
  get id() { return this.attrs.id || ""; }
  set id(v) { this.attrs.id = String(v); }
  get className() { return this.classList.toString(); }
  set className(v) { this.classList = new ClassList(); String(v).split(/\s+/).filter(Boolean).forEach((c) => this.classList.add(c)); }
  setAttribute(k, v) { this.attrs[k] = String(v); }
  getAttribute(k) { return Object.prototype.hasOwnProperty.call(this.attrs, k) ? this.attrs[k] : null; }
  hasAttribute(k) { return Object.prototype.hasOwnProperty.call(this.attrs, k); }
  removeAttribute(k) { delete this.attrs[k]; }
  addEventListener(t, f) { (this.listeners[t] = this.listeners[t] || []).push(f); }
  removeEventListener(t, f) { this.listeners[t] = (this.listeners[t] || []).filter((x) => x !== f); }
  appendChild(c) { this.children.push(c); c.parentNode = this; this.doc.created.push(c); return c; }
  append(...nodes) { nodes.forEach((n) => this.appendChild(typeof n === "string" ? this.doc.createTextNode(n) : n)); }
  matches(sel) {
    return sel.split(",").some((part) => {
      const c = compound(part.trim());
      if (c.tag && c.tag !== this.tagName) return false;
      if (c.id && c.id !== this.id) return false;
      if (!c.classes.every((x) => this.classList.contains(x))) return false;
      return c.attrs.every(([k, v]) => this.hasAttribute(k) && (v === undefined || this.getAttribute(k) === v.replace(/^["']|["']$/g, "")));
    });
  }
  closest(sel) { let e = this; while (e) { if (e.matches && e.matches(sel)) return e; e = e.parentNode; } return null; }
  all() { return this.children.flatMap((c) => [c, ...(c.all ? c.all() : [])]); }
  querySelectorAll(sel) { return this.all().filter((e) => e.matches && e.matches(sel)); }
  querySelector(sel) { return this.querySelectorAll(sel)[0] || null; }
  focus() { this.doc.activeElement = this; }
  click() { return this.doc.fire(this, "click", {}); }
  reset() { this.children.forEach((c) => { if (c.value !== undefined) c.value = ""; }); }
}

class Doc extends Element {
  constructor(specs) {
    super(null, { tag: "html" });
    this.doc = this;
    this.created = [];
    this.readyState = "interactive";
    this.body = new Element(this, { tag: "body" });
    this.nodes = specs.map((s) => new Element(this, s));
    this.nodes.forEach((n) => { this.body.children.push(n); n.parentNode = this.body; });
    this.children = [this.body];
    this.documentElement = this;
  }
  getElementById(id) { return this.nodes.find((n) => n.id === id) || this.created.find((n) => n.id === id) || null; }
  createElement(tag) { return new Element(this, { tag }); }
  createTextNode(text) { const e = new Element(this, { tag: "#text" }); e.textContent = String(text); return e; }
  fire(el, type, props) {
    const ev = Object.assign({ type, target: el, currentTarget: el, defaultPrevented: false, preventDefault() { this.defaultPrevented = true; }, stopPropagation() {} }, props || {});
    ev.target = (props && props.target) || el;
    const handlers = [...((el.listeners || {})[type] || [])];
    if (typeof el["on" + type] === "function") handlers.push(el["on" + type]);
    handlers.forEach((h) => h.call(el, ev));
    return ev;
  }
}

function main(input) {
  const doc = new Doc(input.elements || []);
  const alerts = [];
  const win = { listeners: {}, addEventListener(t, f) { (this.listeners[t] = this.listeners[t] || []).push(f); } };
  const sandbox = { document: doc, window: win, alert: (m) => alerts.push(String(m)), console: { log() {}, error() {}, warn() {} } };
  win.document = doc; win.alert = sandbox.alert;
  sandbox.globalThis = sandbox;
  const ctx = vm.createContext(sandbox);
  vm.runInContext(input.code, ctx, { timeout: 3000 });
  doc.fire(doc, "DOMContentLoaded", {});
  (win.listeners.load || []).forEach((h) => h({ type: "load" }));
  const env = {
    $: (id) => doc.getElementById(id),
    doc, alerts,
    fire: (el, type, props) => doc.fire(el, type, props),
    key: (key) => doc.fire(doc, "keydown", { key }),
    el: (spec) => new Element(doc, spec),
  };
  const out = new Function("env", input.scenario)(env);
  process.stdout.write(JSON.stringify(out === undefined ? null : out));
}

let raw = "";
process.stdin.on("data", (d) => (raw += d));
process.stdin.on("end", () => {
  try { main(JSON.parse(raw)); } catch (e) { process.stderr.write("JS-помилка: " + (e && e.message ? e.message : e) + "\n"); process.exit(2); }
});
