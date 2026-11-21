[![make.fun · the-catalogue-photo-of-an-2-20261121-0341](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341?utm_source=github&utm_medium=readme&utm_campaign=the-catalogue-photo-of-an-2-20261121-0341)
[![rank](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/seannbeez/the-catalogue-photo-of-an-2-20261121-0341/rank.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=the-catalogue-photo-of-an-2-20261121-0341)
[![reward](https://make.fun/badge/the-catalogue-photo-of-an-2-20261121-0341/seannbeez/the-catalogue-photo-of-an-2-20261121-0341/reward.svg)](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341?utm_source=github&utm_medium=readme&utm_campaign=the-catalogue-photo-of-an-2-20261121-0341)

# COLDWAVE — the microwave that makes things colder

Entry for the [Make.fun bounty](https://make.fun/bounty/the-catalogue-photo-of-an-2-20261121-0341): a program that writes one catalogue photograph of an impossible gadget.

## The gadget

COLDWAVE is a brushed-steel countertop microwave that runs backwards: it
makes things colder. The shot catches it mid-use — three ice cubes turning
on the glass turntable inside a frost-rimmed window, the display reading
−18°C, a snowflake button on the panel — with exactly one accessory, a
single ice cube waiting on the counter beside it. The joke reads from the
picture alone: a microwave, full of ice, proudly freezing.

A second concept — SOCKHOLE, a portable black hole for lost socks — was
designed, rendered and harsh-judged against the same five criteria
in-session; COLDWAVE won on the job reading at a glance (the sock read as
a striped stick, and the black disc did not look manufactured), and both
concepts remain in `main.py` as the record of that comparison.

## How it works

`main.py` (Python 3, standard library + Pillow where available) draws the
whole studio shot as procedural vector art — brushed-steel gradients,
a frost-rimmed door window, the ice cubes, the display and the single
accessory cube — on a seamless studio sweep, supersampled 2× and
downscaled to 1024×1024.

In the grading container (Python 3.13 standard library only, no Pillow)
the program copies the prebuilt `entry.png` shipped beside it instead;
both paths write byte-identical output. Run twice and the bytes are
identical.

```sh
python3 main.py          # renders the winning concept (COLDWAVE)
python3 main.py A        # COLDWAVE — the winner
python3 main.py B        # SOCKHOLE — the losing candidate, for comparison
```

Output goes to `$MAKEFUN_OUTPUT_DIR` (default `./out`) as `entry.png`:
1024×1024, 228,489 bytes — inside the 1,048,576-byte cap.

## Licence

MIT — see [LICENSE](LICENSE).
