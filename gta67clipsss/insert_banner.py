"""Insert an ad banner into a vertical clip.

Rules: the banner plays in full, with its sound, at the middle of every minute (0:30, 1:30, 2:30, ...);
a clip shorter than a minute gets it once, in the middle. While the banner plays the main video is paused
(frozen frame, its sound muted). The banner is 100% opaque, full width (about 30% of the screen),
centred vertically. No speed-up (1.0x, under the 1.1x limit).

usage: python insert_banner.py <clip.mp4> <banner.mov> <out.mp4> [--crop W:H:X:Y]
"""
import argparse, json, subprocess, sys


def dur(path):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", path],
                       capture_output=True, text=True, check=True)
    return float(json.loads(r.stdout)["format"]["duration"])


def points(d):
    if d < 60:
        return [d / 2]
    out, t = [], 30.0
    while t < d - 1:
        out.append(t)
        t += 60
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("clip"); ap.add_argument("banner"); ap.add_argument("out")
    ap.add_argument("--crop", default="1320:712:0:1076", help="banner area inside the banner video (W:H:X:Y)")
    a = ap.parse_args()
    D, B = dur(a.clip), dur(a.banner)
    pts = points(D)
    n = len(pts)
    edges = [0.0] + pts + [D]
    f = []
    # main video and audio split into n+1 parts, plus a frozen frame at every insertion point
    f.append(f"[0:v]fps=30,scale=1080:1920,setsar=1,split={2 * n + 1}" + "".join(f"[v{i}]" for i in range(2 * n + 1)))
    f.append(f"[0:a]aresample=48000,aformat=channel_layouts=stereo,asplit={n + 1}" + "".join(f"[a{i}]" for i in range(n + 1)))
    # banner: crop the ad strip, full width, opaque; sound normalised to the clip loudness (-14 LUFS)
    f.append(f"[1:v]crop={a.crop},scale=1080:-2,fps=30,setsar=1,format=yuv420p,split={n}" + "".join(f"[bv{i}]" for i in range(n)))
    f.append(f"[1:a]loudnorm=I=-14:TP=-1.5:LRA=11,aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{B:.3f},asplit={n}"
             + "".join(f"[ba{i}]" for i in range(n)))
    seq = []
    for i in range(n + 1):
        s, e = edges[i], edges[i + 1]
        f.append(f"[v{2 * i}]trim={s:.3f}:{e:.3f},setpts=PTS-STARTPTS[pv{i}]")
        f.append(f"[a{i}]atrim={s:.3f}:{e:.3f},asetpts=PTS-STARTPTS[pa{i}]")
        seq.append(f"[pv{i}][pa{i}]")
        if i < n:
            t = pts[i]
            # pause: hold the frame at t for the whole banner, banner on top in the middle
            f.append(f"[v{2 * i + 1}]trim={t:.3f}:{t + 0.05:.3f},setpts=PTS-STARTPTS,tpad=stop_mode=clone:stop_duration={B + 1:.3f},"
                     f"trim=0:{B:.3f},setpts=PTS-STARTPTS[fz{i}]")
            f.append(f"[bv{i}]setpts=PTS-STARTPTS[bs{i}]")
            f.append(f"[fz{i}][bs{i}]overlay=x=(W-w)/2:y=(H-h)/2:eof_action=repeat,trim=0:{B:.3f},setpts=PTS-STARTPTS[bo{i}]")
            f.append(f"[ba{i}]asetpts=PTS-STARTPTS[bb{i}]")
            seq.append(f"[bo{i}][bb{i}]")
    f.append("".join(seq) + f"concat=n={len(seq)}:v=1:a=1[v][a]")
    cmd = ["ffmpeg", "-y", "-v", "error", "-i", a.clip, "-i", a.banner, "-filter_complex", ";".join(f),
           "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-r", "30", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", a.out]
    subprocess.run(cmd, check=True)
    print(f"{a.out}: clip {D:.1f}s, banner {B:.2f}s at " + ", ".join(f"{p:.1f}s" for p in pts) + f", total {dur(a.out):.1f}s")


if __name__ == "__main__":
    sys.exit(main())
