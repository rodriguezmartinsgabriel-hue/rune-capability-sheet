//! Urashima Taro - a cinematic reel made with Rune alone, no external footage.
//!
//! One composite look, built from Rune's own GPU layers at the same time:
//! grain-gradient base, atmospheric mesh, motivated glow, haze, a unifying film
//! grain pass and native type. Every layer's parameters change with the story
//! beat, so technique serves direction instead of demonstrating itself.
//!
//! cargo run -p rune --example urashima_pure -- --snap pure.png --at 52.0
//! cargo run -p rune --example urashima_pure -- --video urashima-pure.mp4 --fps 24 --duration 60

use rune::color::{self, Color};
use rune::compose::{Compositor, Frame};
use rune::render::{EffectPhase, EffectSite};
use rune::tok;
use rune::{AppSpec, Cx, El, TextStyle, Tx, col, el, row, text};
use rune_fx::*;

const W: f32 = 540.0;
const H: f32 = 960.0;
const DURATION: f64 = 60.0;

// Effect marks: all layers are present together; only their numbers move.
const BASE: u32 = 1;
const ATMOS: u32 = 2;
const LIGHT: u32 = 3;
const HAZE: u32 = 4;
const GRAIN: u32 = 5;
const SOURCE: u32 = 6;
const SPARKLES: u32 = 7;

fn c(hex: &str) -> Color { color::hex(hex).expect("palette hex") }
fn bone() -> Color { c("#EDE8DF") }
fn ash() -> Color { c("#8A8F94") }
fn shu() -> Color { c("#D14037") }
fn void() -> Color { c("#050607") }

const TITLE_BIG: TextStyle = TextStyle::new(34.0, 650.0);
const META: TextStyle = TextStyle::new(16.0, 600.0);

struct Chapter {
    start: f64,
    end: f64,
    kicker: &'static str,
    lines: &'static [&'static str],
    density: f32,
    glow: f32,
    haze: f32,
}

const CHAPTERS: &[Chapter] = &[
    Chapter { start: 0.0, end: 3.0, kicker: "I / O RETORNO", density: 0.10, glow: 0.10, haze: 0.02, lines: &[
        "Ele voltou.", "Fazia 300 anos.",
    ] },
    Chapter { start: 3.0, end: 10.0, kicker: "II / O MAR", density: 0.55, glow: 0.18, haze: 0.10, lines: &[
        "Salvou uma tartaruga.", "Ela prometeu pagar.",
    ] },
    Chapter { start: 10.0, end: 20.0, kicker: "III / O PALACIO", density: 0.38, glow: 0.42, haze: 0.06, lines: &[
        "A tartaruga o levou.", "Um palacio sob as ondas.",
    ] },
    Chapter { start: 20.0, end: 30.0, kicker: "IV / A CAIXA", density: 0.22, glow: 0.24, haze: 0.03, lines: &[
        "Tr\u{00ea}s dias. Uma caixa.", "N\u{00e3}o abra.",
    ] },
    Chapter { start: 30.0, end: 42.0, kicker: "V / O CAIS", density: 0.30, glow: 0.08, haze: 0.04, lines: &[
        "Voltou ao cais.", "Ningu\u{00e9}m o conhecia.",
    ] },
    Chapter { start: 42.0, end: 50.0, kicker: "VI / A PROVA", density: 0.20, glow: 0.12, haze: 0.02, lines: &[
        "Tr\u{00ea}s dias no palacio.", "Trezentos anos na terra.",
    ] },
    Chapter { start: 50.0, end: 56.0, kicker: "VII / O CLIMAX", density: 0.85, glow: 0.90, haze: 0.20, lines: &[
        "Ele abriu a caixa.", "O tempo saiu de uma vez.",
    ] },
    Chapter { start: 56.0, end: 60.0, kicker: "VIII / O GRAO", density: 0.02, glow: 0.03, haze: 0.00, lines: &[
        "S\u{00f3} um gr\u{00e3}o ficou.",
    ] },
];

struct Reel {
    t: f64,
}

fn state() -> Reel { Reel { t: 0.0 } }
fn setup(_: &mut Reel, _: rune::Waker) {}
fn poll(s: &mut Reel, clock: f64, _: &mut Tx) -> bool { s.t = clock; true }

fn fade(t: f64, start: f64, end: f64) -> f32 {
    if t < start || t >= end { return 0.0; }
    let f = (((end - start) * 0.12) as f32).clamp(0.6, 1.2);
    let sm = |x: f32| { let x = x.clamp(0.0, 1.0); x * x * (3.0 - 2.0 * x) };
    sm(((t - start) as f32) / f).min(sm(((end - t) as f32) / f))
}

fn timecode(t: f64) -> String {
    let s = t.max(0.0) as u64;
    format!("{:02}:{:02} / 01:00", s / 60, s % 60)
}

fn view(s: &Reel, _: &mut Cx<Reel>) -> El {
    let _theme = tok::theme(true);
    let now = s.t.clamp(0.0, DURATION);
    let idx = CHAPTERS.iter().position(|c| now >= c.start && now < c.end).unwrap_or(CHAPTERS.len() - 1);
    let ch = &CHAPTERS[idx];
    let alpha = fade(now, ch.start, ch.end);
    let local = ((now - ch.start) / (ch.end - ch.start)).clamp(0.0, 1.0) as f32;
    let progress = (now / DURATION) as f32;

    // One motivated camera move per beat: a slow push-in, never a focal-length zoom.
    let ease = local * local * (3.0 - 2.0 * local);
    let push = 1.0 + 0.12 * ease;
    let shake = if ch.kicker.starts_with("VII") { (now * 37.0).sin() as f32 * 0.8 } else { 0.0 };
    // The motivated light source drifts; the grain boils at 24 fps; haze breathes.
    let light_x = 270.0 + 42.0 * (now * 0.62).sin() as f32;
    let light_y = 250.0 + 34.0 * (now * 0.47).cos() as f32;
    let glow = ch.glow * (0.80 + 0.35 * (now * 1.3).sin() as f32);
    let haze = ch.haze * (0.75 + 0.50 * (now * 0.9).cos() as f32);
    let boil = 0.06 * (now * 24.0 * std::f64::consts::PI).sin() as f32;
    let stage = |mark: u32, data: [f32; 4]| {
        el().key(format!("fx-{}", mark))
            .effect(mark)
            .effect_data(data)
            .w(W).h(H)
            .scale(push)
            .offset(shake, 0.0)
    };

    let backdrop = col().gap(0.0)
        .child(stage(BASE, [idx as f32, ch.density, local, 0.0]))
        .child(stage(ATMOS, [idx as f32, ch.density, local, 0.0]).opacity(0.32))
        .child(stage(HAZE, [idx as f32, haze.max(0.0), local, 0.0]).opacity(0.22))
        .child(stage(LIGHT, [idx as f32, glow.max(0.0), local, 0.0]).opacity(0.75))
        .child(stage(GRAIN, [idx as f32, (ch.density + boil).max(0.0), 24.0, local]).opacity(0.42))
        .child(stage(SPARKLES, [idx as f32, ch.density, local, 0.0]).opacity(0.30));

    let scrim = el().key("scrim").absolute(40.0, 400.0).w(W - 80.0).h(270.0).radius(16.0)
        .linear_gradient(1.57, [
            (0.0, void().alpha(0.34 * alpha)),
            (1.0, void().alpha(0.78 * alpha)),
        ]);
    let mut words = col().key("words").padding(22.0).gap(10.0);
    for line in ch.lines {
        words = words.child(text(*line).font(TITLE_BIG).color(bone()).opacity(alpha));
    }

    let top = row().key("top").absolute(40.0, 120.0).w(W - 80.0).justify_between()
        .child(text(ch.kicker).font(META).color(shu()).opacity(alpha))
        .child(text(timecode(now)).font(META).color(ash()).opacity(alpha));
    let track = el().key("track").absolute(40.0, 720.0).w(W - 80.0).h(3.0).radius(2.0).fill(ash().alpha(0.25));
    let fill = el().key("fill").absolute(40.0, 720.0).w((W - 80.0) * progress).h(3.0).radius(2.0).fill(shu());
    let sig = el().key("sig").absolute(40.0, 690.0)
        .child(text("URASHIMA TARO  -  um conto do Jap\u{00e3}o").font(META).color(ash()).opacity(alpha * 0.8));

    el().key("root").w(W).h(H).fill(void())
        .child(backdrop)
        .child(el().key("source").absolute(light_x - 32.0, light_y - 32.0).size(64.0, 64.0).radius(32.0)
            .effect(SOURCE).effect_data([idx as f32, glow.max(0.0), local, 0.0]).fill(shu()).opacity(alpha))
        .child(scrim.child(words))
        .child(top).child(sig).child(track).child(fill)
}

#[derive(Default)]
struct Gfx { fx: Option<FxRenderer> }

fn layer(mark: u32, d: [f32; 4], shape: Shape, t: f32) -> Option<FxLayer> {
    let chapter = d[0] as u32;
    let fx = match mark {
        BASE => Fx::fill(GrainGradientParams {
            kind: GradientKind::Radial,
            colors: Stops::hex(&[0x1a1c20, 0x050607]),
            amount: 0.18 + 0.10 * d[1],
            ..GrainGradientParams::default()
        }),
        ATMOS => {
            let colors: &[u32] = match chapter {
                2 => &[0x0a1014, 0x16232b, 0x050607],
                6 => &[0x140607, 0x3a0d10, 0x050607],
                _ => &[0x0a0b0c, 0x1a1c20, 0x050607],
            };
            Fx::fill(MeshGradientParams { colors: Stops::hex(colors), speed: 0.10 + 0.06 * d[1], ..MeshGradientParams::dusk() })
        }
        LIGHT => Fx::glow(GlowParams { style: GlowStyle::Aura, color: rgb(0xe8e2d7),
            intensity: 0.08 + 0.55 * d[1], radius: 90.0 + 120.0 * d[1], aura_speed: 0.28, ..Default::default() }),
        HAZE => Fx::distort(DistortParams::HeatHaze { height: 300.0, scale: 12.0,
            speed: 0.5, amount: d[1], whole_shape: true }),
        GRAIN => Fx::grain(GrainParams { amount: 0.28 + 0.35 * d[1], fps: d[2], ..Default::default() }),
        SOURCE => Fx::glow(GlowParams { style: GlowStyle::Neon, color: rgb(0xd14037),
            intensity: 0.5 + 0.6 * d[1], radius: 26.0, ..Default::default() }),
        SPARKLES => Fx::sparkles(SparkleParams { burst: None, count: 110, size: 1.5,
            color: rgb(0xede8df), margin: 18.0, ..Default::default() }),
        _ => return None,
    };
    Some(fx.on(shape).at(t).seed(chapter + 1))
}

impl Compositor<Reel> for Gfx {
    fn animating(&self) -> bool { true }
    fn render(&mut self, f: &mut Frame<'_, Reel>) {
        let (device, queue, size) = (f.device, f.queue, f.size);
        let t = f.rt.t as f32;
        let mut at = Vec::new();
        let mut layers = Vec::new();
        let mut placements = Vec::new();
        for (n, i) in f.rt.instances.iter().enumerate() {
            if i.params[1] != rune::render::KIND_EFFECT { continue; }
            let mark = f.rt.marks.get(n).copied().unwrap_or(0);
            let k = i.params[3];
            let [x, y, w, h] = i.rect.map(|v| v / k);
            let r = i.radii.iter().fold(0.0f32, |a, v| a.max(v.abs())) / k;
            let Some(l) = layer(mark & 0xff, i.uv, Shape::rounded(x, y, w, h, r), t) else { continue };
            at.push(n as u32);
            layers.push(l);
            placements.push(FxSlot::default().scale(k).clip(i.clip, i.fade));
        }
        let fx = self.fx.get_or_insert_with(|| FxRenderer::new(device, f.format, FxOptions { dither: true }));
        fx.set_srgb_blend(f.srgb_blend());
        fx.add_format(device, wgpu::TextureFormat::Rgba16Float);
        fx.prepare_with_slots(device, queue, &FxFrame { viewport: [size.0, size.1], scale: 1.0,
            layers: &layers, backdrop: None, sources: &[] }, &placements);
        let clear = f.rt.clear_color();
        f.ui.prepare(device, queue, &mut f.rt.text.atlas, &f.rt.instances, size);
        f.ui.draw_with_backdrop(f.encoder, f.target, clear, &mut |phase, s: &EffectSite<'_>| {
            if let EffectPhase::Draw(pass) = phase {
                if let Some(k) = at.iter().position(|n| *n == s.index) {
                    fx.draw_layer_in(pass, s.format, s.origin, k);
                }
            }
        });
    }
}

fn main() {
    rune::run_with(AppSpec {
        setup: Some(setup),
        poll: Some(poll),
        ..AppSpec::new("Urashima Pure", (W, H), state, view)
    }, Gfx::default());
}
