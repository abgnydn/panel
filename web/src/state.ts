/**
 * Lightweight cross-scene state.
 *
 * No framework. Just a typed object + a tiny event bus. Scenes read/write
 * directly; UI components subscribe via `state.on('change', ...)` when they
 * need re-render hooks.
 */
import type { Sample } from "./data/samples";
import type { PanelResult } from "./api/mock-result";

export type IntakeChoice = {
  sample?: Sample;
  file?: File;
  language: string;       // ISO L1 code: tl | id | en
  situation: string;
};

type StateShape = {
  intake: IntakeChoice;
  result?: PanelResult;       // populated by deliberation when backend returns
  source?: "live" | "mock";    // which path delivered the result
};

const state: StateShape = {
  intake: { language: "tl", situation: "" },
};

type Listener = (s: StateShape) => void;
const listeners = new Set<Listener>();

export const Store = {
  get(): StateShape {
    return state;
  },
  setIntake(patch: Partial<IntakeChoice>) {
    state.intake = { ...state.intake, ...patch };
    listeners.forEach((l) => l(state));
  },
  setResult(result: PanelResult, source: "live" | "mock") {
    state.result = result;
    state.source = source;
    listeners.forEach((l) => l(state));
  },
  subscribe(l: Listener): () => void {
    listeners.add(l);
    return () => listeners.delete(l);
  },
};
