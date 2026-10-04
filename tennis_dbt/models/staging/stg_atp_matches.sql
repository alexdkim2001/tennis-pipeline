-- Bronze -> silver: type casting + dedup.
--
-- Column names below follow the standard Sackmann/TML ATP matches schema.
-- Bronze stores everything as strings, so this is the first place anything
-- gets a real type. If `dbt run` fails on an unknown column, check
-- `describe workspace.tennis_bronze.atp_matches` and adjust the casts below
-- to match what's actually there.
--
-- match_id handles the known data issue: 489 rows (Aug 2025+) have a null
-- match_num, so those rows get a deterministic hash key instead of
-- tourney_id + match_num.
--
-- Dedup handles the other known issue: 10 duplicate matches in the source.
-- We keep the most recently ingested copy of each match_id.

with source as (

    select * from {{ source('bronze', 'atp_matches') }}

),

renamed as (

    select
        tourney_id,
        tourney_name,
        surface,
        cast(draw_size as int) as draw_size,
        tourney_level,
        to_date(tourney_date, 'yyyyMMdd') as tourney_date,
        match_num,

        cast(winner_id as int) as winner_id,
        winner_seed,
        winner_entry,
        winner_name,
        winner_hand,
        cast(winner_ht as int) as winner_ht,
        winner_ioc,
        cast(winner_age as double) as winner_age,
        cast(winner_rank as int) as winner_rank,
        cast(winner_rank_points as int) as winner_rank_points,

        cast(loser_id as int) as loser_id,
        loser_seed,
        loser_entry,
        loser_name,
        loser_hand,
        cast(loser_ht as int) as loser_ht,
        loser_ioc,
        cast(loser_age as double) as loser_age,
        cast(loser_rank as int) as loser_rank,
        cast(loser_rank_points as int) as loser_rank_points,

        score,
        cast(best_of as int) as best_of,
        round,
        cast(minutes as int) as minutes,

        cast(w_ace as int) as w_ace,
        cast(w_df as int) as w_df,
        cast(w_svpt as int) as w_svpt,
        cast(w_1stIn as int) as w_1st_in,
        cast(w_1stWon as int) as w_1st_won,
        cast(w_2ndWon as int) as w_2nd_won,
        cast(w_SvGms as int) as w_sv_gms,
        cast(w_bpSaved as int) as w_bp_saved,
        cast(w_bpFaced as int) as w_bp_faced,

        cast(l_ace as int) as l_ace,
        cast(l_df as int) as l_df,
        cast(l_svpt as int) as l_svpt,
        cast(l_1stIn as int) as l_1st_in,
        cast(l_1stWon as int) as l_1st_won,
        cast(l_2ndWon as int) as l_2nd_won,
        cast(l_SvGms as int) as l_sv_gms,
        cast(l_bpSaved as int) as l_bp_saved,
        cast(l_bpFaced as int) as l_bp_faced,

        _source_file,
        _ingested_at

    from source

),

with_match_id as (

    select
        *,
        case
            when match_num is not null and trim(match_num) != ''
                then concat(tourney_id, '-', trim(match_num))
            else md5(concat(
                tourney_id, '|', round, '|',
                cast(winner_id as string), '|', cast(loser_id as string)
            ))
        end as match_id
    from renamed

),

ranked as (

    select
        *,
        row_number() over (
            partition by match_id
            order by _ingested_at desc
        ) as rn
    from with_match_id

)

select
    match_id,
    tourney_id,
    tourney_name,
    surface,
    draw_size,
    tourney_level,
    tourney_date,
    match_num,

    winner_id,
    winner_seed,
    winner_entry,
    winner_name,
    winner_hand,
    winner_ht,
    winner_ioc,
    winner_age,
    winner_rank,
    winner_rank_points,

    loser_id,
    loser_seed,
    loser_entry,
    loser_name,
    loser_hand,
    loser_ht,
    loser_ioc,
    loser_age,
    loser_rank,
    loser_rank_points,

    score,
    best_of,
    round,
    minutes,

    w_ace,
    w_df,
    w_svpt,
    w_1st_in,
    w_1st_won,
    w_2nd_won,
    w_sv_gms,
    w_bp_saved,
    w_bp_faced,

    l_ace,
    l_df,
    l_svpt,
    l_1st_in,
    l_1st_won,
    l_2nd_won,
    l_sv_gms,
    l_bp_saved,
    l_bp_faced,

    _source_file,
    _ingested_at
from ranked
where rn = 1
