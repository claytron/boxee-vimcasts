import mc

def play_video():
    """Play the selected video directly instead of asking the user
    if they want to play it.
    """
    player = mc.GetPlayer()
    feed_list = mc.GetWindow(14000).GetList(100)
    focused_item = feed_list.GetFocusedItem()
    shows = feed_list.GetItems()
    if player.IsPlaying():
        player.Stop()
    player.Play(shows[focused_item])
