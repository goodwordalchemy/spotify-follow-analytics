# In Search Of Songs You Love: The Current State Of My Spotify Analytics Project

I want to make a music discovery tool that helps you find songs that you *love* not just songs that you like.  In my quest for that tool, I decided to rely on the fact that I generally discovery my favorite music through my friends--not through musical similarity to songs that I already listen to.  I went with this path, because I don't have a prototypical type of music that I like.  I like some music from many different genres.  I'm not sure how to pinpoint the features of music that tend to make me like it.  One thing I do know though, is that if a lot of people who's musical opinions I trust are listening to a track, it's worth at least giving it a listen myself.

In order to make an algorithm that replicates this process, you really need three ingredients.
1. You need to know what kind of music you like.  What is the input to this algorithm?
2. You have to know what your friends are listening to.
3. You have to know which of your friends are the best authorities on music.

Since I have been a user of spotify since they first came out in America, and since they have pretty good programming interface for looking up information about songs, (which I've used in a different attempt at a music recommendation algorithm), I decided to try to base my algorithm on spotify data.  

The problem is that, while spotify provides a programming interface that lets you look up all kinds of information about a user and about a user's playlists and saved songs (once that user has given you permission), they do not provide any interface to the "social graph"--that is, there is no easy way to find out who a user "follows."  In order to get that data, I wrote a program that visits the [online spotify web player](play.spotify.com) and performs the following algorithm:

```
1. Store all desired listening/playlists data for a user (call that user "user0").
2. Visit the "following" tab for user0.
4. For each user that user0 follows, store a link between those two users.
5. Add the user id of each user that user0 follows to a queue.
6. For each user in the queue, perform steps 1-4.
7. Stop adding users to the queue once they have a specified distance (i.e. number of links from) user0.  In my case, I did not collect any users that were further than 2 links away from the first user, because it would have taken thousands of years or hundreds of dollars in order to deal with that much data.
```

Once I had the social graph stored, the next step was to specify the criteria by which I would say that a user "likes" a track.  I ultimately decided to use a pretty poor indicator: if a track appears in one of the user's "public playlists," then they like it.  The reason this is not a great metric is that there's no way to know why somebody put a song on a public playlist.  It could be a playlist of songs that they hate, for example, or a playlist of songs that they've generated using a crappy music recommendation algorithm.  It would be much better to know the top tracks that a user listens to.  That is going to be the goal of a future project.  I decided to go with public playlists because you don't need any permissions to see those public playlists, so the logistics of gathering that data are much easier.  (To get private playlists or user listening data, I would have to build an entire website and then convince all of my friends to log into it.)

The final question for this iteration of my music recommendation algorithm is, given the data set acquired above, how do I get a machine to make recommendations?  The algorithm should basically look at what people are listening to, look at what you listen to, and find the set of songs that cooccur most often with songs that you don't listen to in the libraries of your friends.  In a later version of this algorithm, I will take into account the "authority" of recommendations by different users in the network, but for this simple implementation I did not bother.

The recommendation algorithm used a strategy called "bipartite projection."  A network where there are two types of entities (in this case, "users" and "tracks") and the only links in the network are between entities of different types is called a "bipartite graph".  The idea of bipartite projection is to compress the link infomation of the whole network onto one of the sets of entities.  In this case, I projected the network on to the track set by making a stronger link between tracks if they are liked by many users and a weaker link if they do not have a lot of listeners in commeon.

The algorithm:

```
For every track: 
	For every other track in the network: 
		for every user in the network: 
			If the user likes both track i and track j, the score for the track increases in inverse proportion to the amount of tracks that a user likes.  So if a user doesn't like very many tracks, his vote is worth slightly more than somebody who likes a lot of tracks.  
```

What this calculation ultimately creates is a matrix where each entry tells you, "if every track starts with some amount of 'recommendation capacity', the entry in the matrix tells you the fraction of that capacity to be allocated to the other track.  In order to take into account a users's authority, I will modify the recommendation capacity, but for this implementation, I simply set it to 1 for everybody.

The similarity matrix allows you to generate a ranked list of recommended tracks based on a list of tracks passed into the funtion.  To make a recommendation based on a list of tracks,

```
For each track, l, in your list of tracks: 
	Initialize a score of 0.
	For each other track: 
		Increase the score by the sum of recommendation capacity allocated from each track in the overal network by looking up the coordinates of both tracks in the similarity matrix.  
Return the top n tracks with the highest scores.
```

In my initial test, this algorithm works pretty well, but it's a little slow.  You can't build the whole matrix in memory using the algorithm that I implemented.  The recommendations are good though.  The character of the tracks is pretty well preserved.  A list of rock songs will yield mostly rock.  A list of rap songs will return a bunch of mostly rap. The songs that are recommended are new.
The next thing I would like to do is run this algorithm based on top 100 songs for each user.  Spotify created a "Top 100 songs of 2016" for every user, but in order to get those songs, I will have to make a website and convince people to let me scrape their spotify libraries.