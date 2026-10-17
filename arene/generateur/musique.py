#!/usr/bin/env python3
"""Bande-son originale pour les vidéos Arène : beat sombre à 90 BPM, intro calme, drop à `drop` s.
Usage : python3 musique.py <duree_s> <drop_s> <sortie.wav> [transitions_s séparées par des virgules]"""
import sys, wave
import numpy as np
from scipy.signal import butter, sosfilt

SR = 44100
BPM = 90
BEAT = 60 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(7)

def note(n):  # n en demi-tons depuis A4
    return 440.0 * 2 ** (n / 12)

def lp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x)

def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x)

def bp(x, lo, hi):
    return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)

def saw(f, t, harm=14):
    y = np.zeros_like(t)
    for k in range(1, harm + 1):
        if f * k > SR / 2.5:
            break
        y += np.sin(2 * np.pi * f * k * t) / k
    return y

def build(duree, drop, transitions):
    N = int(duree * SR)
    t = np.arange(N) / SR
    out_pad = np.zeros(N); out_bass = np.zeros(N); out_drum = np.zeros(N); out_fx = np.zeros(N)

    # Am - F - Dm - E (accords en demi-tons depuis A4)
    prog = [[-12, -9, -5, 0], [-16, -12, -9, -4], [-19, -16, -12, -7], [-17, -13, -10, -5]]
    roots = [-24, -28, -31, -29]
    nbars = int(np.ceil(duree / BAR)) + 1
    for b in range(nbars):
        s = int(b * BAR * SR); e = min(N, int((b + 1) * BAR * SR) + int(0.3 * SR))
        if s >= N:
            break
        tt = np.arange(e - s) / SR
        ch = prog[b % 4]
        seg = np.zeros(e - s)
        for n in ch:
            f = note(n)
            seg += saw(f * 1.003, tt) + saw(f * 0.997, tt)
        env = np.minimum(1, tt / 0.35) * np.exp(-tt * 0.15)
        out_pad[s:e] += seg * env * 0.05
        # arpège de cloche discret (une note par croche, uniquement après le drop)
        if b * BAR >= drop - 0.01:
            for i in range(8):
                ns = s + int(i * BEAT / 2 * SR)
                if ns >= N:
                    break
                ln = min(N - ns, int(0.6 * SR)); ta = np.arange(ln) / SR
                f = note(ch[[0, 2, 1, 3, 2, 1, 3, 2][i]] + 12)
                out_fx[ns:ns + ln] += (np.sin(2 * np.pi * f * ta) + 0.3 * np.sin(4 * np.pi * f * ta)) * np.exp(-ta * 7) * 0.035
        # basse : 808 sur le 1 et le 3,5
        for pos in (0, 2.5):
            bs = s + int(pos * BEAT * SR)
            if bs >= N or b * BAR + pos * BEAT < drop - 0.01:
                continue
            ln = min(N - bs, int(1.2 * BEAT * SR)); tb = np.arange(ln) / SR
            f0 = note(roots[b % 4])
            ph = 2 * np.pi * np.cumsum(f0 * (1 + 0.6 * np.exp(-tb * 40))) / SR
            out_bass[bs:bs + ln] += np.tanh(1.6 * np.sin(ph)) * np.exp(-tb * 1.6) * 0.42

    # batterie après le drop
    def add(buf, pos, sig):
        i = int(pos * SR)
        if i >= N:
            return
        ln = min(len(sig), N - i); buf[i:i + ln] += sig[:ln]
    tk = np.arange(int(0.45 * SR)) / SR
    kick = np.sin(2 * np.pi * np.cumsum(45 + 110 * np.exp(-tk * 30)) / SR) * np.exp(-tk * 7) * 0.9
    tc = np.arange(int(0.3 * SR)) / SR
    clap = bp(rng.standard_normal(len(tc)), 900, 4000) * np.exp(-tc * 18) * 0.55
    th = np.arange(int(0.06 * SR)) / SR
    hat = hp(rng.standard_normal(len(th)), 7000) * np.exp(-th * 70) * 0.22
    nb = int((duree - drop) / BEAT) + 2
    for i in range(nb):
        p = drop + i * BEAT
        if p >= duree - 1.5:
            break
        beat_in_bar = i % 4
        if beat_in_bar == 0:
            add(out_drum, p, kick)
        if beat_in_bar == 2:
            add(out_drum, p, clap)
            add(out_drum, p + 0.5 * BEAT, kick * 0.7)
        for k in range(2):
            v = 1.0 if k == 0 else 0.6
            add(out_drum, p + k * BEAT / 2, hat * v)
        if i % 8 == 7:  # roulement de charley
            for k in range(4):
                add(out_drum, p + BEAT / 2 + k * BEAT / 8, hat * 0.5)

    # montée avant le drop + souffle sur chaque transition
    rl = int(min(drop, 3.0) * SR); rs = int(drop * SR) - rl
    if rl > 0:
        tr = np.arange(rl) / SR
        noise = rng.standard_normal(rl)
        riser = hp(noise, 1500) * (tr / tr[-1]) ** 2 * 0.18
        out_fx[rs:rs + rl] += riser
    tw = np.arange(int(0.7 * SR)) / SR
    whoosh = bp(rng.standard_normal(len(tw)), 400, 3000) * np.sin(np.pi * tw / tw[-1]) ** 2 * 0.12
    for p in transitions:
        add(out_fx, p - 0.35, whoosh)
    timp = np.arange(int(1.5 * SR)) / SR
    impact = (np.sin(2 * np.pi * np.cumsum(38 + 60 * np.exp(-timp * 12)) / SR) * np.exp(-timp * 2.5)) * 0.6
    add(out_drum, drop, impact)

    # ducking des nappes sous le kick
    duck = np.ones(N)
    for i in range(nb):
        p = drop + i * BEAT
        if i % 4 in (0,):
            s = int(p * SR); ln = min(N - s, int(0.4 * SR))
            if ln > 0:
                duck[s:s + ln] = np.minimum(duck[s:s + ln], 1 - 0.55 * np.exp(-np.arange(ln) / SR * 9))
    pad = lp(out_pad, 1800) * duck
    mix = pad + lp(out_bass, 400) + out_drum + out_fx
    # fondu de fin
    fo = int(2.0 * SR); mix[-fo:] *= np.linspace(1, 0, fo) ** 1.5
    fi = int(0.05 * SR); mix[:fi] *= np.linspace(0, 1, fi)
    mix = np.tanh(mix * 1.1)
    mix *= 0.89 / np.max(np.abs(mix))
    st = np.stack([mix, np.roll(mix, int(0.012 * SR)) * 0.96 + mix * 0.04], axis=1)  # léger élargissement stéréo
    return st

if __name__ == '__main__':
    duree, drop, outp = float(sys.argv[1]), float(sys.argv[2]), sys.argv[3]
    trans = [float(x) for x in sys.argv[4].split(',')] if len(sys.argv) > 4 and sys.argv[4] else []
    st = build(duree, drop, trans)
    with wave.open(outp, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((st * 32767).astype(np.int16).tobytes())
    print('ok', outp)
