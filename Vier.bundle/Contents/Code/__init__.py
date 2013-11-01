import re, string

VIER_URL	  = 'http://www.vier.be/'
VIER_PROGRAMMA_VIDEO_URL = 'http://www.vier.be/%s/videos/%s'
VIER_VIDEO_STREAMING_URL = 'http://streaming.sbsbelgium.be/%s.mp4'
VIER_BACKGROUND_URL = 'http://www.vier.be/sites/default/files/takeover/%s/bg_%s.jpg'       


ICON = 'vier_logo.png'
ART = 'art-default.png'

####################################################################################################
def Start():

  Plugin.AddPrefixHandler('/video/vier', MainMenu, 'Vier', ICON, ART)
  Plugin.AddViewGroup('InfoList', viewMode='InfoList', mediaType='items')
  ObjectContainer.title1 = 'Vier'
  ObjectContainer.content = ContainerContent.GenericVideos
  ObjectContainer.art = R(ART)
  DirectoryObject.thumb = R(ICON)
  VideoClipObject.thumb = R(ICON)
  VideoClipObject.art = R(ART)
  HTTP.CacheTime = 1800

####################################################################################################
def MainMenu():

  oc = ObjectContainer(
    objects = [
      DirectoryObject(
        key     = Callback(GetItemList, url='', title2='Videos'),
        title   = L('Videos')
#      ),
#      DirectoryObject(
#        key     = Callback(GetProgramList, url='programmas', title2='Programmas'),
#        title   = L('Programmas')
      )
    ]
  )                                 
  # append programs list directly
  oc = GetProgramList(url="programmas", oc=oc)
  oc = GetProgramList(url="programmas/categorieen/sport", oc=oc)
  return oc

####################################################################################################

#def GetProgramList(url, title2):
def GetProgramList(url, oc):
  #oc = ObjectContainer(title2=title2, view_group='InfoList')
  html = HTML.ElementFromURL(VIER_URL + url)
  programs = html.xpath('.//div[contains(@class, "node-programma")]')
  for program in programs:
    program_url = program.xpath(".//a")[1].get("href").split('/')[1].replace('-', '')
    if program_url == "tnogver":
      program_url = "istnogver" 
    Log.Info(program_url)
    title = program.xpath(".//a")[1].text
    Log.Info(title)
    img = program.xpath(".//img")[0].get("pagespeed_lazy_src")
    Log.Info(img)
    do = DirectoryObject(key = Callback(GetItemList, url=program_url, title2=title), title = title, thumb=img, art=Resource.ContentsOfURLWithFallback(VIER_BACKGROUND_URL % (program_url, program_url), fallback=R(ART)))
    oc.add(do)
  return oc 
	
def GetItemList(url, title2, page=''):
  Log.Exception('GetItemList')
  cookies = HTTP.CookiesForURL(VIER_URL)
  unsortedVideos = {}
  oc = ObjectContainer(title2=title2, view_group='InfoList', http_cookies=cookies)
  Log.Exception('videos')
  html = HTML.ElementFromURL(VIER_PROGRAMMA_VIDEO_URL % (url, page))
  videos = html.xpath('.//div[contains(@class, "node-video")]')
  Log.Info(videos)
  for video in videos:
    Log.Info("video:")
    try:
      video_page_url = VIER_PROGRAMMA_VIDEO_URL % (url, video.xpath(".//a")[0].get("href"))
      title = video.xpath(".//a")[1].text
      img = video.xpath(".//img")[0].get("pagespeed_lazy_src")
      sort = video_page_url.split('/')[-1] 
      Log.Info(video_page_url)
      try:
        int(sort)  
        unsortedVideos[sort] = VideoClipObject(url = video_page_url, title = title, thumb=img)
      except:
        Log.Exception("not a nummeric key, video not added")
    except:
      Log.Exception("error adding VideoClipObject")
      pass
      
  keys = unsortedVideos.keys()
  Log.Info(keys)
  keys.sort(reverse=True,key=int)

  for key in keys:
    oc.add(unsortedVideos[key])

  pager = html.xpath('.//li[@class="pager-next"]')
  Log.Info(pager)
  Log.Info(html.xpath('.//li[@class="pager-next"]//a'))
  if pager:
    page_url = html.xpath('.//li[@class="pager-next"]//a')[0].get('href').split('?')[-1]
    Log.Info(page_url)
    # add "next page"
    oc.add(DirectoryObject(key=Callback(GetItemList, url=url, page='?'+page_url, title2='Volgende...'), title   = L('Volgende...')))
  
  return oc