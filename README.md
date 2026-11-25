# News Image — 25 November 2026

[![make.fun](https://make.fun/badge.svg)](https://make.fun/bounty/news-image-20261125)

Entry for the [make.fun bounty "Sum up 25 November's world news in one image"](https://make.fun/bounty/news-image-20261125) — a program that draws a one-page newspaper front page (1024×1024 PNG) summing up Wednesday 25 November 2026 in six stories:

1. Ukrainian drones hit Russian ships in the Gulf of Finland
2. Cyberattack hits the CIA and the ODNI
3. Huawei found guilty on 10 of 12 trade-secret counts in the US
4. Houthi drone hits a tower in Riyadh, 11 injured
5. NATO sends early-warning aircraft to Poland
6. WHO evacuates Ebola staff in Congo

## How it works

`main.py` is pure Python 3 stdlib — no Pillow, no network, no copied
assets. It contains a hand-written 5×7 bitmap font and a small PNG
encoder (zlib + CRC chunks), and draws the whole front page — masthead,
six colour-banded story panels, footer — pixel by pixel at run time.
The output is fully deterministic: two runs write byte-identical files.

## Run it

```sh
python3 main.py            # writes /output/entry.png
python3 main.py out.png    # writes to a path of your choice
```

The image is 1024×1024 and under 1 MiB, as the bounty requires.

## License

MIT — see [LICENSE](LICENSE).
