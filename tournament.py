#!/usr/bin/env python
#
# tournament.py -- implementation of a Swiss-system tournament
#

import psycopg2
from operator import itemgetter


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    return psycopg2.connect("dbname=tournament")


def deleteMatches():
    """Remove all the match records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("delete from matches;")
    c.execute("delete from match_pair;")
    conn.commit()
    conn.close()


def deletePlayers():
    """Remove all the player records from the database."""
    conn = connect()
    c = conn.cursor()
    c.execute("delete from players;")
    conn.commit()
    conn.close()


def countPlayers():
    """Returns the number of players currently registered."""
    conn = connect()
    c = conn.cursor()
    c.execute("select count(*) from players;")
    player_count = c.fetchone()
    conn.close()
    return player_count[0]


def registerPlayer(name):
    """Adds a player to the tournament database.

    The database assigns a unique serial id number for the player.  (This
    should be handled by your SQL database schema, not in your Python code.)

    Args:
      name: the player's full name (need not be unique).
    """
    conn = connect()
    c = conn.cursor()
    c.execute("insert into players (player_name) values (%s);", (name,))
    conn.commit()
    conn.close()


def playerStandings():
    """Returns a list of the players and their win records, sorted by wins.

    The first entry in the list should be the player in first place, or a
    playertied for first place if there is currently a tie.

    Returns:
      A list of tuples, each of which contains (id, name, wins, matches):
        id: the player's unique id (assigned by the database)
        name: the player's full name (as registered)
        wins: the number of matches the player has won
        matches: the number of matches the player has played
    """
    conn = connect()
    c = conn.cursor()
    c.execute("""select player_id, player_name, coalesce(wins, 0),
                 coalesce(total,0) from players left join (
                 select player, count(player) as total from matches
                 group by player) t on player_id = t.player left join(
                 select player, count(player) as wins from matches where
                 result = 1 group by player) w on player_id = w.player
                 order by wins desc;""")
    standings = c.fetchall()
    conn.close()
    return standings


def reportMatch(winner, loser):
    """Records the outcome of a single match between two players.

    Args:
      winner:  the id number of the player who won
      loser:  the id number of the player who lost
    """
    conn = connect()
    c = conn.cursor()
    c.execute("""insert into match_pair (tour_id, player1, player2) values
                (1, %s, %s) returning match_id""", (winner, loser))
    match_id = c.fetchone()[0]
    c.execute("""insert into matches (tour_id, match_id, player, result)
                values (1, %s, %s, 1), (1, %s, %s, 0)""", (
        match_id, winner, match_id, loser))
    conn.commit()
    conn.close()


def swissPairings():
    """Returns a list of pairs of players for the next round of a match.

    Assuming that there are an even number of players registered, each
    player appears exactly once in the pairings.  Each player is paired
    with another player with an equal or nearly-equal win record, that
    is, a player adjacent to him or her in the standings.

    Returns:
      A list of tuples, each of which contains (id1, name1, id2, name2)
        id1: the first player's unique id
        name1: the first player's name
        id2: the second player's unique id
        name2: the second player's name
    """
    conn = connect()
    c = conn.cursor()
    c.execute("""select player_id, player_name, coalesce(sum, 0) as sum
                 from players left join (select player, sum(result) as
                 sum from matches group by player) as s
                 on player = player_id""")
    players_info = c.fetchall()
    c.execute("""select player1, player2 from match_pair where tour_id = 1""")
    existing_pairs = c.fetchall()
    players_info.sort(key=itemgetter(2))
    final_pairs = []
    for i in range(len(players_info)/2):
        player1 = players_info.pop(0)
        player1_id = player1[0]
        for i in range(len(players_info)/2):
            player2 = players_info[0]
            player2_id = player2[0]
            if (player1_id, player2_id) in existing_pairs or (
                    player2_id, player1_id) in existing_pairs:
                pass
            else:
                players_info.remove(player2)
        final_pairs.append((player1[0], player1[1], player2[0], player2[1]))
    conn.close()
    return final_pairs
