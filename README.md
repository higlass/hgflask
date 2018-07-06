# hgflask

Lightweight Flask HiGlass Server for dynamic track generation in interactive Python sessions.

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

![image](https://user-images.githubusercontent.com/2143629/42402390-7e145f96-8148-11e8-8ba6-ae2246c5cc4e.png)
