import hgflask.client as hgc

def test_client1():
    viewconf = hgc.HiGlassConfig()
    view = viewconf.add_view()
    track = view.add_track('matrix', 
            position='center',
            server='localhost:8989',
            tileset_uuid='a')

    result = viewconf.to_json_string()

    print('result:', result)
