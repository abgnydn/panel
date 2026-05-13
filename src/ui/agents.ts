/**
 * Shared agent display registry — name, tagline, tint, inline SVG icon.
 *
 * Every scene imports this so agent identity stays consistent and the
 * upgrade from emoji → SVG icon is in one place.
 */
import { ICONS } from "./icons";

export type AgentId =
  | "lawyer"
  | "translator"
  | "regulator"
  | "peer_advocate"
  | "triage"
  | "negotiator";

export type AgentDisplay = {
  id: AgentId;
  name: string;
  tagline: string;
  tint: string;
  /** Inline SVG, already pre-classed via icon() helper if needed. */
  iconSvg: string;
};

const TINTS: Record<AgentId, string> = {
  lawyer:        "var(--agent-lawyer)",
  translator:    "var(--agent-translator)",
  regulator:     "var(--agent-regulator)",
  peer_advocate: "var(--agent-peer)",
  triage:        "var(--agent-triage)",
  negotiator:    "var(--agent-negotiator)",
};

export const AGENTS: AgentDisplay[] = [
  { id: "lawyer",        name: "Lawyer",         tagline: "Local labor law",            tint: TINTS.lawyer,        iconSvg: ICONS.lawyer },
  { id: "translator",    name: "Translator",     tagline: "Plain language in your L1",  tint: TINTS.translator,    iconSvg: ICONS.translator },
  { id: "regulator",     name: "Regulator",      tagline: "ILO / ASEAN standards",      tint: TINTS.regulator,     iconSvg: ICONS.regulator },
  { id: "peer_advocate", name: "Peer Advocate",  tagline: "Similar past cases",         tint: TINTS.peer_advocate, iconSvg: ICONS.peer_advocate },
  { id: "triage",        name: "Triage",         tagline: "Urgency & contacts",         tint: TINTS.triage,        iconSvg: ICONS.triage },
  { id: "negotiator",    name: "Negotiator",     tagline: "What to say before signing", tint: TINTS.negotiator,    iconSvg: ICONS.negotiator },
];

export const AGENT_BY_ID: Record<AgentId, AgentDisplay> =
  AGENTS.reduce((acc, a) => { acc[a.id] = a; return acc; }, {} as Record<AgentId, AgentDisplay>);

/** Pre-classed icon HTML for use in 36×36 avatar containers. */
export function agentIconHtml(id: AgentId, sizeClass: "icon-sm" | "icon-md" | "icon-lg" = "icon-md"): string {
  const a = AGENT_BY_ID[id];
  if (!a) return "";
  return a.iconSvg.replace("<svg", `<svg class="${sizeClass}" aria-hidden="true"`);
}
