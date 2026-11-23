# Laudo AAA — Urashima Taro, reel 60 s em Rune puro

**Arquivo:** `20261123_urashima_60s_9x16_v01.mp4` · **Data:** 23/11/2026 · **Direção:** Gabriel

## Medições

| Item | Medido | Estado |
|---|---|---|
| Resolução | 1080×1920 | OK |
| FPS / frames | 24 / 1440 | OK |
| Duração | 60,000 s | OK |
| Vídeo | H.264, yuv420p, `tv`, bt709 / bt709 / bt709 | OK |
| Movflags | `+faststart` | OK |
| Áudio | AAC 48 kHz, 2 canais | OK |
| Loudness integrado | **−15,8 LUFS** (faixa de aviso −17 a −12) | OK |
| True peak | **−3,0 dBFS** (limite ≤ −1,5) | OK |
| LRA | 17,5 LU (acima da preferência 6–9 do vault) | AVISO |
| Quadros pretos | 0 detectados | OK |
| Freezedetect | 30 eventos com limiar 0,3% — movimento sutil, visível nas amostras | AVISO |
| Render | 1440 frames em 41,83 s (34,4 frames/s), CPU/frame p50 6,96 ms, p95 12,55 ms | OK |
| Fonte Rust | `urashima_pure.rs`, `char_audit.py` = 0 ERROR | OK |

## Direção aplicada

- **Espinha dramática:** Voyage and Return + arco Icarus, hook in medias res nos 0–3 s, clímax em 50–56 s e resolução em 56–60 s.
- **Motivo:** 3 → 300; a frase plantada "não abra" é paga no clímax. Cada linha é causa ou consequência da anterior.
- **Safe zone:** 12% topo / 22% base / 6% laterais.
- **Um único acento:** vermilion `#D14037`; neutros `#EDE8DF` e `#8A8F94`; fundo `#050607`.
- **Técnicas combinadas (não sequenciais):** gradiente de grão, malha atmosférica, glow motivado, haze, partículas, filme-grão, push-in com easing, shake de 6 quadros no clímax e tipografia nativa — todas simultâneas, com parâmetros derivados do tempo.

## Verificação de fatos

TinyFish: USC Digital Folklore Archives, Wikipedia e historyofjapan.co.uk confirmam tartaruga resgatada, caixa com aviso, 300 anos e fumaça que envelhece o pescador. Vault: `00 — MOC Storytelling`, `Contos Japoneses`, `23-grain-film-urashima`, `Ciencia de Cor — MOC`, `Video - MOC`, `Bruxos do VFX — MOC`, `Câmara 3D — MOC`, `Design & Post Production — MOC`.

## Limites honestos

- Nenhuma publicação externa foi feita; `handoff` aqui não significa `published`.
- Aprovação final de publicação é exclusivamente humana (Gabriel).
- O reel é intencionalmente minimalista: a baixa variação de pixels gera avisos no `freezedetect`, não quadros congelados de fato.
