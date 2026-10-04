-- One row per player: career record + most recent ranking.
-- This is the model the dashboard's KPI tiles and player picker read from.

with player_matches as (

    select * from {{ ref('int_player_matches') }}

),

-- a player's name/hand/ioc can vary slightly across rows (e.g. accents);
-- take the most recent match's version as the canonical display name.
latest_identity as (

    select
        player_id,
        player_name,
        player_hand,
        player_ioc
    from (
        select
            player_id,
            player_name,
            player_hand,
            player_ioc,
            row_number() over (
                partition by player_id
                order by tourney_date desc
            ) as rn
        from player_matches
    )
    where rn = 1

),

latest_ranking as (

    select
        player_id,
        current_rank,
        current_rank_points,
        rank_as_of
    from (
        select
            player_id,
            player_rank as current_rank,
            player_rank_points as current_rank_points,
            tourney_date as rank_as_of,
            row_number() over (
                partition by player_id
                order by tourney_date desc
            ) as rn
        from player_matches
        where player_rank is not null
    )
    where rn = 1

),

record as (

    select
        player_id,
        count(*) as matches_played,
        sum(case when won then 1 else 0 end) as wins,
        sum(case when won then 0 else 1 end) as losses,
        min(tourney_date) as first_match_date,
        max(tourney_date) as last_match_date
    from player_matches
    group by player_id

)

select
    record.player_id,
    latest_identity.player_name,
    latest_identity.player_hand,
    latest_identity.player_ioc,
    record.matches_played,
    record.wins,
    record.losses,
    round(record.wins / record.matches_played, 4) as win_pct,
    latest_ranking.current_rank,
    latest_ranking.current_rank_points,
    latest_ranking.rank_as_of,
    record.first_match_date,
    record.last_match_date
from record
left join latest_identity using (player_id)
left join latest_ranking using (player_id)
