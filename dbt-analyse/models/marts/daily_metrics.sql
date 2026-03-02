with agg as (
    select
        event_date,
        country,
        platform,
        count(distinct user_id) as dau,
        sum(iap_revenue) as total_iap_revenue,
        sum(ad_revenue) as total_ad_revenue,
        sum(match_start_count) as matches_started,
        sum(match_end_count) as matches_ended,
        sum(victory_count) as total_victories,
        sum(defeat_count) as total_defeats,
        sum(server_connection_error) as total_server_errors
    from {{ ref('stg_user_daily_metrics') }}
    group by event_date, country, platform
)
select
    event_date,
    country,
    platform,
    dau,
    total_iap_revenue,
    total_ad_revenue,
    round(safe_divide(total_iap_revenue + total_ad_revenue, dau), 6) as arpdau,
    matches_started,
    round(safe_divide(matches_started, dau), 4) as match_per_dau,
    round(safe_divide(total_victories, matches_ended), 4) as win_ratio,
    round(safe_divide(total_defeats, matches_ended), 4) as defeat_ratio,
    round(safe_divide(total_server_errors, dau), 4) as server_error_per_dau
from agg
order by event_date, country, platform
