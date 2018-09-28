import hgflask

print("yo")

def test_server_start():
    '''
    Ensure that the server has started
    '''
    tilesets = [
        {
            'filepath': 'data/Dixon2012-J1-NcoI-R1-filtered.100kb.multires.cool',
            'uuid': 'a',
        },
        {
            'filepath': 'data/wgEncodeCaltechRnaSeqHuvecR1x75dTh1014IlnaPlusSignalRep2.bigWig',
            'uuid': 'b',
        },
        {
            'filepath': 'http://hgdownload.cse.ucsc.edu/goldenpath/hg19/encodeDCC/wgEncodeSydhTfbs/wgEncodeSydhTfbsGm12878InputStdSig.bigWig',
            'uuid': 'c',
        },

    ]
    print("hello")
    server = hgflask.start(tilesets)

    print("hi")
    assert('min_pos' in server.tileset_info('a'))
    assert('dense' in server.tiles('a', 0, 0, 0))

    assert('max_pos' in server.tileset_info('b'))
    assert('dense' in server.tiles('b', 0, 0))

    # print('tileset_info', server.tileset_info('c'))
    ## stop the server so that the program can exit
    server.stop()
