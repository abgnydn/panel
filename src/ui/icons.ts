/**
 * Inline SVG icons — single-colour line style, 1.5 stroke.
 *
 * All icons inherit `currentColor`, so set the surrounding text color and
 * the icon follows. 24×24 viewBox, sized via CSS `width`/`height` or the
 * `.icon-sm` / `.icon-md` utility classes.
 */
export const ICONS = {
  // Agents
  lawyer: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 4v17M6 21h12M12 4l-7 4 3 6c.5 1 1.8 1.5 3 1s2-1.5 1.5-2.5L12 4zM12 4l7 4-3 6c-.5 1-1.8 1.5-3 1s-2-1.5-1.5-2.5L12 4z"/>
  </svg>`,

  translator: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M4 6h10M9 4v2c0 4-2 8-5 10M5 11c0 3 4 5 8 5"/>
    <path d="M21 21l-5-12-5 12M14 17h4"/>
  </svg>`,

  regulator: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M3 21h18M12 3l9 6H3l9-6zM6 10v10M10 10v10M14 10v10M18 10v10"/>
  </svg>`,

  peer_advocate: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="8" cy="8" r="3"/>
    <circle cx="16" cy="8" r="3"/>
    <path d="M2 20c0-3 2-5 6-5s6 2 6 5M14 15c4 0 6 2 6 5"/>
  </svg>`,

  triage: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M10.3 3.8L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.8a2 2 0 0 0-3.4 0z"/>
    <path d="M12 9v4M12 17h.01"/>
  </svg>`,

  negotiator: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 11c0 4-4 7-9 7-1.5 0-3-.3-4.3-.8L3 19l1.8-4.7C3.7 13.2 3 11.7 3 10c0-3.9 4-7 9-7s9 3.1 9 7z"/>
    <path d="M8 10h8M8 13h5"/>
  </svg>`,

  // Stances
  concede: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M5 12l5 5L20 7"/>
  </svg>`,

  push_back: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M6 6l12 12M18 6L6 18"/>
  </svg>`,

  extend: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
    <path d="M12 5v14M5 12h14"/>
  </svg>`,

  // Generic UI
  arrow_right: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M5 12h14M13 6l6 6-6 6"/>
  </svg>`,

  arrow_left: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M19 12H5M11 18l-6-6 6-6"/>
  </svg>`,

  close: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
    <path d="M6 6l12 12M18 6L6 18"/>
  </svg>`,

  download: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3"/>
  </svg>`,

  upload: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12"/>
  </svg>`,

  qr: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <rect x="3" y="3" width="7" height="7" rx="1"/>
    <rect x="14" y="3" width="7" height="7" rx="1"/>
    <rect x="3" y="14" width="7" height="7" rx="1"/>
    <path d="M14 14h3v3h-3zM20 14v3M14 20h3v1M21 20v1"/>
  </svg>`,

  share: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="6" cy="12" r="3"/>
    <circle cx="18" cy="6" r="3"/>
    <circle cx="18" cy="18" r="3"/>
    <path d="M8.6 10.7l6.8-3.4M8.6 13.3l6.8 3.4"/>
  </svg>`,

  globe: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="9"/>
    <ellipse cx="12" cy="12" rx="4" ry="9"/>
    <path d="M3 12h18"/>
  </svg>`,

  target: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="9"/>
    <circle cx="12" cy="12" r="5"/>
    <circle cx="12" cy="12" r="1.2" fill="currentColor"/>
  </svg>`,

  block: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
    <circle cx="12" cy="12" r="9"/>
    <path d="M5.5 5.5l13 13"/>
  </svg>`,
} as const;

export type IconKey = keyof typeof ICONS;

export function icon(key: IconKey, className = "icon-sm"): string {
  const svg = ICONS[key];
  if (!svg) return "";
  return svg.replace("<svg", `<svg class="${className}" aria-hidden="true"`);
}
