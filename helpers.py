import mc

def play_video():
    """Play the selected video directly instead of asking the user
    if they want to play it.
    """
    player = mc.GetPlayer()
    feed_list = mc.GetWindow(14000).GetList(100)
    focused_item = feed_list.GetFocusedItem()
    episodes = feed_list.GetItems()
    if player.IsPlaying():
        player.Stop()
    player.Play(episodes[focused_item])


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
        ep_title = episode.GetLabel()
        if ep_path.startswith(video_base):
            ep_number = ep_path.split("/")[4]
            episode.SetLabel("#%s - %s" % (ep_number, ep_title))
            keepers.append(episode)
        else:
            mc.LogDebug("vimcasts removing non video item: %s" % ep_path)
    # reset the list to only the items that contained a video
    feed_list.SetItems(keepers)
