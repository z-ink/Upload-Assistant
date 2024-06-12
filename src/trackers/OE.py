# -*- coding: utf-8 -*-
import asyncio
import requests
from difflib import SequenceMatcher
import json
import os
import platform

from src.trackers.COMMON import COMMON
from src.console import console

class OE():
    def __init__(self, config):
        self.config = config
        self.tracker = 'OE'
        self.source_flag = 'OE'
        self.search_url = 'https://onlyencodes.cc/api/torrents/filter'
        self.upload_url = 'https://onlyencodes.cc/api/torrents/upload'
        self.banned_groups = ['0neshot', '3LT0N', '4K4U', '4yEo', '$andra', '[Oj]', 'AFG', 'AkihitoSubs', 'AniHLS', 'Anime Time', 'AnimeRG', 'AniURL', 'AR', 'AROMA', 'ASW', 'aXXo', 'BakedFish', 'BiTOR', 'BHDStudio', 'BRrip', 'bonkai', 'Cleo', 'CM8', 'C4K', 'CrEwSaDe', 'core', 'd3g', 'DDR', 'DeadFish', 'DeeJayAhmed', 'DNL', 'ELiTE', 'EMBER', 'eSc', 'EVO', 'EZTV', 'FaNGDiNG0', 'FGT', 'fenix', 'FUM', 'FRDS', 'FROZEN', 'GalaxyTV', 'GalaxyRG', 'GERMini', 'Grym', 'GrymLegacy', 'HAiKU', 'HD2DVD', 'HDTime', 'Hi10', 'ION10', 'iPlanet', 'JacobSwaggedUp', 'JIVE', 'Judas', 'KiNGDOM', 'LAMA', 'Leffe', 'LiGaS', 'LOAD', 'LycanHD', 'MeGusta,' 'MezRips,' 'mHD,' 'Mr.Deadpool', 'mSD', 'NemDiggers', 'neoHEVC', 'NeXus', 'NhaNc3', 'nHD', 'nikt0', 'nSD', 'NhaNc3', 'NOIVTC', 'pahe.in', 'PlaySD', 'playXD', 'PRODJi', 'ProRes', 'project-gxs', 'PSA', 'QaS', 'Ranger', 'RAPiDCOWS', 'RARBG', 'Raze', 'RCDiVX', 'RDN', 'Reaktor', 'REsuRRecTioN', 'RMTeam', 'ROBOTS', 'rubix', 'SANTi', 'SHUTTERSHIT', 'SpaceFish', 'SPASM', 'SSA', 'TBS', 'Telly,' 'Tenrai-Sensei,' 'TERMiNAL,' 'TM', 'topaz', 'TSP', 'TSPxL', 'Trix', 'URANiME', 'UTR', 'VipapkSudios', 'ViSION', 'WAF', 'Wardevil', 'x0r', 'xRed', 'XS', 'YakuboEncodes', 'YIFY', 'YTS', 'YuiSubs', 'ZKBL', 'ZmN', 'ZMNT']
        pass
    
    async def upload(self, meta):
        common = COMMON(config=self.config)
        await common.edit_torrent(meta, self.tracker, self.source_flag)
        await common.unit3d_edit_desc(meta, self.tracker)
        cat_id = await self.get_cat_id(meta['category'])
        type_id = await self.get_type_id(meta['type'], meta.get('tv_pack', 0), meta.get('video_codec'), meta.get('category', ""))
        resolution_id = await self.get_res_id(meta['resolution'])
        oe_name = await self.edit_name(meta)
        if meta['anon'] != 0 or self.config['TRACKERS'][self.tracker].get('anon', False):
            anon = 1
        else:
            anon = 0
        if meta['bdinfo'] != None:
            mi_dump = None
            bd_dump = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/BD_SUMMARY_00.txt", 'r', encoding='utf-8').read()
        else:
            mi_dump = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/MEDIAINFO.txt", 'r', encoding='utf-8').read()
            bd_dump = None
        desc = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/[{self.tracker}]DESCRIPTION.txt", 'r').read()
        open_torrent = open(f"{meta['base_dir']}/tmp/{meta['uuid']}/[{self.tracker}]{meta['clean_name']}.torrent", 'rb')
        files = {'torrent': open_torrent}
        data = {
            'name' : await self.get_name(meta),
            'description' : desc,
            'mediainfo' : mi_dump,
            'bdinfo' : bd_dump, 
            'category_id' : cat_id,
            'type_id' : type_id,
            'resolution_id' : resolution_id,
            'tmdb' : meta['tmdb'],
            'imdb' : meta['imdb_id'].replace('tt', ''),
            'tvdb' : meta['tvdb_id'],
            'mal' : meta['mal_id'],
            'igdb' : 0,
            'anonymous' : anon,
            'stream' : meta['stream'],
            'sd' : meta['sd'],
            'keywords' : meta['keywords'],
            'personal_release' : int(meta.get('personalrelease', False)),
            'internal' : 0,
            'featured' : 0,
            'free' : 0,
            'doubleup' : 0,
            'sticky' : 0,
        }
        # Internal
        if self.config['TRACKERS'][self.tracker].get('internal', False) == True:
            if meta['tag'] != "" and (meta['tag'][1:] in self.config['TRACKERS'][self.tracker].get('internal_groups', [])):
                data['internal'] = 1
                
        if meta.get('category') == "TV":
            data['season_number'] = meta.get('season_int', '0')
            data['episode_number'] = meta.get('episode_int', '0')
        headers = {
            'User-Agent': f'Uploadrr ({platform.system()} {platform.release()})'
        }
        params = {
            'api_token': self.config['TRACKERS'][self.tracker]['api_key'].strip()
        }
        
        if not meta['debug']:
            success = 'Unknown'
            try:
                response = requests.post(url=self.upload_url, files=files, data=data, headers=headers, params=params)
                response.raise_for_status()                
                response_json = response.json()
                success = response_json.get('success', False)
                data = response_json.get('data', {})
            except Exception as e:
                console.print(f"[red]Encountered Error: {e}[/red]\n[bold yellow]May have uploaded, please go check..")
            if success == 'Unknown':
                console.print("[bold yellow]Status of upload is unknown, please go check..")
                success = False
            elif success:
                console.print("[bold green]Torrent uploaded successfully!")
            else:
                console.print("[bold red]Torrent upload failed.")

            if data:
                if 'name' in data and 'The name has already been taken.' in data['name']:
                    console.print("[red]Name has already been taken.")
                if 'info_hash' in data and 'The info hash has already been taken.' in data['info_hash']:
                    console.print("[red]Info hash has already been taken.")                
            else:
                console.print("[cyan]Request Data:")
                console.print(data)
    
            try:
                open_torrent.close()
            except Exception as e:
                console.print(f"[red]Failed to close torrent file: {e}[/red]")

            return success 

    def get_language_tag(self, meta):
        lang_tag = ""  
        has_eng_audio = False
        audio_lang = ""
        if meta['is_disc'] != "BDMV":
            try:
                with open(f"{meta.get('base_dir')}/tmp/{meta.get('uuid')}/MediaInfo.json", 'r', encoding='utf-8') as f:
                    mi = json.load(f)
                for track in mi['media']['track']:
                    if track['@type'] == "Audio":
                        if track.get('Language', 'None').startswith('en'):
                            has_eng_audio = True
                        if not has_eng_audio:
                            audio_lang = mi['media']['track'][2].get('Language_String', "").upper()
            except Exception as e:
                print(f"Error: {e}")
        else:
            for audio in meta['bdinfo']['audio']:
                if audio['language'] == 'English':
                    has_eng_audio = True
                if not has_eng_audio:
                    audio_lang = meta['bdinfo']['audio'][0]['language'].upper()
        if audio_lang != "":
            lang_tag = audio_lang
        return lang_tag

    def get_basename(self, meta):
        path = next(iter(meta['filelist']), meta['path'])
        return os.path.basename(path)

    async def get_name(self, meta):
        basename = self.get_basename(meta)
        type = meta.get('type', "")
        title = meta.get('title',"")
        alt_title = meta.get('aka', "")
        year = meta.get('year', "")
        resolution = meta.get('resolution', "")
        if resolution == "OTHER":
            resolution = ""
        audio = meta.get('audio', "")
        lang_tag = self.get_language_tag(meta)
        service = meta.get('service', "")
        season = meta.get('season', "")
        episode = meta.get('episode', "")
        part = meta.get('part', "")
        repack = meta.get('repack', "")
        three_d = meta.get('3D', "")
        tag = meta.get('tag', "")
        if tag == "":
            tag = "- NOGRP"
        source = meta.get('source', "")
        uhd = meta.get('uhd', "")
        hdr = meta.get('hdr', "")
        episode_title = meta.get('episode_title', '')
        if meta.get('is_disc', "") == "BDMV": #Disk
            video_codec = meta.get('video_codec', "")
            region = meta.get('region', "")
        elif meta.get('is_disc', "") == "DVD":
            region = meta.get('region', "")
            dvd_size = meta.get('dvd_size', "")
        else:
            video_codec = meta.get('video_codec', "")
            video_encode = meta.get('video_encode', video_codec)
        edition = meta.get('edition', "")
        cut = meta.get('cut', "")
        ratio = meta.get('ratio', "")

        if meta['category'] == "TV":
            try:
                year = meta['year']
                if not year: 
                    raise ValueError("No TMDB Year Found..trying IMDB")
            except (KeyError, ValueError):
                try:
                    year = meta['imdb_info']['year']
                    if not year:
                        raise ValueError("No IMDB Year Found..")
                except (KeyError, ValueError):
                    year = ""
        if meta.get('no_season', False) is True:
            season = ''
        if meta.get('no_year', False) is True:
            year = ''
        if meta.get('no_aka', False) is True:
            alt_title = ''
        if meta['debug']:
            console.log("[cyan]get_name cat/type")
            console.log(f"CATEGORY: {meta['category']}")
            console.log(f"TYPE: {meta['type']}")
            console.log("[cyan]get_name meta:")
            console.log(meta)

        #YAY NAMING FUN
        if meta['category'] == "MOVIE": #MOVIE SPECIFIC
            if type == "DISC": #Disk
                if meta['is_disc'] == 'BDMV':
                    name = f"{title} [{alt_title}] {year} {three_d} {lang_tag} {cut} {ratio} {edition} {repack} {resolution} {region} {uhd} {source} {hdr} {video_codec} {audio}{tag}"
                    potential_missing = ['edition', 'region', 'distributor']
                elif meta['is_disc'] == 'DVD': 
                    name = f"{title} {alt_title} {year} {lang_tag} {cut} {ratio} {edition} {repack} {source} {dvd_size} {audio}{tag}"
                    potential_missing = ['edition', 'distributor']
                elif meta['is_disc'] == 'HDDVD':
                    name = f"{title} {alt_title} {year} {lang_tag} {cut} {ratio} {edition} {repack} {resolution} {source} {video_codec}] {audio}{tag}"
                    potential_missing = ['edition', 'region', 'distributor']
            elif type == "REMUX" and source in ("BluRay", "HDDVD"): #BluRay/HDDVD Remux
                name = f"{title} {alt_title} {year} {three_d} {lang_tag} {cut} {ratio} {edition} {repack} {resolution} {uhd} {source} REMUX {hdr} {video_codec} {audio}{tag}" 
                potential_missing = ['edition', 'description']
            elif type == "REMUX" and source in ("PAL DVD", "NTSC DVD", "DVD"): #DVD Remux
                name = f"{title} {alt_title} {year} {lang_tag} {cut} {ratio} {edition} {repack} {source} REMUX  {audio}{tag}" 
                potential_missing = ['edition', 'description']
            elif type == "ENCODE": #Encode
                name = f"{title} {alt_title} {year} {lang_tag} {cut} {ratio} {edition} {repack} {resolution} {uhd} {source} {audio} {hdr} {video_encode}{tag}"  
                potential_missing = ['edition', 'description']
            elif type == "WEBDL": #WEB-DL
                name = f"{title} {alt_title} {year} {lang_tag} {cut} {ratio} {edition} {repack} {resolution} {uhd} {service} WEB-DL {audio} {hdr} {video_encode}{tag}"
                potential_missing = ['edition', 'service']
            elif type == "WEBRIP": #WEBRip
                name = f"{title} {alt_title} {year} {lang_tag} {cut} {ratio} {edition} {repack} {resolution} {uhd} {service} WEBRip {audio} {hdr} {video_encode}{tag}"
                potential_missing = ['edition', 'service']
            elif type == "HDTV": #HDTV
                name = f"{title} {alt_title} {year} {lang_tag} {cut} {ratio} {edition} {repack} {resolution} {source} {audio} {video_encode}{tag}"
                potential_missing = []
        elif meta['category'] == "TV": #TV SPECIFIC
            if type == "DISC": #Disk
                if meta['is_disc'] == 'BDMV':
                    name = f"{title} {year} {alt_title} {season}{episode} {three_d} {lang_tag} {cut} {ratio} {edition} {repack} {resolution} {region} {uhd} {source} {hdr} {video_codec} {audio}{tag}"
                    potential_missing = ['edition', 'region', 'distributor']
                if meta['is_disc'] == 'DVD':
                    name = f"{title} {alt_title} {season}{episode} {three_d} {lang_tag} {cut} {ratio} {edition} {repack} {source} {dvd_size} {audio}{tag}"
                    potential_missing = ['edition', 'distributor']
                elif meta['is_disc'] == 'HDDVD':
                    name = f"{title} {alt_title} {year} {lang_tag} {cut} {ratio} {edition} {repack} {resolution} {source} {video_codec} {audio}{tag}"
                    potential_missing = ['edition', 'region', 'distributor']
            elif type == "REMUX" and source in ("BluRay", "HDDVD"): #BluRay Remux
                name = f"{title} {year} {alt_title} {season}{episode} {episode_title} {part} {three_d} {lang_tag} {cut} {ratio} {edition} {repack} {resolution} {uhd} {source} REMUX {hdr} {video_codec} {audio}{tag}" #SOURCE
                potential_missing = ['edition', 'description']
            elif type == "REMUX" and source in ("PAL DVD", "NTSC DVD"): #DVD Remux
                name = f"{title} {year} {alt_title} {season}{episode} {episode_title} {part} {lang_tag} {cut} {ratio} {edition} {repack} {source} REMUX {audio}{tag}" #SOURCE
                potential_missing = ['edition', 'description']
            elif type == "ENCODE": #Encode
                name = f"{title} {year} {alt_title} {season}{episode} {episode_title} {part} {lang_tag} {cut} {ratio} {edition} {repack} {resolution} {uhd} {source} {audio} {hdr} {video_encode}{tag}" #SOURCE
                potential_missing = ['edition', 'description']
            elif type == "WEBDL": #WEB-DL
                name = f"{title} {year} {alt_title} {season}{episode} {episode_title} {part} {lang_tag} {cut} {ratio} {edition} {repack} {resolution} {uhd} {service} WEB-DL {audio} {hdr} {video_encode}{tag}"
                potential_missing = ['edition', 'service']
            elif type == "WEBRIP": #WEBRip
                name = f"{title} {year} {alt_title} {season}{episode} {episode_title} {part} {lang_tag} {cut} {ratio} {edition} {repack} {resolution} {uhd} {service} WEBRip {audio} {hdr} {video_encode}{tag}"
                potential_missing = ['edition', 'service']
            elif type == "HDTV": #HDTV
                name = f"{title} {year} {alt_title} {season}{episode} {episode_title} {part} {lang_tag} {cut} {ratio} {edition} {repack} {resolution} {source} {audio} {video_encode}{tag}"
                potential_missing = []

        
        return ' '.join(name.split())

    async def get_type_id(self, type, tv_pack, video_codec, category):
        type_id = {
            'DISC': '19', 
            'REMUX': '20',
            'WEBDL': '21',
            }.get(type, '0')
        if type  == "WEBRIP":
            if video_codec == "HEVC":
                # x265 Encode
                type_id = '10'
            if video_codec == 'AV1':
                # AV1 Encode
                type_id = '14'
            if video_codec == 'AVC':
                # x264 Encode
                type_id = '15'
        if type == "ENCODE":
            if video_codec == "HEVC":
                # x265 Encode
                type_id = '10'
            if video_codec == 'AV1':
                # AV1 Encode
                type_id = '14'
            if video_codec == 'AVC':
                # x264 Encode
                type_id = '15'
        return type_id

    async def get_res_id(self, resolution):
        resolution_id = {
            '8640p':'10', 
            '4320p': '1', 
            '2160p': '2', 
            '1440p' : '3',
            '1080p': '3',
            '1080i':'4', 
            '720p': '5',  
            '576p': '6', 
            '576i': '7',
            '480p': '8', 
            '480i': '9'
            }.get(resolution, '10')
        return resolution_id



    async def search_existing(self, meta):
        dupes = {}
        console.print("[yellow]Searching for existing torrents on site...")
        params = {
            'api_token' : self.config['TRACKERS'][self.tracker]['api_key'].strip(),
            'tmdbId' : meta['tmdb'],
            'categories[]' : await self.get_cat_id(meta['category']),
            'types[]' : await self.get_type_id(meta['type'], meta.get('tv_pack', 0), meta.get('sd', 0), meta.get('category', "")),
            'resolutions[]' : await self.get_res_id(meta['resolution']),
            'name' : ""
        }
        if meta['category'] == 'TV':
            params['name'] = f"{meta.get('season', '')}{meta.get('episode', '')}"
        if meta.get('edition', "") != "":
            params['name'] + meta['edition']
        try:
            response = requests.get(url=self.search_url, params=params)
            response = response.json()
            for each in response['data']:
                result = each['attributes']['name']
                size = each['attributes']['size']
                dupes[result] = size
        except Exception:
            console.print('[bold red]Unable to search for existing torrents on site. Either the site is down or your API key is incorrect')
            await asyncio.sleep(5)

        return dupes
