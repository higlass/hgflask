# hgflask

Lightweight Flask HiGlass Server for dynamic track generation in interactive Python sessions.

## Usage

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

## hgflask.client

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


