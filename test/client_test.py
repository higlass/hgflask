import hgflask.client as hgc

def test_client1():
    viewconf = hgc.ViewConf()
    view = viewconf.add_view()
    track = view.add_track(
            track_type='matrix', 
            position='center',
            tileset_uuid='a',
            api_url='localhost:8989')

    result = viewconf.to_dict()

    print('result:', result)
