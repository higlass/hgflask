# hgflask

Lightweight Flask HiGlass Server for dynamic track generation in interactive Python sessions.

## Usage

```
import functools as ft
import hgtiles
import hgtiles.cooler as hgco
import hgflask
import multiprocessing as mp
import os.path as op
import slugid
from hgflask import create_app

TILESETS = [{  
    'uuid': "abc",
    'filetype': "grid_1000",
    'datatype': "matrix",
    },
    {  
    'uuid': "abc1",
    'filetype': "grid_8000",
    'datatype': "matrix",
    },
]

# check if we're already keeping track of any processes
try:
    processes
except Exception:
    processes = {}
    
for puid in processes:
    processes[puid].terminate()


# we're going to assign a uuid to each server process so that if anything
# goes wrong, the variable referencing the process doesn't get lost
app = create_app(tilesets=TILESETS, external_filetype_handlers=filetype_handlers)

port=get_open_port()
uuid = slugid.nice().decode('utf8')
processes[uuid] = mp.Process(
    target=ft.partial(app.run, 
                      debug=True, 
                      port=port, 
                      host='0.0.0.0',
                      use_reloader=False))
processes[uuid].start()
```

## hgflask.client

The `client` subpackage contains wrappers for HiGlass viewconfig management. Typicall used with the [higlass-jupyter](https://github.com/reservoirgenomics/jupyter-higlass) widget.
```
hgc = hfc.HiGlassConfig()

# create two views, each occupying half of the 12 unit wide grid
view1 = hgc.add_view(x=0, width=6)
view2 = hgc.add_view(x=6, width=6)

# Add a track to the first view
hgc.add_track(view1, 'heatmap', 'center', 'http://higlass.io/api/v1', 'CQMd6V_cRw6iCI_-Unl3PQ')
```

Start the widget:

```
import jupyter_higlass
jupyter_higlass.HiGlassDisplay(viewconf=hgc.to_json_string())
```


![image](https://user-images.githubusercontent.com/2143629/42402390-7e145f96-8148-11e8-8ba6-ae2246c5cc4e.png)


