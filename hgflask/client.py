import json
import slugid

class HiGlassConfig:
    def __init__(self):
        self.viewconf = {
        'editable': True,
        'views': [],
          "trackSourceServers": [
            "http://higlass.io/api/v1"
          ],
          "exportViewUrl": "http://higlass.io/api/v1/viewconfs"
        }
        
        pass
    
    def add_view(self, uid=None, 
                 width=12, 
                 height=6,
                 x=0, y=0):
        '''
        Add a new view
        
        Parameters:
        -----------
        uid: The uid of the view
        
        Returns:
        --------
        uid: string
            The uid of new view
        width: int
            The width of this of view on a 12 unit grid
        height: int
            The height of the this view. The height is proportional
            to the height of all the views present.
        x: int
            The position of this view on the grid
        y: int
            The position of this view on the grid
        '''
        if uid is None:
            uid = slugid.nice().decode('utf8')
            
        for view in self.viewconf['views']:
            if view['uid'] == uid:
                raise ValueError("View with this uid already exists")
            
        self.viewconf['views'] += [
            {
                'uid': uid,
                'tracks': {
                    'top': [],
                    'center': [],
                    'left': [],
                    'right': [],
                    'bottom': []
                },
                "layout": {
                    "w": width,
                    "h": height,
                    "x": x,
                    "y": y
                  },
            }
        ]
        
        return uid
    
    def add_track(self, view_uid, track_type, position, server=None, 
            tileset_uuid=None, options={}):
        '''
        Add a track to a position.
        
        Parameters
        ----------
        view_uid: string
            The identifier for the view to add this track to
        track_type: string
            The type of track to add (e.g. "heatmap", "line")
        position: string
            One of 'top', 'bottom', 'center', 'left', 'right'
        server: string
            The server storing the data for this track
        tileset_uuid:
            The uuid of the track on the server
        '''
        selected_view = None
        for view in self.viewconf['views']:
            if view['uid'] == view_uid:
                selected_view = view
        
        if view is None:
            raise ValueError("View with specified uid doesn't exist. Try calling add_view({}".format(view_uid))
        
        if position not in selected_view['tracks']:
            raise ValueError('Track position must be one of:', 
                             selected_view['tracks'].keys())
    
        new_track = {
            'type': track_type,
            'options': options
        }

        if server is not None:
            new_track['server'] = server
        if tileset_uuid is not None:
            new_track['tilesetUid'] = tileset_uuid

        selected_view['tracks'][position] += [new_track]
    
    def to_json_string(self):
        return json.dumps(
            self.viewconf
        )
