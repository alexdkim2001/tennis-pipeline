-- One row per player per match date where a ranking was recorded.
-- Feeds the ranking-over-time line chart. One player can have multiple
-- matches on the same tourney_date (rare); we keep the best (lowest) rank
-- recorded that day so the trend line has one point per date.

with player_matches as (

    select * from {{ ref('int_player_matches') }}
    where player_rank is not null

)

select
    player_id,
    player_name,
    tourney_date,
    min(player_rank) as rank,
    max(player_rank_points) as rank_points
from player_matches
group by player_id, player_name, tourney_date
