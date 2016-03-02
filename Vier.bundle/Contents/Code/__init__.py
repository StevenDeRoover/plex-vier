import re, string

VIER_URL = 'http://www.vier.be'

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

  oc = ObjectContainer()

  # append programs list directly
  oc = GetProgramList(url="/programmas", oc=oc)
  oc = GetProgramList(url="/programmas/categorieen/sport", oc=oc)
  return oc

####################################################################################################

def GetProgramList(url, oc):

    # Request the URL
    html = HTML.ElementFromURL(VIER_URL + url)
    programs = html.xpath('.//div[contains(@class, "region-content")]//div[contains(@class, "node-programma")]')
    for program in programs:
        program_url = program.xpath(".//a")[0].get("href")
        Log.Info(program_url)
        title = program.xpath('.//h3')[0].text
        Log.Info(title)
        img = program.xpath(".//img")[0].get("src")
        Log.Info(img)
        do = DirectoryObject(
            key = Callback(GetItemList, url=program_url, title=title),
            title = title,
            thumb = img,
#            art = Resource.ContentsOfURLWithFallback(VIER_BACKGROUND_URL % (program_url, program_url), fallback=R(ART))
        )
        oc.add(do)

    return oc

def GetItemList(url, title):

    cookies = HTTP.CookiesForURL(VIER_URL)
    oc = ObjectContainer(title1=title, view_group='InfoList', http_cookies=cookies)

    # Find the correct URL after redirection
    html = HTML.ElementFromURL(VIER_URL + url)
    real_url = html.xpath("//head//link[@rel='canonical']")[0].get('href')

    # Request the URL
    html = HTML.ElementFromURL(real_url + '/videos')

    videos = html.xpath('.//div[contains(@class, "node-video")]')
    for video in videos:
        try:
            video_page_url = VIER_URL + video.xpath(".//a")[0].get("href")
            title = video.xpath(".//h3//a")[0].text
            img = video.xpath(".//img")[0].get("src")
            Log.Info(video_page_url)

            oc.add(
                VideoClipObject(
                    url = video_page_url,
                    title = title,
                    thumb = img
                )
            )
        except:
            Log.Exception("error adding VideoClipObject")
            pass
      
#    pager = html.xpath('.//li[@class="pager-next"]')
#    Log.Info(pager)
#    Log.Info(html.xpath('.//li[@class="pager-next"]//a'))
#    if pager:
#        page_url = html.xpath('.//li[@class="pager-next"]//a')[0].get('href').split('?')[-1]
#        Log.Info(page_url)
#        # add "next page"
#        oc.add(DirectoryObject(key=Callback(GetItemList, url=url, page='?'+page_url, title2='Volgende...'), title   = L('Volgende...')))

    return oc