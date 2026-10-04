-- Pairwise record between every two players who have faced each other.
-- One row per (player_id, opponent_id) direction, so looking up "A vs B"
-- and "B vs A" both resolve directly without a self-join at query time.

with player_matches as (

    select * from {{ ref('int_player_matches') }}

),

pairwise as (

    select
        player_id,
        opponent_id,
        count(*) as matches_played,
        sum(case when won then 1 else 0 end) as wins,
        sum(case when won then 0 else 1 end) as losses,
        max(tourney_date) as last_played
    from player_matches
    group by player_id, opponent_id

)

select
    pairwise.player_id,
    player_overview.player_name,
    pairwise.opponent_id,
    opponent_overview.player_name as opponent_name,
    pairwise.matches_played,
    pairwise.wins,
    pairwise.losses,
    round(pairwise.wins / pairwise.matches_played, 4) as win_pct,
    pairwise.last_played
from pairwise
left join {{ ref('gold_player_overview') }} as player_overview
    on pairwise.player_id = player_overview.player_id
left join {{ ref('gold_player_overview') }} as opponent_overview
    on pairwise.opponent_id = opponent_overview.player_id
