## Commands

### Moderator Commands

`!startbets h:mm:ss.mmm`

Starts a round of betting with an estimated run time of h:mm:ss.mmm. This should be an **over-estimate**, and is used only to scale the bonus for an early bet. Betting ends automatically after this time has elapsed.

If `!startbets` appears to not be working, submit a `!finaltime`.

`!finaltime h:mm:ss.mmm`

Ends a round of betting with a run time of h:mm:ss.mmm. The winners are displayed.

`!winners`

Displays the top 5 scorers. Score is based on accuracy and the earliness of the bet.

`!betcount`

Displays the current number of bets.

`!echo anything`

Hexbet will respond with "anything".

`!wecho anything`

Hexbet will whisper you "anything". This doesn't seem to work unless you are friends with hexbet.

### User commands

`!bet h:mm:ss.mmm`

Sets or updates a bet. The time of the bet is recorded. Betting again later will reduce the time bonus.

`!checkbet`

Hexbot will @you your current bet, and when you placed the bet.

