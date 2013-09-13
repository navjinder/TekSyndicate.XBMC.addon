#!/usr/bin/python
# -*- coding: utf-8 -*-
import urllib,urllib2,re,xbmcplugin,xbmcgui,sys,xbmcaddon,socket

socket.setdefaulttimeout(30)
pluginhandle = int(sys.argv[1])
xbox = xbmc.getCondVisibility("System.Platform.xbox")
addon = xbmcaddon.Addon(id='plugin.video.teksyndicatecom')
translation = addon.getLocalizedString
forceViewMode=addon.getSetting("forceViewMode")
viewMode=str(addon.getSetting("viewMode"))

def index():
        addDir(translation(30001),"https://teksyndicate.com/content/video",'listVideos',"")
        addDir(translation(30004),"https://teksyndicate.com/content/review",'listVideos',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode=="true":
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def listVideos(url):
        content = getUrl(url)
        spl=content.split('<div class="feed-image')
        for i in range(1,len(spl),1):
            entry=spl[i]
            match=re.compile('href="(.+?)"', re.DOTALL).findall(entry)
            url=match[0]
            match=re.compile('src="(.+?)"', re.DOTALL).findall(entry)
            thumb=match[0]
            match=re.compile(' href="/users/(.+?)"', re.DOTALL).findall(entry)
            useri=match[0]
            match=re.compile('<div class="feed-cn"(.+?)</div>', re.DOTALL).findall(entry)
            desc=""
            if len(match)>0:
              desc=match[0]
            feedtype=""
            match=re.compile('class="feed-type">(.+?)<', re.DOTALL).findall(entry)
            if len(match)>0:
              feedtype=match[0]
            match=re.compile('href="/(.+?)"', re.DOTALL).findall(entry)
            title=match[0]
            if feedtype!="":
              title=title+" ("+feedtype+") by "+useri
            title=cleanTitle(title)
            addDir(title,'https://teksyndicate.com/'+url,'playVideo',thumb,desc)
        match=re.compile('<li class="next last"><a title="Go to next page" href="(.+?)">(.+?)</a>', re.DOTALL).findall(content)
        for url, title in match:
          if title=="next ›":
            addDir(translation(30002),'https://teksyndicate.com/'+url,'listVideos',"")
        xbmcplugin.endOfDirectory(pluginhandle)
        if forceViewMode=="true":
          xbmc.executebuiltin('Container.SetViewMode('+viewMode+')')

def playVideo(url):
          content = getUrl(url)
          match0=re.compile('src="http://www.youtube.com/embed/videoseries\\?list=(.+?)&', re.DOTALL).findall(content)
          match1=re.compile('src="http://www.youtube.com/embed/(.+?)\\?', re.DOTALL).findall(content)
          match2=re.compile('src="http://www.youtube.com/p/(.+?)\\?', re.DOTALL).findall(content)
          url=""
          if len(match0)>0:
            pl=match0[0]
            if '"' in pl:
              pl=pl[:pl.find('"')]
            playYoutubePlaylist(pl)
            url="pl"
          elif len(match1)>0:
            url = getYoutubeUrl(match1[0])
          elif len(match2)>0:
            playYoutubePlaylist(match2[0])
            url="pl"
          if url!="":
            if url!="pl":
              xbmc.Player().play(url)
          else:
            xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30003)+',5000)')

def playYoutubePlaylist(id):
          ids=[]
          titles=[]
          content = getUrl("http://gdata.youtube.com/feeds/api/playlists/"+id)
          spl=content.split('<media:player')
          playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
          playlist.clear()
          if len(spl)>1:
            for i in range(1,len(spl),1):
                entry=spl[i]
                match=re.compile('v=(.+?)&', re.DOTALL).findall(entry)
                url=getYoutubeUrl(match[0])
                match=re.compile("<media:title type='plain'>(.+?)</media:title>", re.DOTALL).findall(entry)
                listitem = xbmcgui.ListItem(match[0])
                playlist.add(url,listitem)
            xbmc.Player().play(playlist)
          else:
            xbmc.executebuiltin('XBMC.Notification(Info:,'+translation(30003)+',5000)')

def getYoutubeUrl(id):
          if xbox==True:
            url = "plugin://video/YouTube/?path=/root/video&action=play_video&videoid=" + id
          else:
            url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + id
          return url

def cleanTitle(title):
        return title.replace("&lt;","<").replace("&gt;",">").replace("&amp;","&").replace("&#038;","&").replace("&#39;","'").replace("&#039;","'").replace("&#8211;","-").replace("&#8220;","-").replace("&#8221;","-").replace("&#8217;","'").replace("&quot;","\"").replace("-"," ").replace("reviews/"," ").replace("videos/"," ").replace("2013/"," ").strip().upper()

def getUrl(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:19.0) Gecko/20100101 Firefox/19.0')
        response = urllib2.urlopen(req)
        link=response.read()
        response.close()
        return link

def getRedirectedUrl(url):
        req = urllib2.Request(url)
        req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; rv:19.0) Gecko/20100101 Firefox/19.0')
        response = urllib2.urlopen(req)
        response.close()
        return str(response.geturl())

def parameters_string_to_dict(parameters):
        ''' Convert parameters encoded in a URL to a dict. '''
        paramDict = {}
        if parameters:
            paramPairs = parameters[1:].split("&")
            for paramsPair in paramPairs:
                paramSplits = paramsPair.split('=')
                if (len(paramSplits)) == 2:
                    paramDict[paramSplits[0]] = paramSplits[1]
        return paramDict

def addDir(name,url,mode,iconimage,desc=""):
        u=sys.argv[0]+"?url="+urllib.quote_plus(url)+"&mode="+str(mode)
        ok=True
        liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name, "Plot": desc } )
        ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True)
        return ok

params=parameters_string_to_dict(sys.argv[2])
mode=params.get('mode')
url=params.get('url')
if type(url)==type(str()):
  url=urllib.unquote_plus(url)

if mode == 'listChannelVideos':
    listChannelVideos(url)
elif mode == 'listVideos':
    listVideos(url)
elif mode == 'listChannel':
    listChannel(url)
elif mode == 'playVideo':
    playVideo(url)
else:
    index()
