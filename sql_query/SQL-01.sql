-- Calculate the Number of Kills and the Number of Suicides per Player
-- and Per Match

select match_id, player_name, sum(kill_count) as kill_count,
       sum(suicide_count) as suicide_count, 0 as death_count
from (select match_id, killer_name as player_name,
      count(killer_name) as kill_count, 0 as suicide_count
      from match_frag where victim_name is not null
      group by match_id, killer_name union
      select match_id, killer_name as player_name, 0 as kill_count,
             count(killer_name) as suicide_count
      from match_frag where victim_name is null group by match_id, killer_name)
