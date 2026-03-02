/*
    stg_user_daily_metrics
    ----------------------
    Cleans & standardizes raw data:
      - Platform → UPPERCASE
      - Null/empty country → 'UNKNOWN'
      - Deduplicates on (user_id, event_date) keeping max values
*/

with deduplicated as (

    select
        user_id,
        cast(event_date as date)       as event_date,
        cast(install_date as date)     as install_date,
        upper(trim(platform))          as platform,
        case
            when country is null or trim(country) = '' then 'UNKNOWN'
            else trim(country)
        end                            as country,
        total_session_count,
        total_session_duration,
        match_start_count,
        match_end_count,
        victory_count,
        defeat_count,
        server_connection_error,
        iap_revenue,
        ad_revenue,
        -- Handle duplicates: keep row with highest session duration per user-day
        row_number() over (
            partition by user_id, event_date
            order by total_session_duration desc
        ) as rn
    from {{ source('raw', 'user_daily_metrics') }}
    where user_id is not null
      and event_date is not null

)

select
    user_id,
    event_date,
    install_date,
    platform,
    country,
    total_session_count,
    total_session_duration,
    match_start_count,
    match_end_count,
    victory_count,
    defeat_count,
    server_connection_error,
    iap_revenue,
    ad_revenue
from deduplicated
where rn = 1
