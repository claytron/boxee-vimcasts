import mc


def cleanse_feed():
    """Remove items from the feed that are not videos
    """
    feed_list = mc.GetWindow(14000).GetList(9000)
    keepers = mc.ListItems()
    for episode in feed_list.GetItems():
        video_base = "http://media.vimcasts.org/videos/"
        ep_path = episode.GetPath()
        if ep_path.startswith(video_base):
            keepers.append(episode)
        else:
            mc.LogDebug("vimcasts removing non video item: %s" % ep_path)
    # reset the list to only the items that contained a video
    feed_list.SetItems(keepers)
