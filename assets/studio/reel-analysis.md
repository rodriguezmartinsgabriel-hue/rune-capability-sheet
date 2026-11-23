# Laudo frame-a-frame — `demo/rune.mp4` (referência oficial)

**Arquivo analisado:** `demo/rune.mp4` do repositório `anomalyco/rune` — 1920×1080, 60 fps, 54,000 s, 3240 frames, H.264 + AAC, 21,8 MB.
**Método:** extração integral dos 3240 frames em 480×270, medição de R/G/B, luminância Rec.709, saturação HSV e diferença média frame a frame; seis subagentes interpretaram faixas de 9 s com contact sheets de 36 amostras cada.

## 1. Estrutura de cortes

O reel tem **apenas 4 cortes duros**, concentrados na segunda metade:

| Tempo | Frame | `diff` | De → para |
|---|---:|---:|---|
| 32,000 s | 1920 | 119,38 | Night Drive → Pricing |
| 36,000 s | 2160 | 88,95 | Pricing → Library |
| 38,667 s | 2320 | 84,31 | Library → PAD-16 |
| 42,667 s | 2560 | 64,08 | PAD-16 → Ship v2.0 |

Todo o resto — 0–32 s e 42,7–54 s — é continuidade por cross-dissolve, wipe, morph, push-in e fade. O `diff` típico dentro dos planos fica entre 0,1 e 8; os cortes têm 64–119. **Corte só em frame estável**, nunca durante movimento.

## 2. Mapa de planos

| Tempo | Plano | Técnica de transição | Assinatura visual |
|---|---|---|---|
| 0–1,8 | Documento `Small type, sharp edges` | pan lento | manchete gigante cortada pela borda |
| 1,8–2,9 | Mesmo documento | whip pan (~1,1 s, easing simétrico) | pico `diff=21,9` em 2,48 s |
| 2,9–4,0 | Seleção de texto + toolbar `B I U A` | dissolve com motion blur (~0,3 s) | push-in + ghosting |
| 4–8,2 | Toggles e swatches | hold com spring | `Spring 1.2 - 1.6, 3-4px travel` |
| 8,2–9 | Tema claro | fade-to-white em 42 frames | lum 27 → 241, sat 0,147 → 0,018 |
| 9–10,3 | Settings claro | pan lento | branco `#F3F4F6`, sat 0,014 |
| 10,3–10,65 | → código | cross-dissolve 0,32 s | lum 240 → 32 |
| 10,65–14,3 | Split diff `backoff.rs` | zoom 1,0× → 1,8× em 0,15 s | review comments reais |
| 14,3–14,75 | → grid | dissolve + virada de cor | sat 0,18 → 0,396 |
| 14,75–18 | Grid com luz por trás | push-in 1,0× → 1,2× | bloom dourado |
| 18–19 | Grid âmbar | dissolve 0,12 s | lum 39, sat 0,345 |
| 19–21 | Modal liquid metal | push-in + sparkles | `Liquid metal 1.3× → 2.0×` |
| 21–23,6 | Deployments | hold de 2,2 s | `diff < 1,4` |
| 23,6–27 | Hero gradiente + galeria | zoom 15,8 de `diff` | `Liquid glass 1.1× → 1.5×` |
| 27–32 | Player Night Drive | wipe + parallax | `Filtered glass 1.1× → 1.3×` |
| 32–36 | Pricing | corte + zoom + borda elétrica | `Electric border 1.1× → 1.4×` |
| 36–38,7 | Library | corte + wobble com RGB split | `Shockwaves 1.1× → 1.3×` |
| 38,7–42,7 | PAD-16 | corte + pads no BPM 90 | `Pads on the beat 1.1× → 1.5×` |
| 42,7–47,7 | Ship v2.0 | corte + fogo + `Ship it → Shipping…` | `Fire 1.1× → 1.2×` |
| 48–50,9 | Wordmark FINE | fade-to-black 0,28 s + montagem de azulejos | pico `diff=25,15` |
| 50,9–53,4 | End card | hold absoluto de 2,42 s | tagline + URL |
| 53,4–54 | Fade final | rampa linear | último frame lum 0,26 |

## 3. Paleta e luminância

- Escada descendente deliberada: `Library` lum 98,7 → `PAD-16` 69,9 → `Ship` 28,2.
- Dark nunca é preto puro: `#19191B` a `#1B1E23`, com canal azul 2–8 unidades acima do vermelho.
- Saturação baixa (0,14–0,17) com picos isolados: 0,2195 no toggle azul, 0,5442 no painel rosa, 0,3964 no grid âmbar.
- Cartão final: `#100F12` / preto, prata frio (B > G > R) e laranja `#FD5A1E` na cena do fogo.
- Fade final termina em lum 0,26 — preto verdadeiro, sem cartão posterior.

## 4. Regras extraídas para o nosso reel

1. Zero cortes nos primeiros 32 s; transições por dissolve/whip/push-in.
2. Cortes apenas em frames estáveis, com quebra de luminância de 40–50 pontos.
3. Hold de 2–4 s antes do clímax — é onde o olho descansa.
4. Pill de parâmetro sempre no mesmo lugar (inferior-esquerda): `Efeito 1.1× → 1.5×`.
5. Push-in lento e contínuo em toda captura de UI (10–25 % de escala).
6. Micro-interação coreografada: cursor chega, clica, estado muda.
7. Causa e efeito visíveis: clique → sparkles → nova linha com timestamp `now`.
8. Arco de cor em três atos: neutro → frio/dessaturado → quente/saturado → prata frio.
9. Tipografia disciplinada: uma família sans, 3–4 níveis de tamanho, mono só para código/hashes.
10. End card imóvel de ~2,4 s com tagline e URL em cascata; fade final de ~0,6 s.

**Fonte:** os 3240 frames e o CSV de métricas estão em `reel-reference/allframes/`; os contact sheets por faixa em `reel-reference/chunks/`.
