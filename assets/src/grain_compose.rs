//! Rune x grain engine: composite a rendered grain film with a native Rune UI.
//!
//! The clip is the deterministic 141k-particle grain render from the Urashima/HyperFrames
//! project. Rune decodes it frame by frame in headless runs, so --snap / --video export the
//! composite without a player or a window.
//!
//! cargo run -p rune --example grain_compose -- --snap out.png --at 3.0
//! cargo run -p rune --example grain_compose -- --video grain-ui.mp4 --fps 24 --duration 6

use rune::tok::{self, type_};
use rune::{AppSpec, Cx, El, Player, SurfaceFit, Tx, Waker, col, el, row, text};
use std::time::Duration;

const CLIP: &str = "C:/Users/gabri/Documents/urashima-grain/urashima-grain.mp4";
const W: f32 = 540.0;
const H: f32 = 960.0;

struct Grain {
    clip: Player,
}

fn state() -> Grain {
    let clip = Player::new(CLIP.into());
    clip.set_looping(true);
    clip.play();
    Grain { clip }
}

fn setup(s: &mut Grain, wake: Waker) {
    s.clip.set_waker(wake);
}

fn poll(s: &mut Grain, _: f64, tx: &mut Tx) -> bool {
    if s.clip.is_playing() {
        tx.wake_after(Duration::from_millis(33));
    }
    s.clip.is_playing()
}

fn view(s: &Grain, _: &mut Cx<Grain>) -> El {
    let t = tok::theme(true);
    let (cw, ch) = s.clip.natural_size().unwrap_or((1080, 1920));
    let video = el()
        .key("grain")
        .w(W)
        .h(H * (ch as f32 / cw as f32) / (1920.0 / 1080.0))
        .video(&s.clip, SurfaceFit::Fill);

    let progress = s
        .clip
        .duration()
        .filter(|d| *d > 0.0)
        .map_or(0.0, |d| (s.clip.time() / d).clamp(0.0, 1.0));
    let status = match s.clip.state() {
        rune::PlayerState::Loading => "LOADING GRAINS",
        rune::PlayerState::Playing => "URASHIMA / GRAIN ENGINE",
        rune::PlayerState::Ready => "PAUSED",
        rune::PlayerState::Ended => "ENDED",
        rune::PlayerState::Failed(_) => "FAILED",
        _ => "",
    };

    let title = text("URASHIMA TARO")
        .font(type_::TITLE)
        .color(t.text)
        .help("The grain field follows the film frame by frame");
    let sub = text(status)
        .font(type_::MONO_CAPTION)
        .color(t.text_secondary);
    let bar = row()
        .key("progress")
        .w_full()
        .h(3.0)
        .radius(2.0)
        .fill(t.control_track)
        .child(el().w(W * progress as f32).h(3.0).radius(2.0).fill(t.indicator));

    let overlay = col()
        .key("overlay")
        .absolute(0.0, 0.0)
        .w(W)
        .h(H)
        .padding(24.0)
        .justify_between()
        .child(col().gap(4.0).child(title).child(sub))
        .child(bar);

    el()
        .key("root")
        .w(W)
        .h(H)
        .fill(t.bg)
        .child(video)
        .child(overlay)
}

fn main() {
    rune::run(AppSpec {
        setup: Some(setup),
        poll: Some(poll),
        ..AppSpec::new("Grain x Rune", (W, H), state, view)
    });
}
