-- Unpivots each match into two player-centric rows (winner's and loser's
-- perspective). Every downstream player stat (win %, rank history,
-- head-to-head) aggregates from this one grain, so the aggregation logic
-- doesn't have to special-case "am I the winner or loser column" more than
-- once.

with matches as (

    select * from {{ ref('stg_atp_matches') }}

),

as_winner as (

    select
        match_id,
        tourney_id,
        tourney_name,
        tourney_date,
        surface,
        round,
        best_of,
        minutes,

        winner_id as player_id,
        winner_name as player_name,
        winner_hand as player_hand,
        winner_ioc as player_ioc,
        winner_rank as player_rank,
        winner_rank_points as player_rank_points,

        loser_id as opponent_id,
        loser_name as opponent_name,

        true as won,

        w_ace as aces,
        w_df as double_faults,
        w_svpt as serve_pts,
        w_1st_in as first_serve_in,
        w_1st_won as first_serve_won,
        w_2nd_won as second_serve_won,
        w_sv_gms as serve_games,
        w_bp_saved as bp_saved,
        w_bp_faced as bp_faced

    from matches

),

as_loser as (

    select
        match_id,
        tourney_id,
        tourney_name,
        tourney_date,
        surface,
        round,
        best_of,
        minutes,

        loser_id as player_id,
        loser_name as player_name,
        loser_hand as player_hand,
        loser_ioc as player_ioc,
        loser_rank as player_rank,
        loser_rank_points as player_rank_points,

        winner_id as opponent_id,
        winner_name as opponent_name,

        false as won,

        l_ace as aces,
        l_df as double_faults,
        l_svpt as serve_pts,
        l_1st_in as first_serve_in,
        l_1st_won as first_serve_won,
        l_2nd_won as second_serve_won,
        l_sv_gms as serve_games,
        l_bp_saved as bp_saved,
        l_bp_faced as bp_faced

    from matches

)

select * from as_winner
union all
select * from as_loser
