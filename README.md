# hgflask

Lightweight Flask HiGlass Server for dynamic track generation in interactive Python sessions.

## Usage

### Server

Starting a hgflask server:

```
import hgflask
import hgflask.client as hfc

tilesets = [
    {
        'filepath': 'matrix.mcool',
        'uuid': 'a',
    }
]
server = hgflask.start(tilesets)
print(server.tileset_info('a'))
```
#### Custom data handlers

If we would like to create our own custom data server, we have to register
the `tileset_info` and `tiles` methods:

```
handlers = {
    'tileset_info': ft.partial(tileset_info, hg_points),
    'tiles': ft.partial(tiles_wrapper, hg_points),
}
```
And call `hgflask.start` with this extra information:

```
import hgflask
import functools as ft

handlers = {
    'tileset_info': ft.partial(tileset_info, hg_points),
    'tiles': ft.partial(tiles_wrapper, hg_points),
}

tilesets = [{
    'filetype': 'scatter_points',
    'uuid': 'a'
}]

server = hgflask.start(tilesets, external_filetype_handlers = handlers)
```

And then we can test the running server:

```
server.tileset_info('a')
```

### Client

The `client` subpackage contains wrappers for HiGlass viewconfig management. Typically used with the [higlass-jupyter](https://github.com/reservoirgenomics/jupyter-higlass) widget.
```
hgc = hfc.HiGlassConfig()
view_uid = hgc.add_view()
hgc.add_track(view_uid, 'heatmap', 'center', 
        'http://localhost:{}/api/v1'.format(server.port), 
        'a')

import jupyter_higlass
jupyter_higlass.HiGlassDisplay(viewconf=hgc.to_json_string())
```


![image](https://user-images.githubusercontent.com/2143629/42402390-7e145f96-8148-11e8-8ba6-ae2246c5cc4e.png)


