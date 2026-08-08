import os
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS
from health_engine import compute_health_scores, get_worst_n, get_router_detail

app = Flask(__name__)
CORS(app)

# Load datasets at startup
base_dir = os.path.dirname(os.path.abspath(__name__))
data_dir = os.path.join(base_dir, 'sample_data')

routers_df = pd.read_csv(os.path.join(data_dir, 'routers.csv'))
metrics_df = pd.read_csv(os.path.join(data_dir, 'metrics.csv'))
complaints_df = pd.read_csv(os.path.join(data_dir, 'COMPLA~1.CSV')) # keeping the weird filename

# Compute scores once at startup
scores_df = compute_health_scores(metrics_df, routers_df)

@app.route('/api/rankings', methods=['GET'])
def get_rankings():
    """Returns the worst N routers."""
    n = int(request.args.get('n', 10))
    worst_routers = get_worst_n(scores_df, n)
    return jsonify(worst_routers)

@app.route('/api/router/<router_id>', methods=['GET'])
def get_router(router_id):
    """Returns details for a specific router."""
    detail = get_router_detail(router_id, scores_df, metrics_df, complaints_df)
    if detail:
        return jsonify(detail)
    return jsonify({"error": "Router not found"}), 404

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Returns fleet-wide statistics."""
    total_routers = len(scores_df)
    healthy = len(scores_df[scores_df['health_score'] >= 80])
    fair = len(scores_df[(scores_df['health_score'] >= 60) & (scores_df['health_score'] < 80)])
    degraded = len(scores_df[(scores_df['health_score'] >= 40) & (scores_df['health_score'] < 60)])
    critical = len(scores_df[scores_df['health_score'] < 40])
    
    return jsonify({
        "total": total_routers,
        "healthy": healthy,
        "fair": fair,
        "degraded": degraded,
        "critical": critical,
        "average_score": round(scores_df['health_score'].mean(), 1)
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
