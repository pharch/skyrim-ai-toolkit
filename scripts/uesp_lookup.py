#!/usr/bin/env python3
"""Read-only, on-demand UESP MediaWiki client. NOT a wiki crawler/mirror.

NOTE: API reachability was not verified in this environment (initial 403).
Honor access policies and do not use this to bypass restrictions.
"""
import argparse, json, sys, urllib.parse, urllib.request, urllib.error, time
BASE='https://en.uesp.net/w/api.php'
UA='SkyrimGlitchResearch/0.1 (individual-use source verification; contact via wiki account)'

def query(params):
    args={'format':'json','formatversion':2,**params}
    url=BASE+'?'+urllib.parse.urlencode(args)
    request=urllib.request.Request(url,headers={'User-Agent':UA,'Accept':'application/json'})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request,timeout=20) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if e.code in (429,502,503) and attempt < 2:
                time.sleep((attempt+1)*3)
                continue
            raise RuntimeError(f'UESP API returned HTTP {e.code}. Do not evade restrictions; check permitted access. URL: {BASE}') from e
        except (TimeoutError,urllib.error.URLError) as e:
            raise RuntimeError(f'UESP API unavailable: {e}') from e

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--online', action='store_true', help='explicitly permit an on-demand request to en.uesp.net')
    sub=ap.add_subparsers(dest='op',required=True)
    s=sub.add_parser('search');s.add_argument('terms');s.add_argument('--limit',type=int,default=8)
    p=sub.add_parser('page');p.add_argument('title')
    args=ap.parse_args()
    if not args.online:
        ap.error('network access is opt-in; use python3 -m tools.uesp with the local index, or pass --online explicitly')
    if args.op=='search':
        result=query({'action':'query','list':'search','srsearch':args.terms,'srlimit':max(1,min(20,args.limit)),'srnamespace':0})
        items=[{'title':x.get('title'),'pageid':x.get('pageid'),'timestamp':x.get('timestamp'),'url':'https://en.uesp.net/wiki/'+urllib.parse.quote(x.get('title','').replace(' ','_'),safe=':/')} for x in result.get('query',{}).get('search',[])]
        print(json.dumps({'source':'UESP','items':items},indent=2))
    else:
        res=query({'action':'query','titles':args.title,'prop':'revisions|info','inprop':'url','rvprop':'ids|timestamp|content','rvslots':'main','rvlimit':1})
        items=[]
        for x in res.get('query',{}).get('pages',[]):
            rev=(x.get('revisions') or [{}])[0]
            slot=rev.get('slots',{}).get('main',{})
            items.append({'title':x.get('title'),'pageid':x.get('pageid'),'url':x.get('fullurl'),'revid':rev.get('revid'),'timestamp':rev.get('timestamp'),'wikitext':slot.get('content','')})
        print(json.dumps({'source':'UESP','items':items},ensure_ascii=False,indent=2))

if __name__=='__main__':
    try: main()
    except Exception as e: print(str(e),file=sys.stderr);sys.exit(2)
