//! UM - 15-second vertical ad, rendered 100% in Rune.
//!
//! A24 atmosphere (negative space, film grain, one red accent, late reveal)
//! with Apple finishing (exact contrast, disciplined type, controlled motion).
//!
//! cargo run -p rune --example ad_um -- --video um.mp4 --fps 24 --duration 15

use rune::color::{self, Color};
use rune::compose::{Compositor, Frame};
use rune::render::{EffectPhase, EffectSite};
use rune::{AppSpec, Cx, El, LineCap, Shape, TextStyle, Tx, canvas, col, el, text};
use rune_fx::*;

const W: f32 = 540.0;
const H: f32 = 960.0;
const DURATION: f64 = 15.0;

const BASE: u32 = 1;
const LIGHT: u32 = 2;
const GRAIN: u32 = 3;

fn c(hex: &str) -> Color { color::hex(hex).expect("hex") }
fn void() -> Color { c("#050506") }
fn bone() -> Color { c("#F2EFE9") }
fn ash() -> Color { c("#8A8A86") }
fn shu() -> Color { c("#B32117") }

const HUGE: TextStyle = TextStyle::new(184.0, 700.0);
const BIG: TextStyle = TextStyle::new(36.0, 400.0);
const SMALL: TextStyle = TextStyle::new(18.0, 600.0);

struct Ad { t: f64 }
fn state() -> Ad { Ad { t: 0.0 } }
fn setup(_: &mut Ad, _: rune::Waker) {}
fn poll(s: &mut Ad, clock: f64, _: &mut Tx) -> bool { s.t = clock; true }

fn ease(x: f32) -> f32 { let x = x.clamp(0.0, 1.0); x * x * (3.0 - 2.0 * x) }

fn window(t: f64, a: f64, b: f64) -> (f32, f32) {
    if t < a || t >= b { return (0.0, 0.0); }
    let local = ((t - a) / (b - a)).clamp(0.0, 1.0) as f32;
    let f = (((b - a) * 0.10) as f32).clamp(0.25, 0.8);
    (local, ease(local / f).min(ease((1.0 - local) / f)))
}

fn dots(local: f32, t: f64) -> Shape {
    let mut s = Shape::new();
    let center: [f32; 2] = [270.0, 480.0];
    let n = 72usize;
    for i in 0..n {
        let alive = i as f32 / n as f32;
        if local > alive {
            continue;
        }
        let ang = i as f32 * 2.39996;
        let rad = 40.0 + (i as f32).sqrt() * 34.0;
        let sx = center[0] + ang.cos() * rad;
        let sy = center[1] + ang.sin() * rad;
        let pull = ease(((local - alive) * 8.0).clamp(0.0, 1.0));
        let drift = (t as f32 * 0.5 + i as f32 * 0.11).sin() * 2.0;
        let x = sx + (center[0] - sx) * pull + drift;
        let y = sy + (center[1] - sy) * pull;
        let r = 2.4 + (1.0 - pull) * 0.8;
        let ring: Vec<[f32; 2]> = (0..8)
            .map(|k| {
                let a = k as f32 * std::f32::consts::PI / 4.0;
                [x + r * a.cos(), y + r * a.sin()]
            })
            .collect();
        s = s.fill(ring, ash());
    }
    if local > 0.62 {
        let r = 5.0;
        let ring: Vec<[f32; 2]> = (0..10)
            .map(|k| {
                let a = k as f32 * std::f32::consts::PI / 5.0;
                [center[0] + r * a.cos(), center[1] + r * a.sin()]
            })
            .collect();
        s = s.fill(ring, shu());
    }
    s.view_box(W, H)
}

fn view(s: &Ad, _: &mut Cx<Ad>) -> El {
    let t = s.t.clamp(0.0, DURATION);
    let (l1, a1) = window(t, 0.0, 3.0);
    let (l2, a2) = window(t, 3.0, 6.0);
    let (l3, a3) = window(t, 6.0, 9.0);
    let (l4, a4) = window(t, 9.0, 12.0);
    let (l5, a5) = window(t, 12.0, 15.0);
    let _ = (l1, l4, l5);

    let stage = |mark: u32, data: [f32; 4]| {
        el().key(format!("fx-{}", mark)).effect(mark).effect_data(data).w(W).h(H)
    };

    let world = canvas(dots(l3, t)).key("dots").absolute(0.0, 0.0).w(W).h(H).opacity(a3);

    let open = col().key("open").absolute(0.0, 0.0).w(W).h(H)
        .padding(48.0).justify_between()
        .child(text("UM").font(HUGE).color(bone()).opacity(a1).scale(1.0 + 0.10 * ease(l1)))
        .child(text("uma coisa de cada vez").font(SMALL).color(ash()).opacity(a1 * 0.9));

    let second = col().key("second").absolute(0.0, 0.0).w(W).h(H).center().gap(20.0)
        .child(text("UM").font(HUGE).color(bone()).opacity(a2).scale(1.18 - 0.18 * ease(l2)))
        .child(text("um app que se recusa a multitarefa").font(SMALL).color(ash()).opacity(a2 * 0.85));

    let reveal = col().key("reveal").absolute(0.0, 0.0).w(W).h(H).center().gap(18.0)
        .child(text("o resto pode esperar.").font(BIG).color(bone()).opacity(a4))
        .child(el().key("rule").w(56.0).h(2.0).fill(shu()).opacity(a4));

    let end = col().key("end").absolute(0.0, 0.0).w(W).h(H).center().gap(22.0)
        .child(text("UM").font(HUGE).color(bone()).opacity(a5))
        .child(text("uma coisa de cada vez").font(SMALL).color(ash()).opacity(a5));

    let fade_out = if t > 14.2 { 1.0 - ease(((t - 14.2) / 0.8) as f32) } else { 1.0 };

    el().key("root").w(W).h(H).fill(void())
        .child(stage(BASE, [0.0, 0.18, 0.0, 0.0]))
        .child(stage(LIGHT, [0.0, 0.12 + 0.4 * l3, 0.0, 0.0]).opacity(0.5))
        .child(stage(GRAIN, [0.0, 0.22 + 0.2 * l3, 24.0, 0.0]).opacity(0.55))
        .child(world)
        .child(open)
        .child(second)
        .child(reveal)
        .child(end)
        .opacity(fade_out)
}

#[derive(Default)]
struct Gfx { fx: Option<FxRenderer> }

fn layer(mark: u32, d: [f32; 4], shape: rune_fx::Shape, t: f32) -> Option<FxLayer> {
    let fx = match mark {
        BASE => Fx::fill(GrainGradientParams { kind: GradientKind::Radial,
            colors: Stops::hex(&[0x101012, 0x050506]), amount: d[1],
            ..GrainGradientParams::default() }),
        LIGHT => Fx::glow(GlowParams { style: GlowStyle::Aura, color: rgb(0xf2efe9),
            intensity: d[1], radius: 160.0, aura_speed: 0.15, ..Default::default() }),
        GRAIN => Fx::grain(GrainParams { amount: d[1], fps: d[2], ..Default::default() }),
        _ => return None,
    };
    Some(fx.on(shape).at(t).seed(7))
}

impl Compositor<Ad> for Gfx {
    fn animating(&self) -> bool { true }
    fn render(&mut self, f: &mut Frame<'_, Ad>) {
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
            let Some(l) = layer(mark & 0xff, i.uv, rune_fx::Shape::rounded(x, y, w, h, 0.0), t) else { continue };
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
    rune::run_with(AppSpec { setup: Some(setup), poll: Some(poll),
        ..AppSpec::new("UM", (W, H), state, view) }, Gfx::default());
}
