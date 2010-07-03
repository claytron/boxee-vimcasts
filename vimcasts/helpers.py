import mc


def cleanse_feed():
    """Modify the feed to do two things.

    - Make sure that non video items don't show up in the UI.
    - Add the episode number to the "label"
    """
    feed_list = mc.GetWindow(14000).GetList(100)
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
