-- Win % by surface, per player. Feeds the surface breakdown chart.
--
-- Grouped by player_id only (not name) because a player's name can vary
-- slightly across rows (e.g. accents); the canonical display name comes
-- from gold_player_overview instead.

with player_matches as (

    select * from {{ ref('int_player_matches') }}
    where surface is not null

),

by_surface as (

    select
        player_id,
        surface,
        count(*) as matches_played,
        sum(case when won then 1 else 0 end) as wins,
        sum(case when won then 0 else 1 end) as losses,
        round(sum(case when won then 1 else 0 end) / count(*), 4) as win_pct
    from player_matches
    group by player_id, surface

)

select
    by_surface.player_id,
    overview.player_name,
    by_surface.surface,
    by_surface.matches_played,
    by_surface.wins,
    by_surface.losses,
    by_surface.win_pct
from by_surface
left join {{ ref('gold_player_overview') }} as overview using (player_id)
