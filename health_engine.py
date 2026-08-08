import pandas as pd

def compute_health_scores(metrics_df, routers_df):
    """
    Computes a composite health score for each router.
    """
    # Calculate average metrics per router over all 24 hours
    avg_metrics = metrics_df.groupby('router_id').agg({
        'avg_speed_mbps': 'mean',
        'latency_ms': 'mean',
        'packet_loss_pct': 'mean',
        'disconnects': 'mean',
        'signal_dbm': 'mean'
    }).reset_index()

    scores = []
    
    for _, row in avg_metrics.iterrows():
        router_id = row['router_id']
        
        # 1. Speed Score (30%) - capped at 80 Mbps
        speed = row['avg_speed_mbps']
        speed_score = min(speed / 80.0, 1.0) * 100

        # 2. Latency Score (25%) - drops to 0 at 300ms
        latency = row['latency_ms']
        latency_score = max(0.0, (1.0 - latency / 300.0)) * 100

        # 3. Packet Loss Score (20%) - drops to 0 at 10%
        loss = row['packet_loss_pct']
        loss_score = max(0.0, (1.0 - loss / 10.0)) * 100

        # 4. Disconnects Score (15%) - drops to 0 at 15 disconnects
        disconnects = row['disconnects']
        disconnects_score = max(0.0, (1.0 - disconnects / 15.0)) * 100

        # 5. Signal Score (10%) - scales between -90dBm and -40dBm
        signal = row['signal_dbm']
        signal_score = min(max(0.0, (signal + 90) / 50.0), 1.0) * 100

        # Weighted final score
        final_score = (speed_score * 0.30) + (latency_score * 0.25) + \
                      (loss_score * 0.20) + (disconnects_score * 0.15) + \
                      (signal_score * 0.10)
                      
        scores.append({
            'router_id': router_id,
            'health_score': round(final_score, 1),
            'speed_score': round(speed_score, 1),
            'latency_score': round(latency_score, 1),
            'loss_score': round(loss_score, 1),
            'disconnects_score': round(disconnects_score, 1),
            'signal_score': round(signal_score, 1)
        })

    scores_df = pd.DataFrame(scores)
    
    # Merge with routers metadata to get building, model, etc.
    final_df = pd.merge(scores_df, routers_df, on='router_id', how='left')
    return final_df

def get_worst_n(scores_df, n=10):
    """
    Returns the top N worst performing routers based on health score.
    """
    worst_routers = scores_df.sort_values('health_score', ascending=True).head(n)
    # determine status based on score
    def get_status(score):
        if score >= 80: return 'Healthy'
        elif score >= 60: return 'Fair'
        elif score >= 40: return 'Degraded'
        else: return 'Critical'
        
    worst_routers['status'] = worst_routers['health_score'].apply(get_status)
    return worst_routers.to_dict(orient='records')

def get_router_detail(router_id, scores_df, metrics_df, complaints_df):
    """
    Returns detailed information for a specific router.
    """
    router_info = scores_df[scores_df['router_id'] == router_id]
    if router_info.empty:
        return None
        
    router_info = router_info.iloc[0].to_dict()
    
    # Determine status
    score = router_info['health_score']
    if score >= 80: router_info['status'] = 'Healthy'
    elif score >= 60: router_info['status'] = 'Fair'
    elif score >= 40: router_info['status'] = 'Degraded'
    else: router_info['status'] = 'Critical'

    # Get hourly metrics
    hourly_metrics = metrics_df[metrics_df['router_id'] == router_id].sort_values('hour')
    router_info['metrics'] = hourly_metrics.to_dict(orient='records')
    
    # Get complaints
    complaints = complaints_df[complaints_df['router_id'] == router_id].sort_values('date', ascending=False)
    router_info['complaints'] = complaints.to_dict(orient='records')
    
    return router_info
