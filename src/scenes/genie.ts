/**
 * Genie chat scene — "Ask the lawbook".
 *
 * Multi-turn conversation against the Databricks Genie Space. Each turn
 * returns:
 *   - The natural-language answer
 *   - The SQL Genie generated (rendered as a collapsible block)
 *   - The result table (when there is one)
 *   - 3 AI-suggested follow-up questions (rendered as chips above the input)
 *
 * State lives in this scene's closure (conversation_id + messages array).
 * Refreshing the page starts a new conversation.
 */
import { gsap } from "gsap";

import type { SceneCtx } from "./router";
import { icon } from "../ui/icons";

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "";

type Turn = {
  role: "user" | "genie";
  text: string;
  sql?: string;
  columns?: string[];
  rows?: any[][];
  latency_ms?: number;
};

type ChatState = {
  conversation_id?: string;
  messages: Turn[];
  suggestions: string[];
  loading: boolean;
};

export async function renderGenieChat(ctx: SceneCtx): Promise<void> {
  const { root, goto } = ctx;
  const state: ChatState = { messages: [], suggestions: [], loading: false };

  root.innerHTML = `
    <section class="genie">
      <header class="rec-head">
        <div class="eyebrow"><span class="dot"></span>Genie · Ask the lawbook anything</div>
        <h1 class="display-heading">Talk to your <em>case file</em></h1>
        <p class="lede">Natural-language questions against destination-country
          labor codes, ILO conventions, the case archive, and the embassy
          directory. Each answer suggests three follow-ups — <em>the
          conversation continues</em>.</p>
      </header>

      <div class="chat-thread" id="thread"></div>

      <div class="chat-suggestions" id="suggestions" hidden></div>

      <form class="chat-input" id="form">
        <input type="text" id="q" placeholder="Ask a question…"
               autocomplete="off" />
        <button class="cta" id="send" type="submit">
          <span>Ask</span>${icon("arrow_right", "icon-sm")}
        </button>
      </form>

      <footer class="delib-foot">
        <button class="cta-ghost" id="back">${icon("arrow_left", "icon-sm")}<span>Back to recommendation</span></button>
      </footer>
    </section>
  `;

  const thread = root.querySelector<HTMLDivElement>("#thread")!;
  const sugBox = root.querySelector<HTMLDivElement>("#suggestions")!;
  const form = root.querySelector<HTMLFormElement>("#form")!;
  const input = root.querySelector<HTMLInputElement>("#q")!;
  const send = root.querySelector<HTMLButtonElement>("#send")!;

  root.querySelector<HTMLButtonElement>("#back")!
    .addEventListener("click", () => goto("recommendation"));

  // ---- Seed suggestions ---------------------------------------------------
  try {
    const seedRes = await fetch(`${API_BASE}/api/genie/seed-questions`);
    if (seedRes.ok) {
      const seed = await seedRes.json();
      state.suggestions = seed.questions || [];
      renderSuggestions();
    }
  } catch { /* offline / not on Databricks — silent */ }

  // ---- Submit handler -----------------------------------------------------
  async function submit(question: string) {
    if (!question.trim() || state.loading) return;
    state.loading = true;
    send.disabled = true;
    input.disabled = true;

    state.messages.push({ role: "user", text: question });
    renderThread();
    appendThinking();
    input.value = "";
    state.suggestions = [];
    renderSuggestions();

    try {
      const res = await fetch(`${API_BASE}/api/genie/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question,
          conversation_id: state.conversation_id,
        }),
      });
      removeThinking();
      if (!res.ok) {
        const errText = await res.text().catch(() => "");
        state.messages.push({
          role: "genie",
          text: `(Genie unreachable — HTTP ${res.status})${errText ? "\n" + errText.slice(0, 200) : ""}`,
        });
      } else {
        const data = await res.json();
        state.conversation_id = data.conversation_id;
        state.messages.push({
          role: "genie",
          text: data.text || "(no answer)",
          sql: data.sql,
          columns: data.columns,
          rows: data.rows,
          latency_ms: data.latency_ms,
        });
        state.suggestions = data.suggested_questions || [];
      }
    } catch (e) {
      removeThinking();
      state.messages.push({
        role: "genie",
        text: `(Genie offline — running locally without the FastAPI server?)\n${(e as Error).message}`,
      });
    } finally {
      state.loading = false;
      send.disabled = false;
      input.disabled = false;
      renderThread();
      renderSuggestions();
      thread.scrollTop = thread.scrollHeight;
      input.focus();
    }
  }

  form.addEventListener("submit", (e) => {
    e.preventDefault();
    submit(input.value);
  });

  sugBox.addEventListener("click", (e) => {
    const t = e.target as HTMLElement;
    const chip = t.closest<HTMLButtonElement>(".chat-chip");
    if (chip?.dataset.q) submit(chip.dataset.q);
  });

  // ---- Renderers ----------------------------------------------------------
  function renderThread() {
    thread.innerHTML = state.messages.map(turnHtml).join("");
    gsap.fromTo(".chat-bubble:last-child",
      { opacity: 0, y: 12 }, { opacity: 1, y: 0, duration: 0.35, ease: "power3.out", clearProps: "transform" });
  }

  function renderSuggestions() {
    if (!state.suggestions.length) {
      sugBox.hidden = true;
      return;
    }
    sugBox.hidden = false;
    sugBox.innerHTML = `
      <div class="chat-sug-label">${state.messages.length === 0 ? "Try one of these" : "Continue the conversation"}</div>
      <div class="chat-sug-row">
        ${state.suggestions.map((q) => `
          <button class="chat-chip" data-q="${escapeAttr(q)}">${escape(q)}</button>
        `).join("")}
      </div>
    `;
  }

  function appendThinking() {
    const el = document.createElement("div");
    el.className = "chat-bubble chat-bubble-genie chat-thinking";
    el.id = "thinking";
    el.innerHTML = `<span class="chat-dot"></span><span class="chat-dot"></span><span class="chat-dot"></span>`;
    thread.appendChild(el);
    thread.scrollTop = thread.scrollHeight;
  }

  function removeThinking() {
    thread.querySelector("#thinking")?.remove();
  }

  // ---- Entrance ----------------------------------------------------------
  gsap.fromTo(".rec-head",     { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".chat-thread",  { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.6, delay: 0.2, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".chat-input",   { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5, delay: 0.4, ease: "power3.out", clearProps: "transform" });
}

function turnHtml(t: Turn): string {
  if (t.role === "user") {
    return `<div class="chat-bubble chat-bubble-user">${escape(t.text)}</div>`;
  }
  let inner = `<div class="chat-bubble-text">${escapeMultiline(t.text)}</div>`;
  if (t.sql) {
    inner += `<details class="chat-sql"><summary>SQL · ${
      t.rows?.length ?? 0
    } rows · ${
      t.latency_ms ? (t.latency_ms / 1000).toFixed(1) + "s" : ""
    }</summary><pre><code>${escape(t.sql)}</code></pre></details>`;
  }
  if (t.columns?.length && t.rows?.length) {
    inner += tableHtml(t.columns, t.rows);
  }
  return `<div class="chat-bubble chat-bubble-genie">${inner}</div>`;
}

function tableHtml(columns: string[], rows: any[][]): string {
  const head = `<tr>${columns.map((c) => `<th>${escape(c)}</th>`).join("")}</tr>`;
  const body = rows.slice(0, 20).map((r) =>
    `<tr>${r.map((cell) => `<td>${escape(String(cell ?? ""))}</td>`).join("")}</tr>`,
  ).join("");
  const more = rows.length > 20 ? `<div class="chat-table-more">…${rows.length - 20} more rows</div>` : "";
  return `<div class="chat-table"><table>${head}${body}</table>${more}</div>`;
}

function escape(s: string): string {
  return s
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}
function escapeAttr(s: string): string {
  return escape(s).replace(/"/g, "&quot;");
}
function escapeMultiline(s: string): string {
  return escape(s).replace(/\n/g, "<br>");
}
