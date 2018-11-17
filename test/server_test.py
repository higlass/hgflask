import hgflask.server as hgse
import hgflask.tilesets as hgti
import hgtiles.chromsizes as hgch

def test_server_start():
    '''
    Ensure that the server has started
    '''

    chromsizes = hgch.get_tsv_chromsizes('data/chromSizes_hg19_reordered.tsv')

    ts = [
            hgti.cooler('data/Dixon2012-J1-NcoI-R1-filtered.100kb.multires.cool'),
            hgti.bigwig('data/wgEncodeCaltechRnaSeqHuvecR1x75dTh1014IlnaPlusSignalRep2.bigWig'),
            hgti.bigwig('data/wgEncodeCaltechRnaSeqHuvecR1x75dTh1014IlnaPlusSignalRep2.bigWig',
                chromsizes=chromsizes),
            hgti.chromsizes('data/chromSizes_hg19_reordered.tsv')
        ]

    print("hello")
    server = hgse.Server(ts)
    server.start()

    excepted = False
    try:
        cs = server.chromsizes('nottobefound')
    except:
        excepted = True

    assert(excepted == True)
    
    cs = server.chromsizes(ts[3].uuid).decode('utf8')
    assert(cs.find('chrM') > -1)
    
    # assert('min_pos' in server.tileset_info(ts[0].uuid))
    # assert('dense' in server.tiles(ts[0].uuid, 0, 0, 0))

    # assert('max_pos' in server.tileset_info(ts[0].uuid))
    # assert('dense' in server.tiles(ts[0].uuid, 0, 0))

    # print('tileset_info', server.tileset_info('c'))
    ## stop the server so that the program can exit
    server.stop()
