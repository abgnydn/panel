/**
 * NGO Dashboard — systemic view.
 *
 * Three.js globe, rotating slowly. Five corridor arcs (PH→SA, ID→MY, etc.)
 * drawn as great-circle quadratic Béziers, each animated as a flowing
 * gradient. Pulsing dots on destination countries indicating recent abuse-
 * pattern activity. KPI strip below the canvas.
 *
 * Pure Three.js — no R3F. ~120 lines of scene code.
 */
import * as THREE from "three";
import { gsap } from "gsap";

import type { SceneCtx } from "./router";

// Country anchor lat/lng — used for the arc endpoints
const COUNTRY: Record<string, [number, number]> = {
  PH: [14.6, 121.0],  // Manila
  ID: [-6.2, 106.8],  // Jakarta
  SA: [24.7, 46.7],   // Riyadh
  MY: [3.1, 101.7],   // KL
  SG: [1.35, 103.8],  // Singapore
  HK: [22.3, 114.2],  // Hong Kong
  AE: [25.2, 55.3],   // Dubai
};

type Corridor = {
  origin: string;
  destination: string;
  label: string;
  intensity: number;   // 0..1 — opacity / pulse strength
  cases: number;
};

const CORRIDORS: Corridor[] = [
  { origin: "PH", destination: "SA", label: "Manila → Riyadh",   intensity: 0.95, cases: 47 },
  { origin: "ID", destination: "MY", label: "Surabaya → KL",     intensity: 0.85, cases: 38 },
  { origin: "PH", destination: "HK", label: "Manila → Hong Kong", intensity: 0.55, cases: 22 },
  { origin: "ID", destination: "SG", label: "Surabaya → SG",     intensity: 0.7,  cases: 28 },
  { origin: "PH", destination: "AE", label: "Cebu → Dubai",      intensity: 0.40, cases: 14 },
];

export function renderDashboard(ctx: SceneCtx): void {
  const { root, goto } = ctx;

  const totalCases = CORRIDORS.reduce((sum, c) => sum + c.cases, 0);
  const urgentCount = 12;  // mock — last 24h urgent sessions

  root.innerHTML = `
    <section class="dashboard">
      <header class="dash-head">
        <div class="eyebrow"><span class="dot"></span>NGO Dashboard · The systemic view</div>
        <h1 class="display-heading">From one worker, <em>to a pattern</em></h1>
        <p class="lede">Every contract Panel reviews — with the worker's consent — becomes
          part of the case archive. Within months, ILO partners and labor ministries see
          where the patterns are. Recruitment fees here. Passport retention there.
          <em>One worker's contract becomes systemic intelligence.</em></p>
      </header>

      <div class="dash-canvas-wrap">
        <canvas id="globe-canvas"></canvas>
        <div class="dash-legend">
          <div class="legend-title">Corridor activity · last 90 days</div>
          ${CORRIDORS.map((c) => `
            <div class="legend-row">
              <span class="legend-arc" style="--intensity:${c.intensity};"></span>
              <span class="legend-label">${c.label}</span>
              <span class="legend-value tabular">${c.cases}</span>
            </div>
          `).join("")}
        </div>
      </div>

      <div class="dash-kpis">
        <div class="kpi">
          <span class="kpi-label">Cases in archive</span>
          <span class="kpi-value tabular">${totalCases + 73}</span>
        </div>
        <div class="kpi">
          <span class="kpi-label">Live sessions today</span>
          <span class="kpi-value tabular">${urgentCount + 18}</span>
        </div>
        <div class="kpi">
          <span class="kpi-label">Urgent (≥7) · last 24h</span>
          <span class="kpi-value tabular">${urgentCount}</span>
        </div>
        <div class="kpi">
          <span class="kpi-label">Corridors covered</span>
          <span class="kpi-value tabular">${CORRIDORS.length}</span>
        </div>
      </div>

      <footer class="delib-foot">
        <button class="cta-ghost" id="back">← Back to your letter</button>
        <button class="cta" id="restart"><span>Review another contract</span></button>
      </footer>
    </section>
  `;

  root.querySelector<HTMLButtonElement>("#back")!.addEventListener("click", () => goto("recommendation"));
  root.querySelector<HTMLButtonElement>("#restart")!.addEventListener("click", () => goto("intake"));

  // ---- Three.js globe -----------------------------------------------------
  const canvas = root.querySelector<HTMLCanvasElement>("#globe-canvas")!;
  initGlobe(canvas);

  // ---- Entrance ------------------------------------------------------------
  gsap.fromTo(".dash-head",     { opacity: 0, y: 20 }, { opacity: 1, y: 0, duration: 0.7, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".dash-canvas-wrap", { opacity: 0, y: 22 }, { opacity: 1, y: 0, duration: 0.8, delay: 0.2, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".kpi",           { opacity: 0, y: 14 }, { opacity: 1, y: 0, duration: 0.5, stagger: 0.08, delay: 0.5, ease: "power3.out", clearProps: "transform" });
  gsap.fromTo(".delib-foot",    { opacity: 0, y: 10 }, { opacity: 1, y: 0, duration: 0.5, delay: 0.9, ease: "power3.out", clearProps: "transform" });
}

// ---------------------------------------------------------------------------
// Three.js globe scene
// ---------------------------------------------------------------------------
function initGlobe(canvas: HTMLCanvasElement): void {
  const rect = canvas.getBoundingClientRect();
  const W = rect.width || 800;
  const H = rect.height || 500;

  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setSize(W, H);

  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(40, W / H, 0.1, 100);
  camera.position.set(0, 0.4, 4.2);
  camera.lookAt(0, 0, 0);

  // Globe — wireframe sphere with subtle continents (just lat/lng grid)
  const R = 1.2;
  const sphere = new THREE.Mesh(
    new THREE.SphereGeometry(R, 48, 32),
    new THREE.MeshBasicMaterial({
      color: 0x0f172a,
      transparent: true,
      opacity: 0.04,
    }),
  );
  scene.add(sphere);

  const wire = new THREE.LineSegments(
    new THREE.WireframeGeometry(new THREE.SphereGeometry(R, 24, 16)),
    new THREE.LineBasicMaterial({ color: 0xcbd5e1, transparent: true, opacity: 0.4 }),
  );
  scene.add(wire);

  const earthGroup = new THREE.Group();
  earthGroup.add(sphere, wire);
  scene.add(earthGroup);

  // City dots
  const dotGeom = new THREE.SphereGeometry(0.018, 12, 12);
  for (const [code, [lat, lng]] of Object.entries(COUNTRY)) {
    const isOrigin = ["PH", "ID"].includes(code);
    const color = isOrigin ? 0x1e40af : 0xdc2626;
    const dot = new THREE.Mesh(dotGeom, new THREE.MeshBasicMaterial({ color }));
    dot.position.copy(latLngToVec3(lat, lng, R * 1.005));
    earthGroup.add(dot);

    // Halo for destinations (pulse with intensity)
    if (!isOrigin) {
      const halo = new THREE.Mesh(
        new THREE.RingGeometry(0.03, 0.05, 24),
        new THREE.MeshBasicMaterial({ color: 0xdc2626, transparent: true, opacity: 0.4, side: THREE.DoubleSide }),
      );
      halo.position.copy(dot.position);
      halo.lookAt(0, 0, 0);
      earthGroup.add(halo);
      (halo as unknown as { _t: number })._t = Math.random() * Math.PI * 2;
    }
  }

  // Arc lines
  const arcGroup = new THREE.Group();
  earthGroup.add(arcGroup);
  for (const c of CORRIDORS) {
    const a = COUNTRY[c.origin];
    const b = COUNTRY[c.destination];
    if (!a || !b) continue;
    const arc = makeArc(latLngToVec3(a[0], a[1], R), latLngToVec3(b[0], b[1], R), c.intensity);
    arcGroup.add(arc);
  }

  // Animation loop
  let rafId = 0;
  const start = performance.now();
  const tick = (now: number) => {
    rafId = requestAnimationFrame(tick);
    const t = (now - start) / 1000;
    earthGroup.rotation.y = t * 0.08;
    earthGroup.rotation.x = Math.sin(t * 0.05) * 0.12;

    // Pulse the destination halos
    earthGroup.traverse((obj) => {
      const tagged = obj as unknown as { _t?: number; scale?: THREE.Vector3; material?: THREE.Material };
      if (tagged._t === undefined) return;
      tagged._t += 0.04;
      if (obj instanceof THREE.Mesh) {
        const s = 1 + Math.sin(tagged._t) * 0.4;
        obj.scale.setScalar(s);
        (obj.material as THREE.MeshBasicMaterial).opacity = 0.55 - Math.sin(tagged._t) * 0.25;
      }
    });

    renderer.render(scene, camera);
  };
  rafId = requestAnimationFrame(tick);

  const onResize = () => {
    const r = canvas.getBoundingClientRect();
    if (!r.width || !r.height) return;
    renderer.setSize(r.width, r.height);
    camera.aspect = r.width / r.height;
    camera.updateProjectionMatrix();
  };
  window.addEventListener("resize", onResize);

  // Stop on leave
  const observer = new MutationObserver(() => {
    if (!document.body.contains(canvas)) {
      cancelAnimationFrame(rafId);
      window.removeEventListener("resize", onResize);
      renderer.dispose();
      observer.disconnect();
    }
  });
  observer.observe(document.body, { childList: true, subtree: true });
}

function latLngToVec3(lat: number, lng: number, r: number): THREE.Vector3 {
  const phi = (90 - lat) * (Math.PI / 180);
  const theta = (lng + 180) * (Math.PI / 180);
  return new THREE.Vector3(
    -r * Math.sin(phi) * Math.cos(theta),
     r * Math.cos(phi),
     r * Math.sin(phi) * Math.sin(theta),
  );
}

function makeArc(a: THREE.Vector3, b: THREE.Vector3, intensity: number): THREE.Line {
  // Mid-point lifted above the sphere — quadratic Bezier
  const mid = a.clone().add(b).multiplyScalar(0.5);
  const lift = 1 + a.distanceTo(b) * 0.45;
  mid.normalize().multiplyScalar(lift);
  const curve = new THREE.QuadraticBezierCurve3(a, mid, b);
  const points = curve.getPoints(60);
  const geom = new THREE.BufferGeometry().setFromPoints(points);
  const mat = new THREE.LineBasicMaterial({
    color: 0xdc2626,
    transparent: true,
    opacity: 0.3 + intensity * 0.55,
    linewidth: 2,
  });
  return new THREE.Line(geom, mat);
}
