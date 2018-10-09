import json
import slugid

class Track:
    def __init__(self, track_type, position, tileset_uuid=None, 
            api_url=None, height=None, width=None, options={}):
        '''
        Add a track to a position.
        
        Parameters
        ----------
        track_type: string
            The type of track to add (e.g. "heatmap", "line")
        position: string
            One of 'top', 'bottom', 'center', 'left', 'right'
        tileset_uuid:
            The of uuid of the tileset being displayed in this track
        api_url: string
            The server storing the data for this track
        height: int 
            The height of the track (in pixels)
        width: int 
            The width of the track (in pixels)
        options: {} 
            The options to pass onto the track
        '''
        new_track = {
            'type': track_type,
            'options': options
        }

        if api_url is not None:
            new_track['server'] = api_url
        if tileset_uuid is not None:
            new_track['tilesetUid'] = tileset_uuid
        if height is not None:
            new_track['height'] = height
        if width is not None:
            new_track['width'] = width

        self.viewconf = new_track
        self.position = position

    def to_json(self):
        return self.viewconf

class View:
    def __init__(self, tracks=[],
                 x=0, y=0, 
                 width=12, 
                 height=6,
                 initialXDomain=None, 
                 initialYDomain=None,
                 uid=None):
        '''
        Add a new view
        
        Parameters
        --------
        tracks: []
            A list of Tracks to include in this view
        x: int
            The position of this view on the grid
        y: int
            The position of this view on the grid
        width: int
            The width of this of view on a 12 unit grid
        height: int
            The height of the this view. The height is proportional
            to the height of all the views present.
        initialXDoamin: [int, int]
            The initial x range of the view
        initialYDomain: [int, int]
            The initial y range of the view
        uid: string
            The uid of new view
        '''
        if uid is None:
            uid = slugid.nice().decode('utf8')

        self.tracks = tracks
        self.uid = uid

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

        if initialXDomain is not None:
            self.viewconf['initialXDomain'] = initialXDomain
        if initialYDomain is not None:
            self.viewconf['initialYDomain'] = initialYDomain


    def add_track(self, *args, **kwargs):
        '''
        Add a track to a position.
        
        Parameters
        ----------
        track_type: string
            The type of track to add (e.g. "heatmap", "line")
        position: string
            One of 'top', 'bottom', 'center', 'left', 'right'
        tileset: hgflask.tilesets.Tileset
            The tileset to be plotted in this track
        server: string
            The server serving this track
        height: int  
            The height of the track, if it is a top, bottom or a center track
        width: int 
            The width of the track, if it is a left, right or a center track
        '''
        new_track = Track(*args, **kwargs)

        self.tracks += [new_track]

    def to_json(self):
        '''
        Convert the existing track to a JSON representation.
        '''
        viewconf = json.loads(json.dumps(self.viewconf))

        for track in self.tracks:
            viewconf['tracks'][track.position] += [track.to_json()]

        return viewconf


class ViewConf:
    def __init__(self, views=[]):
        self.viewconf = {
        'editable': True,
        'views': [],
          "trackSourceServers": [
            "http://higlass.io/api/v1"
          ],
          "exportViewUrl": "http://higlass.io/api/v1/viewconfs"
        }

        self.views = views
        
        pass
    
    def add_view(self, *args, **kwargs):
        '''
        Add a new view
        
        Parameters
        ----------
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
        initialXDoamin: [int, int]
            The initial x range of the view
        initialYDomain: [int, int]
            The initial y range of the view
        '''
        new_view = View(*args, **kwargs)

        for view in self.views:
            if view.uid == uid:
                raise ValueError("View with this uid already exists")

        self.views += [new_view]
        return new_view
    
    def location_lock(self, view_uid1, view_uid2):
        '''
        Add a location lock between two views.
        '''
        pass

    def to_json(self):
        viewconf = json.loads(json.dumps(self.viewconf))

        for view in self.views:
            viewconf['views'] += [view.to_json()]

        return viewconf
    
