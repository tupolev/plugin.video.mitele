# -*- coding: utf-8 -*-
#------------------------------------------------------------
import urlparse,urllib2,urllib,re
import os
import sys
from core import scrapertools
from core import config
from core import logger
from core.item import Item

DEBUG = True
CHANNELNAME = "channelselector"

def getmainlist(preferred_thumb=""):
    logger.info("channelselector.getmainlist")
    itemlist = []

    itemlist.append( Item(title="Canales" , channel="channelselector" , action="channeltypes", thumbnail=urlparse.urljoin(get_thumbnail_path(preferred_thumb),"menu/channels.png")) )
    return itemlist

def mainlist(params,url,category):
    logger.info("channelselector.mainlist")

    # Verifica actualizaciones solo en el primer nivel
    if config.get_platform()!="boxee":
        try:
            from core import updater
        except ImportError:
            logger.info("channelselector.mainlist No disponible modulo actualizaciones")
        else:
            if config.get_setting("updatecheck2") == "true":
                logger.info("channelselector.mainlist Verificar actualizaciones activado")
                updater.checkforupdates()
            else:
                logger.info("channelselector.mainlist Verificar actualizaciones desactivado")

    itemlist = getmainlist("squares")
    for elemento in itemlist:
        logger.info("channelselector item="+repr(elemento))
        addfolder(elemento.title , elemento.channel , elemento.action , thumbnailname=elemento.thumbnail, folder=elemento.folder)

    # Label (top-right)...
    import xbmcplugin
    #xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    #xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

    if config.get_setting("forceview")=="true":
        # Confluence - Thumbnail
        import xbmc
        xbmc.executebuiltin("Container.SetViewMode(500)")

def getchanneltypes():
    logger.info("channelselector.getchanneltypes")
    itemlist = []
    itemlist.append( Item( title=config.get_localized_string(30121) , channel="channelselector" , action="listchannels" , category="*"   , thumbnail="channels"))
    itemlist.append( Item( title=config.get_localized_string(30129) , channel="channelselector" , action="listchannels" , category="N"   , thumbnail="channels-national"))
    itemlist.append( Item( title=config.get_localized_string(30130) , channel="channelselector" , action="listchannels" , category="R"   , thumbnail="channels-regional"))
    itemlist.append( Item( title=config.get_localized_string(30132) , channel="channelselector" , action="listchannels" , category="T"   , thumbnail="channels-thematic"))
    itemlist.append( Item( title=config.get_localized_string(30133) , channel="channelselector" , action="listchannels" , category="I"   , thumbnail="channels-children"))
    #itemlist.append( Item( title=config.get_localized_string(30134) , channel="channelselector" , action="listchannels" , category="NEW" , thumbnail="novedades"))
    return itemlist

def channeltypes(params,url,category):
    logger.info("channelselector.channeltypes")

    lista = getchanneltypes()
    for item in lista:
        addfolder(item.title,item.channel,item.action,category=item.category,thumbnailname=item.thumbnail)

    # Label (top-right)...
    import xbmcplugin
    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category="" )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

    if config.get_setting("forceview")=="true":
        # Confluence - Thumbnail
        import xbmc
        xbmc.executebuiltin("Container.SetViewMode(500)")

def listchannels(params,url,category):
    logger.info("channelselector.listchannels")

    lista = filterchannels(category)
    for channel in lista:
        if config.is_xbmc() and (channel.type=="xbmc" or channel.type=="generic"):
            addfolder(channel.title , channel.channel , "mainlist" , channel.channel)

        elif config.get_platform()=="boxee" and channel.extra!="rtmp":
            addfolder(channel.title , channel.channel , "mainlist" , channel.channel)

    # Label (top-right)...
    import xbmcplugin
    xbmcplugin.setPluginCategory( handle=int( sys.argv[ 1 ] ), category=category )
    xbmcplugin.addSortMethod( handle=int( sys.argv[ 1 ] ), sortMethod=xbmcplugin.SORT_METHOD_NONE )
    xbmcplugin.endOfDirectory( handle=int( sys.argv[ 1 ] ), succeeded=True )

    if config.get_setting("forceview")=="true":
        # Confluence - Thumbnail
        import xbmc
        xbmc.executebuiltin("Container.SetViewMode(500)")

def filterchannels(category):
    returnlist = []

    idiomav=""

    if category=="NEW":
        channelslist = channels_history_list()
        for channel in channelslist:
            # Pasa si no ha elegido "todos" y no está en el idioma elegido
            if channel.language<>"" and idiomav<>"" and idiomav not in channel.language:
                #logger.info(channel[0]+" no entra por idioma #"+channel[3]+"#, el usuario ha elegido #"+idiomav+"#")
                continue
            returnlist.append(channel)
    else:
        channelslist = channels_list()
    
        for channel in channelslist:
            # Pasa si no ha elegido "todos" y no está en la categoría elegida
            if category<>"*" and category not in channel.category:
                #logger.info(channel[0]+" no entra por tipo #"+channel[4]+"#, el usuario ha elegido #"+category+"#")
                continue
            # Pasa si no ha elegido "todos" y no está en el idioma elegido
            if channel.language<>"" and idiomav<>"" and idiomav not in channel.language:
                #logger.info(channel[0]+" no entra por idioma #"+channel[3]+"#, el usuario ha elegido #"+idiomav+"#")
                continue
            returnlist.append(channel)

    return returnlist

def channels_list():
    itemlist = []
    itemlist.append( Item( title="Mitele"                     , channel="mitele"               , language="ES" , category="N"   , type="generic" )) # jesus, truenon, boludiko 05/04/2012

    return itemlist

def addfolder(nombre,channelname,accion,category="",thumbnailname="",folder=True):
    #print "addfolder"
    if category == "":
        try:
            category = unicode( nombre, "utf-8" ).encode("iso-8859-1")
        except:
            pass
    
    import xbmc

    if config.get_setting("thumbnail_type")=="0":
        IMAGES_PATH = xbmc.translatePath( os.path.join( config.get_runtime_path(), 'resources' , 'images' , 'posters' ) )
    elif config.get_setting("thumbnail_type")=="1":
        IMAGES_PATH = xbmc.translatePath( os.path.join( config.get_runtime_path(), 'resources' , 'images' , 'banners' ) )
    elif config.get_setting("thumbnail_type")=="2":
        IMAGES_PATH = xbmc.translatePath( os.path.join( config.get_runtime_path(), 'resources' , 'images' , 'squares' ) )
    
    if config.get_setting("thumbnail_type")=="0":
        WEB_PATH = "http://media.tvalacarta.info/tvalacarta/posters/"
    elif config.get_setting("thumbnail_type")=="1":
        WEB_PATH = "http://media.tvalacarta.info/tvalacarta/banners/"
    elif config.get_setting("thumbnail_type")=="2":
        WEB_PATH = "http://media.tvalacarta.info/tvalacarta/squares/"

    if config.get_platform()=="boxee":
        IMAGES_PATH="http://media.tvalacarta.info/tvalacarta/posters/"

    if thumbnailname=="":
        thumbnailname = channelname

    '''
    thumbnail = os.path.join(IMAGES_PATH, "menu", thumbnailname)
    #logger.info("thumbnail="+thumbnail)
    if not os.path.exists(thumbnail):
        # Preferencia: primero JPG
        thumbnail = os.path.join(IMAGES_PATH, thumbnailname+".jpg")
    # Preferencia: segundo PNG
    if not os.path.exists(thumbnail):
        thumbnail = os.path.join(IMAGES_PATH, thumbnailname+".png")

    # Preferencia: tercero WEB
    if not os.path.exists(thumbnail):
    '''
    if thumbnailname.startswith("http://"):
        thumbnail = thumbnailname
    else:
        thumbnail = WEB_PATH+thumbnailname+".png"

    import xbmcgui
    import xbmcplugin
    #logger.info("thumbnail="+thumbnail)
    listitem = xbmcgui.ListItem( nombre , iconImage="DefaultFolder.png", thumbnailImage=thumbnail)
    itemurl = '%s?channel=%s&action=%s&category=%s' % ( sys.argv[ 0 ] , channelname , accion , category )
    xbmcplugin.addDirectoryItem( handle = int(sys.argv[ 1 ]), url = itemurl , listitem=listitem, isFolder=folder)


def get_thumbnail_path(preferred_thumb=""):

    WEB_PATH = ""
    
    if preferred_thumb=="":
        thumbnail_type = config.get_setting("thumbnail_type")
        if thumbnail_type=="":
            thumbnail_type="2"
        
        if thumbnail_type=="0":
            WEB_PATH = "http://media.tvalacarta.info/tvalacarta/posters/"
        elif thumbnail_type=="1":
            WEB_PATH = "http://media.tvalacarta.info/tvalacarta/banners/"
        elif thumbnail_type=="2":
            WEB_PATH = "http://media.tvalacarta.info/tvalacarta/squares/"
    else:
        WEB_PATH = "http://media.tvalacarta.info/tvalacarta/"+preferred_thumb+"/"

    return WEB_PATH