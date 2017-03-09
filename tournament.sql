-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

create table players (player_id serial primary key, player_name text not null);
create table tournament (tour_id serial primary key, tour_name text not null);
create table match_code (code integer primary key, code_name text not null);
create table match_pair (tour_id integer not null references tournament(tour_id), match_id serial primary key, player1 integer not null references players(player_id), player2 integer not null references players(player_id));
create table matches (tour_id integer references tournament(tour_id), match_id integer references match_pair(match_id), player integer references players(player_id), result integer not null references match_code(code), primary key(tour_id, match_id, player));



