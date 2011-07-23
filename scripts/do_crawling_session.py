
import argparse
import csxj.crawler


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Fetch pages from news sources, dumps interesting data')
    parser.add_argument('--debug', dest='debug', action='store_true', help="run crawler in debug mode")
    parser.add_argument('--outdir', type=str, dest='outdir', required=True, help='directory to dump the json db in')

    args = parser.parse_args()
    DEBUG_MODE = args.debug
    csxj.crawler.main(args.outdir)

