"""Generate a short, light, royalty-free background track (original synthesis).
Usage: python3 music.py OUT.wav SECONDS [mood] [seed]
moods: warm (default), bright, calm"""
import sys, numpy as np
from scipy.io import wavfile
from scipy.signal import butter, lfilter, fftconvolve

SR = 44100
def midi(n): return 440.0 * 2 ** ((n - 69) / 12)

PROGS = {
 "warm":   (92,  [[48,55,64,71],[45,52,60,67],[41,48,57,64],[43,50,59,64]]),   # Cmaj7 Am7 Fmaj7 G
 "bright": (100, [[50,57,66,69],[47,54,62,66],[43,50,59,62],[45,52,61,64]]),   # D Bm G A
 "calm":   (80,  [[45,52,60,64],[41,48,57,60],[48,55,64,67],[43,50,59,62]]),   # Am F C G
}

def env(n, a, r):
    e = np.ones(n); a = int(a*SR); r = int(r*SR)
    if a: e[:a] = np.linspace(0, 1, a)
    if r: e[-r:] *= np.linspace(1, 0, r)
    return e

def pad(freq, dur):
    t = np.arange(int(dur*SR))/SR
    s = sum(np.sin(2*np.pi*freq*d*t + p) for d, p in [(1,0),(1.003,1),(0.997,2),(2,0.5)]) * 0.25
    s += 0.12*np.sin(2*np.pi*freq*3*t)
    return s * env(len(t), dur*0.35, dur*0.4)

def pluck(freq, dur=1.2):
    t = np.arange(int(dur*SR))/SR
    s = np.sin(2*np.pi*freq*t) + 0.35*np.sin(2*np.pi*2*freq*t)*np.exp(-t*6) + 0.1*np.sin(2*np.pi*3*freq*t)*np.exp(-t*9)
    return s * np.exp(-t*3.2) * env(len(t), 0.004, 0.05)

def kick(dur=0.35):
    t = np.arange(int(dur*SR))/SR
    f = 50 + 70*np.exp(-t*30)
    return np.sin(2*np.pi*np.cumsum(f)/SR) * np.exp(-t*9)

def shaker(rng, dur=0.08):
    n = int(dur*SR); x = rng.standard_normal(n) * np.exp(-np.arange(n)/SR*60)
    b, a = butter(2, 6000/(SR/2), 'high'); return lfilter(b, a, x)

def add(buf, sig, start, gain):
    i = int(start*SR); j = min(len(buf), i+len(sig))
    if i < len(buf): buf[i:j] += sig[:j-i]*gain

def make(seconds, mood="warm", seed=0):
    rng = np.random.default_rng(seed)
    bpm, prog = PROGS[mood]
    beat = 60/bpm; bar = beat*4
    total = seconds + 2
    L = np.zeros(int(total*SR)); R = np.zeros_like(L)
    nbars = int(np.ceil(total/bar))
    for b in range(nbars):
        ch = prog[(b + seed) % len(prog)]; t0 = b*bar
        for k, n in enumerate(ch):
            p = pad(midi(n), bar*1.15)
            add(L, p, t0, 0.05 * (1.1 if k%2 else 0.9)); add(R, p, t0, 0.05 * (0.9 if k%2 else 1.1))
        add(L, pad(midi(ch[0]-12), bar*1.1), t0, 0.09); add(R, pad(midi(ch[0]-12), bar*1.1), t0, 0.09)
        arp = [ch[1]+12, ch[2]+12, ch[3]+12, ch[2]+12, ch[1]+24, ch[3]+12, ch[2]+12, ch[3]+12]
        if rng.random() < .5: arp = arp[::-1]
        for i, n in enumerate(arp):
            pl = pluck(midi(n)); pan = 0.5 + 0.3*np.sin(i)
            add(L, pl, t0 + i*beat/2, 0.09*(1-pan)*2*(0.8 if i%2 else 1)); add(R, pl, t0 + i*beat/2, 0.09*pan*2*(0.8 if i%2 else 1))
        if b >= 1:
            for q in range(4):
                if q in (0, 2): add(L, kick(), t0+q*beat, 0.22); add(R, kick(), t0+q*beat, 0.22)
                sh = shaker(rng); add(L, sh, t0+q*beat+beat/2, 0.05); add(R, sh, t0+q*beat+beat/2, 0.04)
    # soft low-pass + reverb
    b, a = butter(2, 7000/(SR/2))
    L, R = lfilter(b, a, L), lfilter(b, a, R)
    n = int(1.6*SR); ir = rng.standard_normal(n) * np.exp(-np.arange(n)/SR*3.5)
    irR = rng.standard_normal(n) * np.exp(-np.arange(n)/SR*3.5)
    L = L + 0.18*fftconvolve(L, ir)[:len(L)]/np.sqrt(n)*20
    R = R + 0.18*fftconvolve(R, irR)[:len(R)]/np.sqrt(n)*20
    x = np.stack([L, R], 1)[:int(seconds*SR)]
    fade = env(len(x), 0.8, 1.5); x *= fade[:, None]
    x /= np.max(np.abs(x)) + 1e-9; x *= 0.8
    return (x*32767).astype(np.int16)

if __name__ == "__main__":
    out, secs = sys.argv[1], float(sys.argv[2])
    mood = sys.argv[3] if len(sys.argv) > 3 else "warm"
    seed = int(sys.argv[4]) if len(sys.argv) > 4 else 0
    wavfile.write(out, SR, make(secs, mood, seed))
