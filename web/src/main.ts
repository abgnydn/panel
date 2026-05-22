import "./style.css";
import { initFluidBackground } from "./three/fluid-background";
import { mountRouter } from "./scenes/router";

const canvas = document.getElementById("bg") as HTMLCanvasElement | null;
const app = document.getElementById("app") as HTMLElement | null;
if (!canvas || !app) throw new Error("missing #bg or #app");

initFluidBackground(canvas);
mountRouter(app);
