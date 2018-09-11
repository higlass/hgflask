import json
import slugid

class HiGlassTrack:
    def __init__(self, track_type, position, server=None, 
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
        new_track = {
            'type': track_type,
            'options': options
        }

        if server is not None:
            new_track['server'] = server
        if tileset_uuid is not None:
            new_track['tilesetUid'] = tileset_uuid

        self.viewconf = new_track
        self.position = position

    def to_json(self):
        return self.viewconf

class HiGlassView:
    def __init__(self, uid=None, 
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

        self.tracks = []

        self.viewconf = {
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


    def add_track(self, track_type, position=None, server=None, 
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
        new_track = HiGlassTrack(track_type, position, 
                server, tileset_uuid, options)

        self.tracks += [new_track]

    def to_json(self):
        '''
        Convert the existing configuration to a JSON representation.
        '''
        viewconf = json.loads(json.dumps(self.viewconf))

        for track in self.tracks:
            viewconf['tracks'][track.position] += [track.to_json()]

        return viewconf


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

        self.views = []
        
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
        view = HiGlassView(uid, width, height, x, y)

        for view in self.views:
            if view['uid'] == uid:
                raise ValueError("View with this uid already exists")

        self.views += [view]
        return view
    
    def location_lock(self, view_uid1, view_uid2):
        '''
        Add a location lock between two views.
        '''
        pass
    
    def to_json_string(self):
        viewconf = json.loads(json.dumps(self.viewconf))

        for view in self.views:
            viewconf['views'] += [view.to_json()]

        return json.dumps(
            viewconf
        )
