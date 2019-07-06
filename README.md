👉 **[Click here if you are looking for `higlass-python`](https://github.com/higlass/higlass-python)! This repo is outdated.** 👍

# hgflask

Lightweight Flask HiGlass Server for dynamic track generation in interactive Python sessions.

## Usage

### Server

Starting a hgflask server:

```
import hgflask.tilesets as hfti
import hgflask.server as hgse

ts = hfti.cooler(
    '../data/Dixon2012-J1-NcoI-R1-filtered.100kb.multires.cool')

server = hgse.start(tilesets=[ts])
```
#### Custom data handlers

If we would like to create our own custom data server, we have to register
the `tileset_info` and `tiles` methods:

```
import math
import numpy as np
import itertools as it

dim = 2000

data = np.zeros((dim, dim))
for x,y in it.product(range(dim), repeat=2):
    data[x][y] = (-(y + 47) * math.sin(math.sqrt(abs(x / 2 + (y+47))))
                             - x * math.sin(math.sqrt(abs(x - (y+47)))))
                             
import functools as ft
import hgtiles.npmatrix as hgnp

import hgflask.server as hgse
import hgflask.tilesets as hfti

ts = hfti.Tileset(
    tileset_info=lambda: hgnp.tileset_info(data),
    tiles=lambda tids: hgnp.tiles_wrapper(data, tids)
)
```
And call `hgflask.start` with this extra information:

```
server = hgse.start([ts])
```

And then we can test the running server:

```
server.tileset_info('a')
```

### Client

The `client` subpackage contains wrappers for HiGlass viewconfig management. Typically used with the [higlass-jupyter](https://github.com/reservoirgenomics/jupyter-higlass) widget.
```
import higlass_jupyter as hiju
import hgflask.client as hgc

conf = hgc.ViewConf([
    hgc.View([
        hgc.Track(track_type='top-axis', position='top'),
        hgc.Track(track_type='left-axis', position='left'),
        hgc.Track(track_type='heatmap', position='center',
                 tileset_uuid=ts.uuid,
                  api_url=server.api_address,
                  height=250,
                 options={ 'valueScaleMax': 0.5 }),

    ])
])

hiju.HiGlassDisplay(viewconf=conf.to_json())
```
